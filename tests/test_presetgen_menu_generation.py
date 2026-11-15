import json
import os
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

from presetgen import copy_shader_tree, generate_menu_shaders


def _write_text(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


class PresetGenMenuShaderTests(unittest.TestCase):
    def test_generate_menu_shaders_deduplicates_by_signature(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source_root = os.path.join(temp_dir, 'source')
            output_root = os.path.join(temp_dir, 'output')
            _write_text(os.path.join(source_root, 'menus', 'menu-base.slang'), '#version 450\n')
            _write_text(os.path.join(source_root, 'menus', 'parameters', 'alpha.inc'), '// alpha\n')
            _write_text(
                os.path.join(source_root, 'core.slang'),
                '#include "menus/parameters/alpha.inc"\n',
            )

            copy_shader_tree(source_root, output_root, lambda *args, **kwargs: None)
            pipeline = SimpleNamespace(data={'shaders': {'core': 'core', 'menu': 'menus/menu-sdr'}})

            first = generate_menu_shaders(
                pipeline_objs=[pipeline],
                shader_root_abs=output_root,
                parameter_root_abs=os.path.join(output_root, 'menus', 'parameters'),
                shader_ext='.slang',
                preset_owner_name='first-preset',
                vprint=lambda *args, **kwargs: None,
            )
            second = generate_menu_shaders(
                pipeline_objs=[pipeline],
                shader_root_abs=output_root,
                parameter_root_abs=os.path.join(output_root, 'menus', 'parameters'),
                shader_ext='.slang',
                preset_owner_name='second-preset',
                vprint=lambda *args, **kwargs: None,
            )

            self.assertEqual(first['menus/menu-sdr']['with_ext'], second['menus/menu-sdr']['with_ext'])
            manifest_path = os.path.join(output_root, 'menus', 'menu-manifest.json')
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            self.assertEqual(len(manifest['entries']), 1)

    def test_generate_menu_shaders_creates_distinct_files_for_distinct_includes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source_root = os.path.join(temp_dir, 'source')
            output_root = os.path.join(temp_dir, 'output')
            _write_text(os.path.join(source_root, 'menus', 'menu-base.slang'), '#version 450\n')
            _write_text(os.path.join(source_root, 'menus', 'parameters', 'alpha.inc'), '// alpha\n')
            _write_text(os.path.join(source_root, 'menus', 'parameters', 'beta.inc'), '// beta\n')
            _write_text(
                os.path.join(source_root, 'core-a.slang'),
                '#include "menus/parameters/alpha.inc"\n',
            )
            _write_text(
                os.path.join(source_root, 'core-b.slang'),
                '#include "menus/parameters/beta.inc"\n',
            )

            copy_shader_tree(source_root, output_root, lambda *args, **kwargs: None)
            pipeline_a = SimpleNamespace(data={'shaders': {'core': 'core-a', 'menu': 'menus/menu-sdr'}})
            pipeline_b = SimpleNamespace(data={'shaders': {'core': 'core-b', 'menu': 'menus/menu-sdr'}})

            map_a = generate_menu_shaders(
                pipeline_objs=[pipeline_a],
                shader_root_abs=output_root,
                parameter_root_abs=os.path.join(output_root, 'menus', 'parameters'),
                shader_ext='.slang',
                preset_owner_name='preset-a',
                vprint=lambda *args, **kwargs: None,
            )
            map_b = generate_menu_shaders(
                pipeline_objs=[pipeline_b],
                shader_root_abs=output_root,
                parameter_root_abs=os.path.join(output_root, 'menus', 'parameters'),
                shader_ext='.slang',
                preset_owner_name='preset-b',
                vprint=lambda *args, **kwargs: None,
            )

            self.assertNotEqual(map_a['menus/menu-sdr']['with_ext'], map_b['menus/menu-sdr']['with_ext'])
            manifest_path = os.path.join(output_root, 'menus', 'menu-manifest.json')
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            self.assertEqual(len(manifest['entries']), 2)

    def test_generate_menu_shaders_is_thread_safe_for_shared_output(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source_root = os.path.join(temp_dir, 'source')
            output_root = os.path.join(temp_dir, 'output')
            _write_text(os.path.join(source_root, 'menus', 'menu-base.slang'), '#version 450\n')
            _write_text(os.path.join(source_root, 'menus', 'parameters', 'alpha.inc'), '// alpha\n')
            _write_text(
                os.path.join(source_root, 'core.slang'),
                '#include "menus/parameters/alpha.inc"\n',
            )

            copy_shader_tree(source_root, output_root, lambda *args, **kwargs: None)
            pipeline = SimpleNamespace(data={'shaders': {'core': 'core', 'menu': 'menus/menu-sdr'}})

            def run_one(idx):
                mapping = generate_menu_shaders(
                    pipeline_objs=[pipeline],
                    shader_root_abs=output_root,
                    parameter_root_abs=os.path.join(output_root, 'menus', 'parameters'),
                    shader_ext='.slang',
                    preset_owner_name=f'parallel-{idx}',
                    vprint=lambda *args, **kwargs: None,
                )
                return mapping['menus/menu-sdr']['with_ext']

            with ThreadPoolExecutor(max_workers=8) as executor:
                generated = list(executor.map(run_one, range(24)))

            self.assertEqual(len(set(generated)), 1)
            manifest_path = os.path.join(output_root, 'menus', 'menu-manifest.json')
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            self.assertEqual(len(manifest['entries']), 1)
            generated_shader = os.path.join(output_root, generated[0].replace('/', os.sep))
            self.assertTrue(os.path.exists(generated_shader))

    def test_copy_shader_tree_preserves_existing_output_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source_root = os.path.join(temp_dir, 'source')
            output_root = os.path.join(temp_dir, 'output')
            _write_text(os.path.join(source_root, 'common.slang'), '#version 450\n')
            _write_text(os.path.join(output_root, 'menus', 'menu-existing.slang'), '// keep\n')

            def run_copy(_):
                copy_shader_tree(source_root, output_root, lambda *args, **kwargs: None)

            with ThreadPoolExecutor(max_workers=6) as executor:
                list(executor.map(run_copy, range(16)))

            self.assertTrue(os.path.exists(os.path.join(output_root, 'common.slang')))
            self.assertTrue(os.path.exists(os.path.join(output_root, 'menus', 'menu-existing.slang')))


if __name__ == '__main__':
    unittest.main()
