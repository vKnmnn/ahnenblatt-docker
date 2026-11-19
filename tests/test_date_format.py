import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

PATH = Path(__file__).resolve().parents[1] / 'root/usr/local/lib/ahnenblatt/configure-date.py'
spec = importlib.util.spec_from_file_location('date_format', PATH)
date_format = importlib.util.module_from_spec(spec)
spec.loader.exec_module(date_format)


class DateFormatTests(unittest.TestCase):
    def test_windows_date_order_and_separator(self):
        for pattern, separator, order in [('dd.MM.yyyy', '.', '1'),
                                           ('M/d/yyyy', '/', '0'),
                                           ('yyyy-MM-dd', '-', '2')]:
            with self.subTest(pattern=pattern):
                self.assertEqual(date_format.date_values(pattern),
                                 {'sShortDate': pattern, 'sDate': separator, 'iDate': order})

    def test_invalid_format_does_not_change_registry(self):
        for pattern in ['yyyy-dd-MM', 'dd.MM.dd', 'dd/MM-yyyy', 'TT.MM.JJJJ', 'x\nvalue']:
            with self.subTest(pattern=pattern), patch.object(date_format.subprocess, 'run') as run:
                with self.assertRaises(ValueError):
                    date_format.configure(pattern)
                run.assert_not_called()

    def test_empty_override_preserves_existing_settings(self):
        with patch.object(date_format.subprocess, 'run') as run:
            date_format.configure('')
            run.assert_not_called()

    def test_override_updates_only_date_values_and_waits_for_wine(self):
        with patch.object(date_format.subprocess, 'run') as run:
            date_format.configure('dd.MM.yyyy')
        commands = [call.args[0] for call in run.call_args_list]
        self.assertEqual([command[5] for command in commands[:-1]],
                         ['sShortDate', 'sDate', 'iDate'])
        self.assertTrue(all(command[3] == r'HKCU\Control Panel\International'
                            for command in commands[:-1]))
        self.assertEqual(commands[-1], ['wineserver', '-w'])
