#!/usr/bin/env bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
python3 scripts/versions.py check
python3 - <<'PY'
import ast
from pathlib import Path
import xml.etree.ElementTree as ET
for folder in ('scripts', 'root/usr/local/lib', 'tests'):
    for path in Path(folder).rglob('*.py'):
        ast.parse(path.read_text(), filename=str(path))
for path in ('root/etc/rc.xml', 'root/etc/xdg/openbox/rc.xml', 'root/etc/fonts/local.conf'):
    ET.parse(path)
print('Python and XML syntax valid')
PY
mapfile -t scripts < <(find scripts root/etc/services.d root/usr/local/bin -type f \
    \( -name '*.sh' -o -name run -o -name finish -o -name 'ahnenblatt-*' \))
for script in "${scripts[@]}"; do bash -n "$script"; done
if command -v shellcheck >/dev/null; then
    shellcheck -s bash "${scripts[@]}"
else
    echo 'shellcheck unavailable: Bash syntax checked, lint skipped'
fi
python3 -m unittest discover -s tests -v
