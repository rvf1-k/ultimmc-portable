#!/usr/bin/env bash
# Instala UltimMC + Minecraft 1.21.8 en ~/minecraft sin sudo.
# Uso: bash install.sh
# Variables opcionales: MC_HOME, JAVA_PATH, MC_ASSETS_REPO, SKIP_ASSETS=1, MC_LAUNCH=1
set -euo pipefail

MC_HOME="${MC_HOME:-$HOME/minecraft}"
SRC="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
JAVA_PATH="${JAVA_PATH:-/usr/bin/java}"
# Por defecto, el repo del que se clonó este instalador (útil si haces fork).
DETECTED_REPO="$(git -C "$SRC" remote get-url origin 2>/dev/null | sed -n 's|.*github\.com[:/]\([^/]*/[^/.]*\)\(\.git\)\?$|\1|p')"
ASSETS_REPO="${MC_ASSETS_REPO:-${DETECTED_REPO:-rvf1-k/ultimmc-portable}}"
MC_VERSION="1.21.8"

say() { printf '\033[1;32m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33mAVISO:\033[0m %s\n' "$*" >&2; }

for cmd in curl python3; do
    command -v "$cmd" >/dev/null 2>&1 || { echo "Falta $cmd" >&2; exit 1; }
done
[ -x "$JAVA_PATH" ] || warn "No encontré Java en $JAVA_PATH (se necesita Java 21)"

say "Instalando en $MC_HOME"
mkdir -p "$MC_HOME"/{bin,logs,icons,instances} \
         "$MC_HOME/data"/{meta/net.minecraft,assets/indexes,assets/objects,assets/virtual,injectors,instances}

# ---------------------------------------------------------------- launcher
say "Copiando launcher y glibc portable"
cp -a "$SRC/payload/UltimMC" "$MC_HOME/"
cp -a "$SRC/payload/glibc" "$MC_HOME/"

cat > "$MC_HOME/bin/ultimmc" <<EOF
#!/bin/bash
# Arranca UltimMC con el glibc portable (Ubuntu 22.04 tiene GLIBC 2.35).
set -e
MC_HOME="$MC_HOME"
GLIBC="\$MC_HOME/glibc/usr/lib/x86_64-linux-gnu"
LAUNCHER_DIR="\$MC_HOME/UltimMC"
LOADER="\$LAUNCHER_DIR/bin/ld-linux-x86-64.so.2"
[ -x "\$LOADER" ] || { echo "Falta el launcher en \$MC_HOME" >&2; exit 1; }
mkdir -p "\$MC_HOME/data" "\$MC_HOME/logs" "\$MC_HOME/instances"
unset QT_PLUGIN_PATH QT_QPA_PLATFORMTHEME
export QT_QPA_PLATFORM="\${QT_QPA_PLATFORM:-xcb}"
export LD_LIBRARY_PATH="\$GLIBC:/usr/lib/x86_64-linux-gnu:\$LAUNCHER_DIR/bin\${LD_LIBRARY_PATH:+:\$LD_LIBRARY_PATH}"
export JAVA_HOME="\${JAVA_HOME:-/usr/lib/jvm/java-21-openjdk-amd64}"
exec "\$LOADER" --library-path "\$LD_LIBRARY_PATH" \\
    "\$LAUNCHER_DIR/bin/UltimMC" -d "\$MC_HOME/data" "\$@"
EOF

cat > "$MC_HOME/bin/jugar-minecraft" <<EOF
#!/bin/bash
# Arranca Minecraft $MC_VERSION directamente en modo offline.
set -e
exec "$MC_HOME/bin/ultimmc" --launch "Minecraft $MC_VERSION" --offline "\$@"
EOF

cat > "$MC_HOME/bin/ultimmc-debug" <<EOF
#!/bin/bash
bash -x "$MC_HOME/bin/ultimmc" "\$@"
EOF

install -m 0755 "$SRC/scripts/seed-game-files.py" "$MC_HOME/bin/seed-game-files.py"
install -m 0755 "$SRC/scripts/seed-assets.py" "$MC_HOME/bin/seed-assets.py"
chmod +x "$MC_HOME/bin/ultimmc" "$MC_HOME/bin/jugar-minecraft" "$MC_HOME/bin/ultimmc-debug"

# ------------------------------------------------------------ configuración
if [ ! -f "$MC_HOME/data/ultimmc.cfg" ]; then
    say "Escribiendo ultimmc.cfg"
    sed -e "s|__HOSTNAME__|$(hostname)|g" \
        -e "s|^JavaPath=.*|JavaPath=$JAVA_PATH|" \
        "$SRC/templates/ultimmc.cfg" > "$MC_HOME/data/ultimmc.cfg"
fi

# No se crea ninguna cuenta: cada persona elige su nombre al abrir el launcher.
# Instrucciones en README.md (apartado "Crear tu cuenta local").
printf '%s\n' "$ASSETS_REPO" > "$MC_HOME/data/assets-repo"

INST="$MC_HOME/data/instances/Minecraft $MC_VERSION"
mkdir -p "$INST/.minecraft"/{mods,saves,resourcepacks,logs,crash-reports}
install -m 0644 "$SRC/templates/icon.png" "$INST/.minecraft/icon.png"
if [ ! -f "$INST/instance.cfg" ]; then
    cat > "$INST/instance.cfg" <<EOF
InstanceType=OneSix
iconKey=default
MCLaunchMethod=LauncherPart
name=Minecraft $MC_VERSION
EOF
fi
if [ ! -f "$INST/mmc-pack.json" ]; then
    cat > "$INST/mmc-pack.json" <<EOF
{
    "components": [
        {"important": true, "uid": "net.minecraft", "version": "$MC_VERSION"}
    ],
    "formatVersion": 1
}
EOF
fi

# ------------------------------------------------------- authlib-injector
if [ ! -f "$MC_HOME/data/injectors/version.json" ]; then
    say "Descargando authlib-injector"
    python3 - "$MC_HOME/data/injectors" <<'PY'
import json, os, sys, urllib.request

dest = sys.argv[1]
latest = json.load(urllib.request.urlopen(
    "https://authlib-injector.yushi.moe/artifact/latest.json", timeout=30))
url = latest["download_url"]
filename = os.path.basename(url)
req = urllib.request.Request(url, headers={"User-Agent": "ultimmc-portable/1.0"})
with urllib.request.urlopen(req, timeout=60) as r, open(os.path.join(dest, filename), "wb") as out:
    out.write(r.read())
latest["download_url"] = filename       # modo offline: no descarga nada
with open(os.path.join(dest, "version.json"), "w", encoding="utf-8") as f:
    json.dump(latest, f, indent=2)
print("authlib-injector", latest["version"])
PY
fi

# ----------------------------------------------- JAR, librerías, meta, index
say "Descargando JAR, librerías, meta e index de assets"
python3 "$MC_HOME/bin/seed-game-files.py"

# ------------------------------------------------------------------ assets
if [ "${SKIP_ASSETS:-0}" = "1" ]; then
    warn "SKIP_ASSETS=1: los assets no se descargaron; el juego no arrancará sin ellos"
else
    say "Descargando y verificando assets"
    MC_HOME="$MC_HOME" MC_ASSETS_REPO="$ASSETS_REPO" python3 "$MC_HOME/bin/seed-assets.py"
fi

# ------------------------------------------------------------ accesos directos
say "Instalando accesos directos"
mkdir -p "$HOME/.local/share/applications"
for f in ultimmc.desktop jugar-minecraft.desktop; do
    sed "s|__MC_HOME__|$MC_HOME|g" "$SRC/templates/$f" > "$MC_HOME/$f"
    chmod +x "$MC_HOME/$f"
    ln -sf "$MC_HOME/$f" "$HOME/.local/share/applications/$f"
done
if [ ! -f "$MC_HOME/README.md" ]; then
    cp "$SRC/templates/README-local.md" "$MC_HOME/README.md"
fi

say "Listo"
echo "  Jugar:      $MC_HOME/bin/jugar-minecraft"
echo "  Launcher:   $MC_HOME/bin/ultimmc"
echo "  Documentos: $MC_HOME/README.md"
echo
echo "  PRIMER ARRANQUE: abre el launcher y crea tu cuenta Local (Add Local)."
echo "  No hay cuenta ni nombre preconfigurado. Ver README.md."
if [ "${MC_LAUNCH:-0}" = "1" ]; then
    exec "$MC_HOME/bin/jugar-minecraft"
fi
