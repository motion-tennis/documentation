#!/usr/bin/env python3
"""Fetch and verify only the pinned nanopb C codec sources for offline checks."""

import argparse
import hashlib
import io
import json
from pathlib import Path
import tarfile
import urllib.request

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--archive", type=Path, help="Use an already downloaded archive")
    args = parser.parse_args()
    lock = json.loads((HERE / "nanopb-source.lock.json").read_text())
    if args.archive:
        data = args.archive.read_bytes()
    else:
        with urllib.request.urlopen(lock["url"], timeout=60) as response:
            data = response.read(4 * 1024 * 1024 + 1)
    if hashlib.sha256(data).hexdigest() != lock["archive_sha256"]:
        raise SystemExit("The nanopb archive does not match the pinned SHA-256")
    args.destination.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        for name, expected in lock["files"].items():
            member = archive.getmember(lock["archive_prefix"] + name)
            if not member.isfile():
                raise SystemExit(f"Expected a regular source file: {name}")
            source = archive.extractfile(member).read()
            if hashlib.sha256(source).hexdigest() != expected:
                raise SystemExit(f"Source hash mismatch: {name}")
            target = args.destination / name
            if target.exists() and target.read_bytes() != source:
                raise SystemExit(f"Refusing to overwrite a different file: {target}")
            target.write_bytes(source)
    print(args.destination.resolve())


if __name__ == "__main__":
    main()
