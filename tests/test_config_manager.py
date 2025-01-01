import unittest
import os
import yaml
from config_manager import YamlFileManager

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
        data = self.manager.read_yaml()
        self.assertEqual(data, self.test_data)

    def test_write_yaml(self):
        new_data = {'key3': 'value3'}
        self.manager.set_data(new_data)
        self.manager.write_yaml()
        with open(self.test_file, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        self.assertEqual(data, new_data)

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
        self.assertNotIn('key1', self.manager.get_data())

    def test_str(self):
        self.assertEqual(str(self.manager), str(self.test_data))

    def test_getitem(self):
        self.assertEqual(self.manager['key1'], 'value1')

    def test_setitem(self):
        self.manager['key3'] = 'value3'
        self.assertEqual(self.manager['key3'], 'value3')

    def test_iter(self):
        keys = [key for key in self.manager]
        self.assertEqual(keys, list(self.test_data.keys()))

    def test_len(self):
        self.assertEqual(len(self.manager), len(self.test_data))

    def test_add(self):
        other_manager = YamlFileManager(self.test_file, yaml_data={'key3': 'value3'})
        combined_manager = self.manager + other_manager
        expected_data = {**self.test_data, **{'key3': 'value3'}}
        self.assertEqual(combined_manager.get_data(), expected_data)

    def test_enter_exit(self):
        with YamlFileManager(self.test_file) as manager:
            self.assertEqual(manager.get_data(), self.test_data)

    def test_eq(self):
        other_manager = YamlFileManager(self.test_file)
        self.assertTrue(self.manager == other_manager)

    def test_call(self):
        self.assertEqual(self.manager(), self.test_data)

if __name__ == '__main__':
    unittest.main()