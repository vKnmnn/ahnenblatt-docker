#!/usr/bin/env bash
set -euo pipefail
major=${1:?Wine major required}
case "$major" in
    10) packages=(wine wine64 wine32:i386) ;;
    11)
        install -d -m 0755 /etc/apt/keyrings
        curl --fail --silent --show-error --location \
            https://dl.winehq.org/wine-builds/winehq.key -o /etc/apt/keyrings/winehq.asc
        echo 'd965d646defe94b3dfba6d5b4406900ac6c81065428bf9d9303ad7a72ee8d1b8  /etc/apt/keyrings/winehq.asc' | sha256sum -c -
        chmod 0644 /etc/apt/keyrings/winehq.asc
        echo 'deb [arch=amd64,i386 signed-by=/etc/apt/keyrings/winehq.asc] https://dl.winehq.org/wine-builds/debian trixie main' > /etc/apt/sources.list.d/winehq.list
        # Pin the tested major; a future WineHQ stable must not silently become Wine 12.
        packages=('winehq-stable=11.0.0.0~trixie-1')
        ;;
    *) echo "Unsupported Wine major: $major" >&2; exit 1 ;;
esac
# Both Debian Wine 10 and WineHQ's Trixie Wine 11 packages use multilib.
dpkg --add-architecture i386
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends "${packages[@]}"
case "$(wine --version)" in
    "wine-$major".*) ;;
    *) echo "Unexpected Wine version (expected $major)" >&2; exit 1 ;;
esac
# Keep prefix initialization independent of wrappers that prefer the 32-bit loader.
# WineHQ may provide either a split wine64 loader or a unified 64-bit wine loader.
python3 - "$major" <<'PY'
from pathlib import Path
import sys

candidates = ([Path('/usr/lib/wine/wine64')] if sys.argv[1] == '10' else [
    Path('/opt/wine-stable/bin/wine64'), Path('/opt/wine-stable/bin/wine'),
])
for loader in candidates:
    if loader.is_file():
        with loader.open('rb') as stream:
            if stream.read(5) == b'\x7fELF\x02':
                Path('/usr/local/bin/wine-native64').symlink_to(loader)
                break
else:
    raise SystemExit('No native 64-bit Wine loader found')
PY
wine-native64 --version
rm -rf /var/lib/apt/lists/*
