import importlib.util
from pathlib import Path
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location('image_tags', SCRIPTS / 'image-tags.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ImageTagTests(unittest.TestCase):
    def test_latest_has_exactly_one_owner(self):
        owners = [series for series in ('2.99', '3', '4', '5')
                  if 'latest' in module.tags(series, 'exact', '11')]
        self.assertEqual(owners, ['5'])

    def test_short_tags_and_explicit_wine11_tags_are_published_together(self):
        for series, version in [('2.99', '2.99p'), ('3', '3.60'), ('4', '4.55'), ('5', '5.02')]:
            expected = [f'{series}-wine11', f'{version}-wine11', series, version]
            if series == '5':
                expected.append('latest')
            self.assertEqual(module.tags(series, version, '11'), expected)

    def test_unsupported_wine_is_rejected(self):
        for wine in ('10', '12'):
            with self.assertRaises(ValueError):
                module.tags('5', '5.02', wine)
