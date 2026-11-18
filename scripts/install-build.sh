#!/usr/bin/env bash
set -euo pipefail
series=${1:?series required}
export HOME=/tmp/build-home WINEPREFIX=/tmp/build-prefix WINEARCH=win64
export WINEDEBUG=-all WINEDLLOVERRIDES='mscoree=;winemenubuilder.exe=d'
# shellcheck source=scripts/build-steps.sh
source "$(dirname "${BASH_SOURCE[0]}")/build-steps.sh"
mkdir -p "$HOME" "$WINEPREFIX" /build-output/app /build-output/fonts
run_step 'initialize Wine' 180 wineboot -u
run_step 'wait for Wine initialization' 180 wineserver -w
# Preserve the existing container's font choices without shipping its prefix.
run_step 'install Tahoma and Ubuntu fonts' 600 winetricks -q tahoma uff
run_step 'wait for font registration' 180 wineserver -w
run_step "install Ahnenblatt $series" 300 wine start /wait /unix /tmp/ahnenblatt-setup.exe \
    /SP- /VERYSILENT /SUPPRESSMSGBOXES /NORESTART '/DIR=C:\AhnenblattApp' \
    '/LOG=Z:\tmp\ahnenblatt-install.log'
stop_build_wine
echo '[build] Exporting application files and fonts'
test -d "$WINEPREFIX/drive_c/AhnenblattApp"
cp -a "$WINEPREFIX/drive_c/AhnenblattApp/." /build-output/app/
find "$WINEPREFIX/drive_c/windows/Fonts" -maxdepth 1 -type f \
    \( -iname '*tahoma*.ttf' -o -iname '*ubuntu*.ttf' \) \
    -exec cp '{}' /build-output/fonts/ \;
test -n "$(find /build-output/fonts -iname '*tahoma*.ttf' -print -quit)"
test -n "$(find /build-output/fonts -iname '*ubuntu*.ttf' -print -quit)"
python3 - "$series" <<'PY'
import json
from pathlib import Path
import sys
sys.path.insert(0, '/build/scripts')
from versions import read_manifest, check_version

series = sys.argv[1]
item = read_manifest()[series]
app = Path('/build-output/app')
executables = [p for p in app.iterdir() if p.suffix.lower() == '.exe'
               and p.stem.lower() in ('ahnblatt', 'ahnenblatt', 'ahnenblatt3', 'ahnenblatt4', 'ahnenblatt5')]
if len(executables) != 1:
    raise SystemExit(f'Expected one Ahnenblatt executable, found {executables}')
check_version(executables[0], item['version'])
Path('/build-output/app.json').write_text(json.dumps({
    **item, 'series': series, 'exe': executables[0].name,
}, indent=2) + '\n')
PY
