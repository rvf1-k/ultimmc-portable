#!/usr/bin/env python3
"""Descarga y verifica los 4273 assets de Minecraft 1.21.8.

Primero intenta la descarga directa desde resources.download.minecraft.net.
Si la red la bloquea (como en el centro), usa el workflow `fetch-assets.yml`
de este repositorio mediante `gh` y recoge los artefactos.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

MC_HOME = os.environ.get("MC_HOME", os.path.expanduser("~/minecraft"))
WORKFLOW = "fetch-assets.yml"
INDEX = os.path.join(MC_HOME, "data", "assets", "indexes", "26.json")
OBJECTS = os.path.join(MC_HOME, "data", "assets", "objects")
BASE = "https://resources.download.minecraft.net"


def assets_repo():
    """Repo con el workflow de assets: variable de entorno > config > este repo."""
    if os.environ.get("MC_ASSETS_REPO"):
        return os.environ["MC_ASSETS_REPO"].strip()
    cfg = os.path.join(MC_HOME, "data", "assets-repo")
    if os.path.exists(cfg):
        with open(cfg, encoding="utf-8") as f:
            value = f.read().strip()
        if value:
            return value
    return "rvf1-k/ultimmc-portable"


REPO = assets_repo()


def gh(*args):
    return subprocess.run(["gh", *args, "--repo", REPO], check=True,
                          capture_output=True, text=True).stdout.strip()


def sha1(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def missing_objects(objects):
    return [(name, meta) for name, meta in objects.items()
            if not os.path.exists(os.path.join(OBJECTS, meta["hash"][:2], meta["hash"]))
            or sha1(os.path.join(OBJECTS, meta["hash"][:2], meta["hash"])) != meta["hash"]]


def direct_download(items):
    def one(item):
        name, meta = item
        digest = meta["hash"]
        dest = os.path.join(OBJECTS, digest[:2], digest)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        try:
            req = urllib.request.Request("%s/%s/%s" % (BASE, digest[:2], digest),
                                         headers={"User-Agent": "ultimmc-portable/1.0"})
            with urllib.request.urlopen(req, timeout=60) as r, open(dest + ".part", "wb") as out:
                shutil.copyfileobj(r, out)
            if sha1(dest + ".part") != digest:
                raise ValueError("sha1 mismatch")
            os.replace(dest + ".part", dest)
            return True
        except Exception:
            return False

    ok = 0
    with ThreadPoolExecutor(max_workers=16) as pool:
        for future in as_completed([pool.submit(one, item) for item in items]):
            ok += bool(future.result())
    return ok


def via_workflow():
    subprocess.run(["gh", "workflow", "run", WORKFLOW, "--repo", REPO,
                    "-f", "mode=full", "-f", "index_name=26",
                    "-f", "index_sha1=b95def05dcfc4c523b59d607540c8c95df4da762"], check=True)
    run_id = None
    for _ in range(60):
        run_id = gh("run", "list", "--limit", "1", "--json", "databaseId",
                    "-q", ".[0].databaseId")
        status = gh("run", "view", run_id, "--json", "status", "-q", ".status")
        if status == "completed":
            break
        time.sleep(5)
    else:
        sys.exit("El workflow no terminó a tiempo; revisa: gh run list --repo %s" % REPO)
    with tempfile.TemporaryDirectory(prefix="mc-assets-") as tmp:
        subprocess.run(["gh", "run", "download", run_id, "--repo", REPO,
                        "--dir", tmp], check=True)
        os.makedirs(OBJECTS, exist_ok=True)
        for group in ("assets-core", "assets-sounds"):
            src = os.path.join(tmp, group)
            if os.path.isdir(src):
                shutil.copytree(src, OBJECTS, dirs_exist_ok=True)


def main():
    if not os.path.exists(INDEX):
        sys.exit("Falta el asset index; ejecuta primero seed-game-files.py")
    with open(INDEX, encoding="utf-8") as f:
        objects = json.load(f)["objects"]
    missing = missing_objects(objects)
    if not missing:
        print("assets verificados: %d/%d" % (len(objects), len(objects)))
        return 0

    sample = list(objects.values())[0]["hash"]
    probe = "%s/%s/%s" % (BASE, sample[:2], sample)
    try:
        with urllib.request.urlopen(probe, timeout=10) as r:
            r.read(16)
        direct_ok = True
    except Exception:
        direct_ok = False

    if direct_ok:
        print("descarga directa disponible:", len(missing), "objetos")
        direct_download(missing)
    else:
        print("descarga directa bloqueada; usando GitHub Actions en", REPO)
        if subprocess.run(["gh", "auth", "status"], capture_output=True).returncode != 0:
            sys.exit("Necesitas `gh auth login` para usar el workflow de assets")
        via_workflow()

    bad = missing_objects(objects)
    print("assets verificados: %d/%d" % (len(objects) - len(bad), len(objects)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
