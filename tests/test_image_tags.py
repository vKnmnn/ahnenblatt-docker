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
        owners = [(series, wine) for series in ('2.99', '3', '4', '5')
                  for wine in ('10', '11') if 'latest' in module.tags(series, 'exact', wine)]
        self.assertEqual(owners, [('5', '10')])

    def test_variants_never_overwrite_each_others_tags(self):
        for series, version in [('2.99', '2.99p'), ('3', '3.60'), ('4', '4.55'), ('5', '5.02')]:
            stable = module.tags(series, version, '10')
            experimental = module.tags(series, version, '11')
            self.assertIn(series, stable)
            self.assertIn(version, stable)
            self.assertFalse(set(stable) & set(experimental))
            self.assertEqual(experimental, [f'{series}-wine11', f'{version}-wine11'])

    def test_unsupported_wine_is_rejected(self):
        with self.assertRaises(ValueError):
            module.tags('5', '5.02', '12')
