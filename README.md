# ultimmc-portable

Instalador **sin sudo** de [UltimMC](https://ultimmc.com/) + Minecraft **1.21.8** para Ubuntu 22.04 u otros sistemas con GLIBC ≤ 2.37 y Java 21. Todo se instala en `~/minecraft`.

**No hay ningún usuario ni perfil preconfigurado**: cada persona elige su propio nombre de jugador la primera vez que abre el launcher.

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
| `JAVA_PATH` | `/usr/bin/java` | Java 21 (o superior compatible). |
| `MC_ASSETS_REPO` | el repo del que clonaste (`origin`) | Repo cuyo workflow baja los assets; cámbialo si haces fork. |
| `SKIP_ASSETS` | `0` | `1` para no descargar los 442 MB de assets. |
| `MC_LAUNCH` | `0` | `1` para abrir el juego al terminar. |

Ejemplo:

```bash
MC_LAUNCH=1 bash install.sh
```

## Crear tu cuenta local (primer arranque)

El instalador **no crea ninguna cuenta**. Haz esto una vez, después de instalar:

1. Abre el launcher: `~/minecraft/bin/ultimmc` (o el acceso “UltimMC”).
2. En la barra superior pulsa **Profiles** → **Manage Accounts** (*Gestionar cuentas*).
3. En la página de cuentas pulsa **Add Local** (*Añadir local*).
4. Escribe el nombre con el que quieres jugar y confirma con **OK**.
5. Cierra el launcher. Ya puedes usar **“Jugar Minecraft 1.21.8”** o pulsar **Launch** en el launcher.

Es una cuenta *Local*: no pide contraseña, no usa Microsoft/Mojang y sirve para jugar en solitario. Tu mundo y tu inventario quedan asociados a ese nombre, así que elige uno que te guste: cambiarlo después crea un personaje distinto. Si el launcher pregunta por una cuenta al lanzar, vuelve al paso 2 y añade una.

## Requisitos

- `bash`, `curl`, `python3`.
- Java 21 instalado (el juego se lanza con `/usr/bin/java` por defecto).
- `gh` autenticado **solo si** la red bloquea `resources.download.minecraft.net`: `gh auth login`.
- Sin sudo: todos los archivos se crean en el HOME del usuario.

## Compartir / instalar en otra red

El repo es público. Si en tu red los assets se descargan directamente, no necesitas GitHub ni `gh`. Si están bloqueados (como en el centro donde se creó), haz **fork** de este repo, clona tu fork y, si hace falta, indica tu repo con:

```bash
gh auth login
MC_ASSETS_REPO=tu-usuario/ultimmc-portable bash install.sh
```

El workflow `fetch-assets.yml` se ejecuta en tu fork y los artefactos se bajan a tu ordenador.

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
- El nombre de jugador lo elige cada persona en el launcher; no viene del usuario del sistema ni de este repo.

## Reinstalación / actualización

Volver a ejecutar `install.sh` sobre la misma carpeta conserva `accounts.json`, `ultimmc.cfg` y la instancia; actualiza el launcher y los scripts. Para reponer solo los archivos del juego:

```bash
~/minecraft/bin/seed-game-files.py
~/minecraft/bin/seed-assets.py
```
