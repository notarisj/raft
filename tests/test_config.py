import unittest
import json
import os
import tempfile

from src.configuration_reader import IniConfig, JsonConfig


class TestIniConfig(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.ini_file = os.path.join(self.tmp_dir.name, 'test.ini')

        ini_content = """
        [Section1]
        key1 = value1
        key2 = value2

        [Section2]
        key3 = value3
        """
        with open(self.ini_file, 'w') as f:
            f.write(ini_content)

        self.ini_config = IniConfig(self.ini_file)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_get_property(self):
        value = self.ini_config.get_property('Section1', 'key1')
        self.assertEqual(value, 'value1')

    def test_get_all_properties(self):
        properties = self.ini_config.get_all_properties('Section2')
        expected_properties = {'key3': 'value3'}
        self.assertDictEqual(properties, expected_properties)

    def test_save(self):
        new_ini_file = os.path.join(self.tmp_dir.name, 'new.ini')
        self.ini_config.save()
        self.assertTrue(os.path.isfile(new_ini_file))

        with open(new_ini_file) as f:
            saved_content = f.read()

        with open(self.ini_file) as f:
            original_content = f.read()

        self.assertEqual(saved_content, original_content)


class TestJsonConfig(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.json_file = os.path.join(self.tmp_dir.name, 'test.json')

        json_content = """
        {
            "key1": "value1",
            "key2": "value2"
        }
        """
        with open(self.json_file, 'w') as f:
            f.write(json_content)

        self.json_config = JsonConfig(self.json_file)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_get_property(self):
        value = self.json_config.get_property('key1')
        self.assertEqual(value, 'value1')

    def test_get_all_properties(self):
        properties = self.json_config.get_all_properties()
        expected_properties = {'key1': 'value1', 'key2': 'value2'}
        self.assertDictEqual(properties, expected_properties)

    def test_save(self):
        new_json_file = os.path.join(self.tmp_dir.name, 'new.json')
        self.json_config.save()
        self.assertTrue(os.path.isfile(new_json_file))

        with open(new_json_file) as f:
            saved_content = json.load(f)

        with open(self.json_file) as f:
            original_content = json.load(f)

        self.assertEqual(saved_content, original_content)


if __name__ == '__main__':
    unittest.main()
