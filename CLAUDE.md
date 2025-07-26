# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ImportRulesEnforcer is a Python tool that automatically refactors import statements in Python codebases. It enforces consistent import patterns by:
- Converting absolute imports to relative imports when modules share the same parent
- Converting relative imports to absolute imports when importing from parent's parent
- Replacing `__all__` imports with direct imports where possible
- Converting private imports (e.g., `_module`) to public imports when available

## Common Commands

### Setup
```bash
make setup  # Full setup including poetry, git init, pre-commit hooks
poetry install  # Install dependencies (project uses Poetry)
```

### Run the tool
```bash
poetry run import_rules_enforcer [files...] [--root <directory>]
# or
poetry run python -m import_rules_enforcer [files...] [--root <directory>]
```

### Testing
```bash
poetry run python -m unittest tests.integration.test_integration
```

## Architecture

### Core Components

1. **Main Entry Point** (`__main__.py`):
   - Orchestrates the conversion process
   - Applies converters in sequence: absolute→relative, relative→absolute, private→public, public→private
   - Uses `libcst` for AST manipulation
   - Returns exit code based on whether files were modified

2. **Base Converter** (`_import_converter.py`):
   - Abstract base class for all import converters
   - Extends `libcst.CSTTransformer`
   - Tracks file modifications via `was_modified` flag

3. **Converter Types**:
   - `Absolute2RelativeConverter`: Converts absolute imports to relative when modules share same parent
   - `Relative2AbsoluteConverter`: Converts relative imports to absolute when importing from parent's parent
   - `Private2PublicConverter`: Converts private module imports to public API imports
   - `Public2PrivateConverter`: Opposite of above (extracts from `__all__`)

4. **Key Dependencies**:
   - `libcst`: For parsing and transforming Python AST
   - `pydantic`/`pydantic-settings`: For CLI argument parsing and settings
   - `utility-functions`: External dependency for file transaction handling

### Conversion Logic Flow

1. Parse command-line arguments via pydantic settings
2. Use `file_modification_transaction` context manager to safely read files
3. Parse each file into libcst Module
4. Apply each converter sequentially, tracking modifications
5. Write back only modified files
6. Print list of modified files and return appropriate exit code

### Testing Approach

Integration tests compare entire directory structures before/after conversion:
- `tests/integration/unmodified/`: Source test files
- `tests/integration/expected/`: Expected output after conversion
- Test copies source to temporary directory, runs conversion, compares with expected

The test uses Python's `filecmp.dircmp` for recursive directory comparison.