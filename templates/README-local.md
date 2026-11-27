# UltimMC + Minecraft en `~/minecraft`

Instalación lista para jugar **sin sudo**. Todo (launcher, datos, juegos, logs) está dentro de `~/minecraft`.

## Cómo jugar

- **Menú Aplicaciones → "Jugar Minecraft 1.21.8"**: abre el juego directamente en modo offline.
- **Menú Aplicaciones → "UltimMC"**: abre el launcher para gestionar instancias, cuentas, mods, etc.
- Desde terminal:
  - `~/minecraft/bin/jugar-minecraft` → iniciar la partida directamente.
  - `~/minecraft/bin/ultimmc` → abrir el launcher.

En el launcher, selecciona **Minecraft 1.21.8** y pulsa el botón de **Launch** (o el de launch offline). La cuenta local se llama **RafMorriq**.

## Qué hay instalado

| Ruta | Contenido |
|---|---|
| `~/minecraft/bin/ultimmc` | Script que arranca UltimMC con el glibc portable (no necesita sudo). |
| `~/minecraft/bin/jugar-minecraft` | Atajo que arranca Minecraft 1.21.8 en modo offline. |
| `~/minecraft/bin/seed-game-files.py` | Vuelve a descargar/verificar JAR, librerías y asset index si faltan. |
| `~/minecraft/bin/seed-assets.py` | Vuelve a descargar y verificar los 4273 assets (usa GitHub Actions si la red bloquea Mojang). |
| `~/minecraft/UltimMC/` | Launcher oficial (build de GitHub Actions) + glibc portable en `glibc/`. |
| `~/minecraft/data/` | Configuración, cuenta, meta, librerías, assets e instancias del juego. |
| `~/minecraft/data/instances/Minecraft 1.21.8/` | Instancia de Minecraft 1.21.8 (Java 21). |
| `~/minecraft/logs/` | Logs del launcher y del juego. |
| `~/.local/share/applications/` | Enlaces a los dos `.desktop` (los archivos originales están en `~/minecraft`). |

## Detalles de la configuración

- **Cuenta:** `Local` (offline) con nombre `RafMorriq`. No usa Microsoft/Mojang, no pide contraseña y sirve para jugar en solitario. El autenticador local se implementa con `authlib-injector 1.2.8`, guardado en `~/minecraft/data/injectors/`.
- **Memoria:** mínimo 1024 MB, máximo 4096 MB.
- **Java:** `/usr/bin/java` (OpenJDK 21,compatible con Minecraft 1.21.8).
- **Idioma del launcher:** español (`es_ES`); el juego se ejecuta con `-Duser.language=en` porque el pack de idioma español no está incluido en el index de assets usado.
- **Archivos del juego:** client.jar, 113 librerías y los 4273 objetos de assets (incluidos sonidos) están descargados y verificados por SHA-1. El launcher funciona en modo offline y no necesita descargar nada al arrancar.

## Limitaciones de la red de este centro

El proxy bloquea `archive.org` (de donde el sitio oficial descarga el ZIP), `authserver.mojang.com`, `sessionserver.mojang.com`, `meta.multimc.org` y `resources.download.minecraft.net`. Por eso:

- El launcher se obtuvo del artifact oficial de GitHub Actions (`UltimMC/Launcher`).
- Los archivos del juego se descargaron desde hosts permitidos (`piston-meta.mojang.com`, `launcher.mojang.com`, `libraries.minecraft.net` y GitHub).
- Solo se puede jugar **offline / jugar en solitario**. No funcionarán servidores con `online-mode=true`, skins de Microsoft ni el login con cuenta de Microsoft/Mojang.

## Mods y mundos

- Mods: `~/minecraft/data/instances/Minecraft 1.21.8/.minecraft/mods/`
- Mundos: `~/minecraft/data/instances/Minecraft 1.21.8/.minecraft/saves/`
- Resource packs: `~/minecraft/data/instances/Minecraft 1.21.8/.minecraft/resourcepacks/`

## Si algo falla

1. Abre una terminal y ejecuta `~/minecraft/bin/ultimmc` para ver errores.
2. Revisa `~/minecraft/logs/ultimmc.log` y `~/minecraft/data/instances/Minecraft 1.21.8/.minecraft/logs/latest.log`.
3. Si faltan el JAR, las librerías o el asset index, ejecuta `~/minecraft/bin/seed-game-files.py`.
4. Si faltan los assets (sonidos, texturas, fuentes), ejecuta `~/minecraft/bin/seed-assets.py`.

## Repositorio de instalación

Todo se instaló desde `https://github.com/rvf1-k/ultimmc-portable`. Ese repo incluye el instalador `install.sh`, el launcher, el glibc portable y un workflow (`fetch-assets.yml`) que descarga los assets desde GitHub cuando la red bloquea `resources.download.minecraft.net`. Para reinstalar en otro ordenador:

```bash
git clone https://github.com/rvf1-k/ultimmc-portable.git
cd ultimmc-portable
bash install.sh
```

Si la red permite el host de assets, `seed-assets.py` los baja directamente; si no, usa `gh` (hay que hacer `gh auth login` primero).
