import json
import os
import tempfile
import unittest

from presetgen import load_global_config


class PresetGenConfigTests(unittest.TestCase):
    def test_load_global_config_uses_config_file_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = os.path.join(temp_dir, 'cfg')
            os.makedirs(config_dir, exist_ok=True)
            config_path = os.path.join(config_dir, 'custom-config.json')
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(
                    {
                        'root_path': '..\\shaders',
                        'pipeline_root': '..\\pipelines',
                        'parameter_root': '..\\params',
                    },
                    f,
                )

            config = load_global_config(config_path)

            self.assertEqual(config['shader_root_abs'], os.path.normpath(os.path.join(config_dir, '..\\shaders')))
            self.assertEqual(config['pipeline_root_abs'], os.path.normpath(os.path.join(config_dir, '..\\pipelines')))
            self.assertEqual(config['parameter_root_abs'], os.path.normpath(os.path.join(config_dir, '..\\params')))

    def test_load_global_config_requires_existing_file(self):
        with self.assertRaises(ValueError):
            load_global_config('C:\\missing\\presetgen-config.json')


if __name__ == '__main__':
    unittest.main()
