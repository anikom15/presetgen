# PresetGen

PresetGen is a Python tool for generating RetroArch slang preset files from structured JSON descriptions. It is designed to help shader authors and advanced users automate the creation of complex preset files, ensuring consistency and maintainability.

## Features
- Compose presets from modular pipeline and parameter set JSON files
- Uses a user-supplied config JSON for `root_path`, `pipeline_root`, and `parameter_root`
- Synchronizes base shaders to `out/shaders` in a parallel-safe way
- Generates menu shaders by content signature, deduplicates identical menu include sets, and records mappings in `out/shaders/menus/menu-manifest.json`
- Writes generated preset files under `out/presets/<type>/`
- Automatic shader index assignment and option handling
- Handles per-shader and global parameters
- Outputs well-formatted `.slangp` files with comments and documentation
- Validates all input files against JSON schemas

## Usage

```
python presetgen.py -i <preset.json> -o <output_dir> -c <config.json> [-v] [--shader-ext .slang]
```

- `-i, --input` : Input preset description file
- `-o OUTPUT_DIR` : Output directory for generated files (required)
- `-c, --config` : Config JSON path (required)
- `-v` : Verbose output (shows details about file loading and processing)
- `--shader-ext` : Shader file extension (default: `.slang`)

Example:
```
python presetgen.py -i example_preset.json -o out -c example_presetgen.json -v
```

Config file example (`example_presetgen.json`):
```json
{
  "root_path": "shaders",
  "pipeline_root": "pipelines",
  "parameter_root": "params"
}
```

## Project Structure
- `presetgen.py` : Main generation script
- `data.py` : Classes for loading and validating JSON files
- `validate_preset.py` : Standalone validation tool
- `pipelines/` : Pipeline JSON files and schema
- `params/` : Parameter set JSON files and schema
- `example_presetgen.json` : Example config for roots (users should provide their own config file)
- `preset.schema.json` : Preset JSON schema
- `requirements.txt` : Python dependencies

## License

This project is licensed under the Apache License, Version 2.0. See the [COPYING](COPYING) file for details.
