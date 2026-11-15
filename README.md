# PresetGen

PresetGen is a Python tool for generating RetroArch slang preset files from structured JSON descriptions. It is designed to help shader authors and advanced users automate the creation of complex preset files, ensuring consistency and maintainability.

## Features
- Compose presets from modular pipeline and parameter set JSON files
- Uses a global `presetgen.json` for `root_path`, `pipeline_root`, and `parameter_root`
- Copies base shaders to `out/shaders` and generates menu shaders there
- Writes generated preset files under `out/presets/<type>/`
- Automatic shader index assignment and option handling
- Handles per-shader and global parameters
- Outputs well-formatted `.slangp` files with comments and documentation
- Validates all input files against JSON schemas

## Usage

```
python presetgen.py -i <preset.json> -o <output_dir> [-v] [--shader-ext .slang]
```

- `-i, --input` : Input preset description file
- `-o OUTPUT_DIR` : Output directory (default: `out` in the script directory)
- `-v` : Verbose output (shows details about file loading and processing)
- `--shader-ext` : Shader file extension (default: `.slang`)

Example:
```
python presetgen.py -i example_preset.json -o out -v
```

Global config example (`presetgen.json` at repository root):
```json
{
  "root_path": "example_shaders",
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
- `presetgen.json` : Global roots for shaders, pipelines, and parameter sets
- `preset.schema.json` : Preset JSON schema
- `requirements.txt` : Python dependencies

## License

This project is licensed under the Apache License, Version 2.0. See the [COPYING](COPYING) file for details.
