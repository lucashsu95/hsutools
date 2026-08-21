# Contributing to hsutools

Thanks for your interest in contributing! This guide covers the basics.

## Development Setup

```bash
# Clone the repo
git clone https://gitlab.com/jameshsu1205/hsutools.git
cd hsutools

# Install dependencies
poetry install

# Install with optional features (for s2tw support)
poetry install --extras s2tw

# Verify installation
poetry run hsu --help
```

## Running Tests

```bash
# Run all tests
poetry run pytest

# Run with verbose output
poetry run pytest -v

# Run a specific test
poetry run pytest tests/test_cli.py::test_cpath_creates_markdown
```

## Code Style

### General Rules

- **Type hints**: Required everywhere (`from __future__ import annotations`)
- **String formatting**: f-strings preferred
- **Path handling**: Always use `pathlib.Path` (never `os.path`)
- **Imports**: Group by stdlib → third-party → local, separated by blank lines

### File Organization

```
src/hsutools/
├── cli.py          # CLI layer — thin, delegates to core/
├── config.py       # Constants only, no logic
├── i18n.py         # All user-facing strings via tr()
├── utils.py        # Shared helpers
└── core/           # Business logic — each module independent
```

### i18n Rules

Every user-facing string must go through `tr()`:

```python
from .i18n import tr

# ✅ Correct
typer.echo(tr("cpath.created", path=output_path))

# ❌ Wrong
typer.echo(f"Created {output_path}")
```

Adding a new key:

```python
# In i18n.py → TEXTS dict
"mycommand.new_key": {
    "en": "English text with {variable}",
    "zh": "中文文字，含 {variable}",
},
```

## Adding a New CLI Command

1. **Create core module** — `src/hsutools/core/my_feature.py`
2. **Export from core** — add to `core/__init__.py`
3. **Add CLI command** — in `cli.py` with `@app.command()`
4. **Add i18n keys** — to `i18n.py` (`TEXTS` dict)
5. **Register help keys** — add to `COMMAND_HELP_KEYS` and `OPTION_HELP_KEYS` in `cli.py`
6. **Write tests** — in `tests/test_cli.py`

### Checklist

- [ ] Core function has `dry_run: bool = False` parameter (if modifying files)
- [ ] All user-facing strings use `tr()`
- [ ] New i18n keys have both `en` and `zh` values
- [ ] Tests cover the happy path at minimum
- [ ] `poetry run pytest` passes

## Pull Request Process

1. **Fork & branch** — `git checkout -b feature/my-feature`
2. **Write tests first** — if adding new functionality
3. **Keep commits focused** — one logical change per commit
4. **Run tests before pushing** — `poetry run pytest`
5. **Open PR** — describe what changed and why

### PR Title Format

```
feat: add dry-run mode to filem command
fix: handle empty directory in cpath
docs: update CLI reference
```

## Project Structure Notes

### `core/` Modules

Each module in `core/` is independent. They:
- Accept `Path` objects, return `List[Path]` or `NamedTuple`
- Support `dry_run: bool = False` for preview mode
- Handle their own error cases

### `cli.py`

The CLI layer is intentionally thin:
- Parses arguments
- Calls `core/` functions
- Handles i18n and user interaction (prompts, confirmation)

### `config.py`

Constants only:
- `FILE_SUFFIX_BUCKETS` — extension → category mapping (166 entries)
- `DEFAULT_IGNORE_NAMES` — files to skip by default
- `IMAGE_EXTENSIONS` — supported image formats

## Getting Help

- Open an issue for bugs or feature requests
- Check existing issues before creating new ones
- For questions, use GitHub Discussions (if available)
