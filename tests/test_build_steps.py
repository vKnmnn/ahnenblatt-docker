from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / 'scripts/build-steps.sh'


class BuildStepTests(unittest.TestCase):
    def shell(self, code):
        return subprocess.run(
            ['bash', '-c', 'set -euo pipefail; source "$1"; ' + code, 'test', str(HELPER)],
            capture_output=True, text=True,
        )

    def test_installer_failure_is_not_hidden_by_cleanup(self):
        result = self.shell('run_step installer 5 bash -c "exit 7"; echo unexpected-success')
        self.assertEqual(result.returncode, 7)
        self.assertIn('FAILED installer: exit 7', result.stderr)
        self.assertNotIn('unexpected-success', result.stdout)

    def test_timeout_identifies_the_step(self):
        result = self.shell('run_step installer 0.05 sleep 2')
        self.assertEqual(result.returncode, 124)
        self.assertIn('FAILED installer: exit 124', result.stderr)

    def test_shutdown_kills_before_waiting(self):
        result = self.shell('''
            export WINEPREFIX=/tmp/build-prefix
            timeout() { shift 2; "$@"; }
            wineserver() { printf 'wineserver %s\\n' "$*"; }
            stop_build_wine
        ''')
        self.assertEqual(result.returncode, 0, result.stderr)
        calls = [line for line in result.stdout.splitlines() if line.startswith('wineserver ')]
        self.assertEqual(calls, ['wineserver -k', 'wineserver -w'])

    def test_shutdown_refuses_a_personal_prefix(self):
        result = self.shell('export WINEPREFIX=/config/wineprefix; stop_build_wine')
        self.assertEqual(result.returncode, 1)
        self.assertIn('Refusing to stop Wine', result.stderr)
