import unittest
from mcpartlib.mcdataformat import MinecraftVersion
import numpy as np
class TestMinecraftVersion(unittest.TestCase):
    def test_default_version(self):
        version = MinecraftVersion()
        self.assertEqual(version.get_version(), '1.20.4')

    def test_version_from_string(self):
        version = MinecraftVersion('1.16.5')
        self.assertEqual(version.get_version(), '1.16.5')

    def test_version_from_list(self):
        version = MinecraftVersion([1, 17, 1])
        self.assertEqual(version.get_version(), '1.17.1')

    def test_version_from_int(self):
        version = MinecraftVersion(18)
        self.assertEqual(version.get_version(), '1.18.0')

    def test_version_from_tuple(self):
        version = MinecraftVersion((1, 19, 2))
        self.assertEqual(version.get_version(), '1.19.2')

    def test_version_from_float(self):
        version = MinecraftVersion(1.19)
        self.assertEqual(version.get_version(), '1.19.0')

    def test_version_from_numpy_array(self):
        version = MinecraftVersion(np.array([1, 20, 3]))
        self.assertEqual(version.get_version(), '1.20.3')

    def test_invalid_version_list(self):
        with self.assertRaises(ValueError):
            MinecraftVersion([1, 17])

    def test_invalid_version_type(self):
        with self.assertRaises(ValueError):
            MinecraftVersion({1, 20, 4})

    def test_version_equality(self):
        version1 = MinecraftVersion('1.16.5')
        version2 = MinecraftVersion([1, 16, 5])
        self.assertEqual(version1, version2)

    def test_version_comparison(self):
        version1 = MinecraftVersion('1.16.5')
        version2 = MinecraftVersion('1.17.1')
        self.assertTrue(version1 < version2)

if __name__ == '__main__':
    unittest.main()