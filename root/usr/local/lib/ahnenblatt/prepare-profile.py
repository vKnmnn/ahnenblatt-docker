#!/usr/bin/env python3
"""Prepare a new standard-installation profile; never overwrite user settings."""
import json
import os
from pathlib import Path


def prepare(prefix, metadata, app=Path('/opt/ahnenblatt'), files=Path('/config/files')):
    links = {prefix / 'drive_c/AhnenblattApp': app, prefix / 'dosdevices/d:': files}
    for link, target in links.items():
        if link.is_symlink() and os.readlink(link) == str(target):
            continue
        if link.exists() or link.is_symlink():
            raise RuntimeError(f'Refusing to replace existing path: {link}')
        link.symlink_to(target, target_is_directory=True)
    settings = prefix / 'drive_c/users/abc/AppData/Roaming/Ahnenblatt' / metadata['ini']
    if not settings.exists():
        settings.parent.mkdir(parents=True, exist_ok=True)
        # Standard installations use AppData, rather than portable settings
        # alongside the executable. The image application directory stays immutable.
        settings.write_text(
            '[Dateien]\r\n'
            'Familien=D:\\Ahnenblatt\r\n'
            'Suchbegriffe=D:\\Ahnenblatt\r\n'
            'Ausgaben=D:\\Ausgaben\r\n'
            'Bilder=D:\\Bilder\r\n'
            'UseAhnfileDir=0\r\n', encoding='utf-16', newline='',
        )


if __name__ == '__main__':
    prepare(Path(os.environ['WINEPREFIX']), json.loads(Path('/opt/ahnenblatt-image.json').read_text()))
