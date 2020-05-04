from unittest import TestCase
from opendemic.modelling import systrom


class TestPosteriors(TestCase):
    def test_raises(self):
        with self.assertRaises(ValueError):
            systrom.get_posteriors([[1, 2], [3, 4]])


class TestHDI(TestCase):
    def test_raises(self):
        with self.assertRaises(ValueError):
            systrom.high_density_interval([[1, 2], [3, 4]])
