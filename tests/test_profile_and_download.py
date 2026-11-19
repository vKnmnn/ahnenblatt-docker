import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


profile = load('profile', 'root/usr/local/lib/ahnenblatt/prepare-profile.py')
versions = load('versions', 'scripts/versions.py')


class ProfileTests(unittest.TestCase):
    def test_user_settings_survive_reinitialization(self):
        with tempfile.TemporaryDirectory() as directory:
            prefix = Path(directory)
            (prefix / 'drive_c').mkdir()
            (prefix / 'dosdevices').mkdir()
            item = {'ini': 'Ahnenblatt4.ini'}
            profile.prepare(prefix, item, files=prefix / 'data')
            ini = prefix / 'drive_c/users/abc/AppData/Roaming/Ahnenblatt/Ahnenblatt4.ini'
            self.assertIn('Familien=D:\\\n', ini.read_text(encoding='utf-16'))
            personal = 'personal settings and activation placeholder'.encode()
            ini.write_bytes(personal)
            profile.prepare(prefix, item, files=prefix / 'data')
            self.assertEqual(ini.read_bytes(), personal)
            self.assertEqual((prefix / 'dosdevices/d:').readlink(), prefix / 'data')

    def test_mounted_data_and_localized_picture_defaults(self):
        cases = [({}, 'Pictures'), ({'LANG': 'de_DE.UTF-8'}, 'Bilder'),
                 ({'LANG': 'fr_FR.UTF-8'}, 'Pictures'),
                 ({'LANG': 'de_DE.UTF-8', 'LC_MESSAGES': 'en_US.UTF-8'}, 'Pictures'),
                 ({'LANG': 'en_US.UTF-8', 'LC_ALL': 'de_DE.UTF-8'}, 'Bilder')]
        for environment, pictures in cases:
            with self.subTest(environment=environment), tempfile.TemporaryDirectory() as directory:
                prefix = Path(directory) / 'prefix'
                (prefix / 'drive_c').mkdir(parents=True)
                (prefix / 'dosdevices').mkdir()
                data = Path(directory) / 'mounted-data'
                media = data / 'Example Family Media'
                media.mkdir(parents=True)
                (media / 'photo.jpg').write_bytes(b'photo placeholder')
                (data / 'family.ahn').write_bytes(b'genealogy placeholder')
                with patch.dict(profile.os.environ, environment, clear=True):
                    profile.prepare(prefix, {'ini': 'Ahnenblatt4.ini'}, files=data)
                ini = prefix / 'drive_c/users/abc/AppData/Roaming/Ahnenblatt/Ahnenblatt4.ini'
                settings = ini.read_text(encoding='utf-16')
                self.assertIn('Familien=D:\\\n', settings)
                self.assertIn(f'Bilder=D:\\{pictures}\n', settings)
                output = 'Ausgabe' if pictures == 'Bilder' else 'Output'
                self.assertIn(f'Ausgaben=D:\\{output}\n', settings)
                self.assertEqual({p.name for p in data.iterdir()},
                                 {'family.ahn', 'Example Family Media', pictures, output})
                self.assertEqual((data / 'family.ahn').read_bytes(), b'genealogy placeholder')
                self.assertEqual((media / 'photo.jpg').read_bytes(), b'photo placeholder')

    def test_existing_application_directory_is_not_replaced(self):
        with tempfile.TemporaryDirectory() as directory:
            prefix = Path(directory)
            existing = prefix / 'drive_c/AhnenblattApp'
            existing.mkdir(parents=True)
            sentinel = existing / 'personal-data'
            sentinel.write_text('keep')
            with self.assertRaises(RuntimeError):
                profile.prepare(prefix, {'ini': 'Ahnenblatt4.ini'})
            self.assertEqual(sentinel.read_text(), 'keep')


class DownloadTests(unittest.TestCase):
    def test_changed_installer_is_rejected_before_version_tool(self):
        item = {'sha256': '0' * 64, 'version': '4.55', 'url': 'https://example.test/setup.exe'}
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / 'setup.exe'
            destination.write_bytes(b'previous known installer')
            with patch.object(versions.urllib.request, 'urlopen', return_value=io.BytesIO(b'MZchanged')):
                with patch.object(versions, 'check_version') as check:
                    with self.assertRaisesRegex(ValueError, 'checksum changed'):
                        versions.download(item, destination)
                    check.assert_not_called()
            self.assertEqual(destination.read_bytes(), b'previous known installer')

    def test_unlocked_build_fails_without_network(self):
        with patch.object(versions.urllib.request, 'urlopen') as network:
            with self.assertRaisesRegex(ValueError, 'not locked'):
                versions.download({'sha256': None}, '/unused')
            network.assert_not_called()

    def test_matching_installer_is_written(self):
        payload = b'MZtest'
        digest = hashlib.sha256(payload).hexdigest()
        item = {'sha256': digest, 'version': '3.60', 'url': 'https://example.test/setup.exe'}
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / 'setup.exe'
            with patch.object(versions.urllib.request, 'urlopen', return_value=io.BytesIO(payload)):
                with patch.object(versions, 'check_version'):
                    self.assertEqual(versions.download(item, destination), digest)
            self.assertEqual(destination.read_bytes(), payload)

    def test_wrong_release_is_rejected(self):
        response = type('Result', (), {'stdout': json.dumps([{'ProductVersion': '4.56'}])})()
        with patch.object(versions.subprocess, 'run', return_value=response):
            with self.assertRaisesRegex(ValueError, 'Expected 4.55'):
                versions.check_version(Path('setup.exe'), '4.55')

    def test_pe_version_without_leading_zero_matches_marketing_version(self):
        response = type('Result', (), {'stdout': json.dumps([{
            'ProductVersion': '5.2.0.1', 'FileVersion': 'Version 5.2.0.1 (64-bit)',
        }])})()
        with patch.object(versions.subprocess, 'run', return_value=response):
            versions.check_version(Path('setup.exe'), '5.02')
            with self.assertRaisesRegex(ValueError, 'Expected 5.03'):
                versions.check_version(Path('setup.exe'), '5.03')
