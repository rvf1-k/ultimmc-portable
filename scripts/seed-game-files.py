#!/usr/bin/env python3
"""Descarga/verifica el JAR, las librerías y el asset index de Minecraft 1.21.8.

Los hosts permitidos en este entorno son piston-meta.mojang.com,
launcher.mojang.com y libraries.minecraft.net. El meta de MultiMC se toma de
raw.githubusercontent.com porque meta.multimc.org está bloqueado.
"""
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.request

MC_HOME = os.environ.get("MC_HOME", os.path.expanduser("~/minecraft"))
DATA = os.path.join(MC_HOME, "data")
META_DIR = os.path.join(DATA, "meta", "net.minecraft")
META = os.path.join(META_DIR, "1.21.8.json")
META_URL = "https://raw.githubusercontent.com/MultiMC/meta-multimc/master/net.minecraft/1.21.8.json"
INDEX_URL = "https://raw.githubusercontent.com/MultiMC/meta-multimc/master/net.minecraft/index.json"
ROOT_INDEX_URL = "https://raw.githubusercontent.com/MultiMC/meta-multimc/master/index.json"


def sha1(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(url, dest, expected_sha1=None, retries=3):
    if os.path.exists(dest) and (not expected_sha1 or sha1(dest) == expected_sha1):
        return "cached"
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    last = None
    for attempt in range(retries):
        try:
            tmp = dest + ".part"
            req = urllib.request.Request(url, headers={"User-Agent": "ultimmc-portable/1.0"})
            with urllib.request.urlopen(req, timeout=60) as response, open(tmp, "wb") as out:
                while True:
                    chunk = response.read(1 << 20)
                    if not chunk:
                        break
                    out.write(chunk)
            if expected_sha1 and sha1(tmp) != expected_sha1:
                raise ValueError("SHA1 mismatch: %s" % url)
            os.replace(tmp, dest)
            return "downloaded"
        except Exception as exc:
            last = exc
            time.sleep(1 + attempt)
    raise RuntimeError("failed %s: %s" % (url, last))


def ensure_meta():
    for url, dest in ((ROOT_INDEX_URL, os.path.join(DATA, "meta", "index.json")),
                      (INDEX_URL, os.path.join(META_DIR, "index.json")),
                      (META_URL, META)):
        if not os.path.exists(dest):
            print("meta:", os.path.relpath(dest, DATA), fetch(url, dest))

    with open(META, encoding="utf-8") as f:
        meta = json.load(f)
    jar = meta["mainJar"]["downloads"]["artifact"]
    if "piston-data.mojang.com" in jar["url"]:
        jar["url"] = jar["url"].replace("https://piston-data.mojang.com/",
                                        "https://launcher.mojang.com/")
        with open(META, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=4, ensure_ascii=False)
        print("meta: mainJar URL parcheada a launcher.mojang.com")
    return meta


def main():
    meta = ensure_meta()

    jar = meta["mainJar"]["downloads"]["artifact"]
    group, artifact, version = meta["mainJar"]["name"].split(":")[:3]
    jar_path = os.path.join(DATA, "libraries", group.replace(".", "/"), artifact,
                            version, "%s-%s-client.jar" % (artifact, version))
    results = [("client.jar", fetch(jar["url"], jar_path, jar["sha1"]))]

    ok = bad = 0
    for library in meta["libraries"]:
        artifact_meta = library.get("downloads", {}).get("artifact")
        if not artifact_meta:
            continue
        try:
            fetch(artifact_meta["url"], os.path.join(DATA, "libraries", artifact_meta["path"]),
                  artifact_meta.get("sha1"))
            ok += 1
        except Exception as exc:
            bad += 1
            print("ERROR library", library["name"], exc, file=sys.stderr)
    results.append(("libraries: %d ok, %d failed" % (ok, bad), "done"))

    idx = meta["assetIndex"]
    idx_path = os.path.join(DATA, "assets", "indexes", idx["id"] + ".json")
    results.append(("asset index " + idx["id"],
                    fetch(idx["url"], idx_path, idx["sha1"])))
    for label, status in results:
        print("%-40s %s" % (label, status))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
