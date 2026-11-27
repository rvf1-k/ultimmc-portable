# ultimmc-portable

Instalador **sin sudo** de [UltimMC](https://ultimmc.com/) + Minecraft **1.21.8** para Ubuntu 22.04 u otros sistema con GLIBC ≤ 2.37 y Java 21. Todo se instala en `~/minecraft`.

## Uso rápido

```bash
git clone https://github.com/rvf1-k/ultimmc-portable.git
cd ultimmc-portable
bash install.sh
```

Al terminar:

- `~/minecraft/bin/jugar-minecraft` → abre Minecraft directamente en modo offline.
- `~/minecraft/bin/ultimmc` → abre el launcher.
- En el menú Aplicaciones aparecen **“Jugar Minecraft 1.21.8”** y **“UltimMC”**.

Variables opcionales:

| Variable | Por defecto | Uso |
|---|---|---|
| `MC_HOME` | `~/minecraft` | Destino de la instalación. |
| `MC_USERNAME` | `RafMorriq` | Nombre de la cuenta local/offline. |
| `JAVA_PATH` | `/usr/bin/java` | Java 21 (o superior compatible). |
| `MC_ASSETS_REPO` | `rvf1-k/ultimmc-portable` | Repo cuyo workflow baja los assets. |
| `SKIP_ASSETS` | `0` | `1` para no descargar los 442 MB de assets. |
| `MC_LAUNCH` | `0` | `1` para abrir el juego al terminar. |

Ejemplo:

```bash
MC_USERNAME=Rafa MC_LAUNCH=1 bash install.sh
```

## Requisitos

- `bash`, `curl`, `python3`.
- Java 21 instalado (el juego se lanza con `/usr/bin/java` por defecto).
- `gh` autenticado **solo si** la red bloquea `resources.download.minecraft.net`: `gh auth login`.
- Sin sudo: todos los archivos se crean en el HOME del usuario.

## Qué contiene el repo

```
install.sh                         # instalador principal
payload/UltimMC/                   # launcher oficial + jars (binario del artifact de GitHub Actions)
payload/glibc/                     # glibc portable 2.39 (el binario pide GLIBC_2.38)
scripts/seed-game-files.py         # meta, client.jar, 113 librerías y asset index
scripts/seed-assets.py             # assets: descarga directa o vía GitHub Actions
scripts/fetch-assets.py            # se ejecuta dentro del workflow
.github/workflows/fetch-assets.yml # descarga los 4273 assets y sube 2 artefactos
templates/                         # ultimmc.cfg, .desktop y README para ~/minecraft
```

## Por qué hay un workflow

En redes con filtrado (como el centro educativo donde se creó) están bloqueados:

- `archive.org` (el enlace “DOWNLOAD NOW” del sitio oficial),
- `nightly.link`, `meta.multimc.org`,
- `authserver.mojang.com` / `sessionserver.mojang.com`,
- `resources.download.minecraft.net` (assets).

El launcher se tomó del artifact oficial de `UltimMC/Launcher` en GitHub Actions y se empaqueta en `payload/`. El meta se lee de `raw.githubusercontent.com`. Los assets se bajan con un workflow de GitHub, que sí puede acceder a Mojang, y se traen como artefactos con `gh run download`.

## Limitaciones

- Cuenta **Local**: se juega offline/en solitario. No funcionan skins de Microsoft ni servidores con `online-mode=true`.
- El idioma del juego queda en inglés (`-Duser.language=en`); el launcher sí se configura en `es_ES`.
- Si usas otro nombre de usuario, cambia `MC_USERNAME` en la instalación. No cambies el UUID generado a mano: se deriva de `OfflinePlayer:<nombre>`.

## Reinstalación / actualización

Volver a ejecutar `install.sh` sobre la misma carpeta conserva `accounts.json`, `ultimmc.cfg` y la instancia; actualiza el launcher y los scripts. Para reponer solo los archivos del juego:

```bash
~/minecraft/bin/seed-game-files.py
~/minecraft/bin/seed-assets.py
```
