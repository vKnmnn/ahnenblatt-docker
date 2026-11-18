#!/usr/bin/env python3
"""Manage installer locks; never silently accept a changed upstream binary."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import urllib.request

MANIFEST = Path(__file__).resolve().parent.parent / "versions/versions.json"


def read_manifest():
    data = json.loads(MANIFEST.read_text())
    if set(data) != {"2.99", "3", "4", "5"}:
        raise ValueError("Expected series 2.99, 3, 4 and 5")
    for series, item in data.items():
        if not re.fullmatch(r"[0-9]+\.[0-9]+[a-z]?", item["version"]):
            raise ValueError(f"Invalid version: {series}")
        if not item["url"].startswith("https://www.ahnenblatt.de/downloads/"):
            raise ValueError(f"Unexpected download URL: {series}")
        if item["sha256"] is not None and not re.fullmatch(r"[0-9a-f]{64}", item["sha256"]):
            raise ValueError(f"Invalid SHA-256: {series}")
        if not re.fullmatch(r"Ahnenblatt[345]?\.ini", item["ini"]):
            raise ValueError(f"Invalid INI filename: {series}")
    return data


def check_version(path, expected):
    result = subprocess.run(
        ["exiftool", "-json", "-ProductVersion", "-FileVersion", str(path)],
        check=True, capture_output=True, text=True,
    )
    tags = json.loads(result.stdout)[0]
    # Numeric PE fields may omit the patch letter (e.g. 2.99p).
    numeric = re.match(r"[0-9]+\.[0-9]+", expected)[0]
    values = [str(tags.get(k, "")) for k in ("ProductVersion", "FileVersion")]
    if not any(re.search(r"(?<![\d.])" + re.escape(numeric) + r"(?!\d)", v) for v in values):
        raise ValueError(f"Expected {expected}, PE version fields are {values}")
    print(f"PE version: {values}; expected {expected}")


def download(item, destination, locking=False):
    if not locking and not item["sha256"]:
        raise ValueError("Installer not locked. Run make lock SERIES=<series>, then commit versions/versions.json")
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent) as work:
        tmp = Path(work) / "installer.exe"
        request = urllib.request.Request(item["url"], headers={"User-Agent": "Ahnenblatt-container-build"})
        with urllib.request.urlopen(request, timeout=120) as response, tmp.open("wb") as output:
            shutil.copyfileobj(response, output)
        with tmp.open("rb") as source:
            if source.read(2) != b"MZ":
                raise ValueError("Download is not a Windows executable")
        digest = hashlib.sha256(tmp.read_bytes()).hexdigest()
        if item["sha256"] and digest != item["sha256"]:
            raise ValueError("Installer checksum changed; review the new release before resetting its lock")
        check_version(tmp, item["version"])
        os.replace(tmp, destination)
    return digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["check", "get", "lock", "fetch", "verify-version"])
    parser.add_argument("series", nargs="?", default="all")
    parser.add_argument("value", nargs="?")
    args = parser.parse_args()
    data = read_manifest()
    if args.command == "check":
        print("Version manifest valid")
        return
    if args.command == "lock":
        selected = data if args.series == "all" else {args.series: data[args.series]}
        for series, item in selected.items():
            path = MANIFEST.parent.parent / ".cache/installers" / f"{item['version']}.exe"
            digest = download(item, path, locking=True)
            item["sha256"] = digest
            print(f"{series}: {item['version']} SHA-256 {digest}")
        tmp = MANIFEST.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(data, indent=2) + "\n")
        tmp.replace(MANIFEST)
        return
    item = data[args.series]
    if args.command == "get":
        print(item[args.value] or "")
    elif args.command == "fetch":
        print(download(item, args.value))
    elif args.command == "verify-version":
        check_version(args.value, item["version"])


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        raise SystemExit(str(error)) from error
