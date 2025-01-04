import unittest
import os
from config_manager import YamlFileManager
import yaml

class TestYamlFileManager(unittest.TestCase):
    def setUp(self):
        self.test_file = 'test_config.yaml'
        self.test_data = {'key1': 'value1', 'key2': 'value2'}
        with open(self.test_file, 'w', encoding='utf-8') as file:
            yaml.dump(self.test_data, file, allow_unicode=True)
        self.manager = YamlFileManager(self.test_file)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_read_yaml(self):
        data = self.manager.read()
        self.assertEqual(data, self.test_data)

    def test_get_data(self):
        data = self.manager.get_data()
        self.assertEqual(data, self.test_data)

    def test_set_data(self):
        new_data = {'key3': 'value3'}
        self.manager.set_data(new_data)
        self.assertEqual(self.manager.get_data(), new_data)

    def test_get_value(self):
        value = self.manager.get_value('key1')
        self.assertEqual(value, 'value1')

    def test_set_value(self):
        self.manager.set_value('key3', 'value3')
        self.assertEqual(self.manager.get_value('key3'), 'value3')

    def test_delete_key(self):
        self.manager.delete_key('key1')
        self.assertIsNone(self.manager.get_value('key1'))

    def test_save(self):
        new_data = {'key3': 'value3'}
        self.manager.set_data(new_data)
        self.manager.save()
        with open(self.test_file, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        self.assertEqual(data, new_data)

    def test_reload(self):
        new_data = {'key3': 'value3'}
        with open(self.test_file, 'w', encoding='utf-8') as file:
            yaml.dump(new_data, file, allow_unicode=True)
        self.manager.reload()
        self.assertEqual(self.manager.get_data(), new_data)

    def test_close(self):
        self.manager.close()
        self.assertTrue(self.manager.is_closed)

if __name__ == '__main__':
    unittest.main()