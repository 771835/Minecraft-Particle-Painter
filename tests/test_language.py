import unittest
from language import JsonFileReader
import os
import json

class TestJsonFileReader(unittest.TestCase):

    def setUp(self):
        """在每个测试之前运行，创建一个临时 JSON 文件"""
        self.test_file_path = 'test.json'
        self.test_data = {
            "greeting": "Hello, {}!",
            "farewell": "Goodbye, {}!",
            "age": 30
        }
        with open(self.test_file_path, 'w', encoding='utf-8') as file:
            json.dump(self.test_data, file)

    def tearDown(self):
        """在每个测试之后运行，删除临时 JSON 文件"""
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)

    def test_read_json(self):
        reader = JsonFileReader(self.test_file_path)
        data = reader.read_json()
        self.assertEqual(data, self.test_data)

    def test_get_value(self):
        reader = JsonFileReader(self.test_file_path)
        reader.read_json()
        self.assertEqual(reader.get_value('greeting'), "Hello, {}!")
        self.assertEqual(reader.get_value('age'), 30)
        self.assertIsNone(reader.get_value('nonexistent_key'))
        self.assertEqual(reader.get_value('nonexistent_key', 'default'), 'default')

    def test_get_lang(self):
        reader = JsonFileReader(self.test_file_path)
        reader.read_json()
        self.assertEqual(reader.get_lang('greeting', ['World']), "Hello, World!")
        self.assertEqual(reader.get_lang('farewell', ['Alice']), "Goodbye, Alice!")
        self.assertEqual(reader.get_lang('age'), 30)
        self.assertIsNone(reader.get_lang('nonexistent_key'))
        self.assertEqual(reader.get_lang('nonexistent_key', default='default'), 'default')

if __name__ == '__main__':
    unittest.main()