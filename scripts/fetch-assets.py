#!/usr/bin/env python3
"""Descarga todos los objetos del asset index de Minecraft (para GitHub Actions)."""
import hashlib
import json
import os
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "https://resources.download.minecraft.net"
INDEX = os.environ.get("ASSET_INDEX", "index.json")


def sha1(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(item):
    name, meta = item
    digest = meta["hash"]
    group = "sounds" if name.startswith("minecraft/sounds/") else "core"
    dest = os.path.join("out", group, digest[:2], digest)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    url = "%s/%s/%s" % (BASE, digest[:2], digest)
    last = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ultimmc-portable/1.0"})
            with urllib.request.urlopen(req, timeout=90) as response, open(dest + ".part", "wb") as out:
                while True:
                    chunk = response.read(1 << 20)
                    if not chunk:
                        break
                    out.write(chunk)
            if sha1(dest + ".part") != digest:
                raise ValueError("sha1 mismatch")
            os.replace(dest + ".part", dest)
            return group, "ok"
        except Exception as exc:
            last = exc
            time.sleep(1 + attempt)
    return group, "FAILED %s: %s" % (name, last)


def main():
    with open(INDEX, encoding="utf-8") as f:
        objects = json.load(f)["objects"]
    failed = []
    counts = {"core": 0, "sounds": 0}
    with ThreadPoolExecutor(max_workers=16) as pool:
        futures = [pool.submit(download, item) for item in objects.items()]
        for i, future in enumerate(as_completed(futures), 1):
            group, status = future.result()
            if status.startswith("FAILED"):
                failed.append(status)
                print(status, file=sys.stderr)
            else:
                counts[group] += 1
            if i % 250 == 0:
                print("progress", i, "/", len(objects), counts, flush=True)
    print("counts", counts, "failed", len(failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
