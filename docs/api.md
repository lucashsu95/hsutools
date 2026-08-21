# Core API Reference

The `core/` modules provide the business logic behind the CLI. Each module is independent and can be used as a library.

## Common Patterns

All core functions follow these conventions:
- Accept `Path` objects for file/directory inputs
- Return `List[Path]` for operations that produce output files
- Support `dry_run: bool = False` for preview mode
- Use `ignore_names: Iterable[str] | None` to skip files
- Use `include_hidden: bool = False` to control hidden file handling

---

## `core.create_path`

Generate Markdown directory tree listings.

### `generate_path_md(root, *, output_file, ignore_names, max_depth) -> Path`

Generate a markdown file listing the directory tree.

```python
from pathlib import Path
from hsutools.core import generate_path_md

output = generate_path_md(
    Path("./my-project"),
    output_file="path.md",
    ignore_names={".git", "__pycache__"},
    max_depth=3,
)
# Returns: Path("my-project/path.md")
```

**Parameters:**
- `root: Path` — Target directory
- `output_file: str` — Output filename (default: `"path.md"`)
- `ignore_names: Iterable[str] | None` — Names to exclude
- `max_depth: int | None` — Traversal depth limit (None = unlimited)

---

## `core.file_manage`

Categorize files into subdirectories by date, prefix, or extension.

### `categorize_files(directory, mode, *, prefix, ignore_names, include_hidden, dry_run) -> List[Path]`

```python
from pathlib import Path
from hsutools.core import categorize_files

# Sort by extension (e.g., Images/, Docs/, PDF_files/)
moved = categorize_files(Path("./downloads"), mode="suffix")

# Sort by modification date (MMDD format)
moved = categorize_files(Path("./downloads"), mode="date")

# Sort by filename prefix
moved = categorize_files(Path("./downloads"), mode="prefix", prefix="IMG_")
```

**Parameters:**
- `directory: Path` — Target directory
- `mode: "date" | "prefix" | "suffix"` — Grouping strategy
- `prefix: str | None` — Required when `mode="prefix"`
- `dry_run: bool` — Preview without modifying

**Returns:** List of paths that would be (or were) moved.

---

## `core.file_renamer`

Batch rename files by text replacement.

### `replace_names(directory, *, find_text, replace_text, include_dirs, ignore_names, include_hidden, dry_run) -> List[Path]`

```python
from pathlib import Path
from hsutools.core import replace_names

# Rename files containing "old" to "new"
updated = replace_names(
    Path("./photos"),
    find_text="old",
    replace_text="new",
    include_dirs=True,
)
```

**Parameters:**
- `directory: Path` — Target directory
- `find_text: str` — Text to find in filenames
- `replace_text: str` — Replacement text
- `include_dirs: bool` — Also rename directories (default: False)
- `dry_run: bool` — Preview without modifying

---

## `core.docx_to_pdf`

Convert DOCX files to PDF.

### `check_docx2pdf_available() -> bool`

Check if `docx2pdf` is installed.

### `convert_docx_directory(directory, *, ignore_names, include_hidden, dry_run) -> List[Path]`

```python
from pathlib import Path
from hsutools.core import convert_docx_directory

converted = convert_docx_directory(Path("./reports"))
# Returns: [Path("./reports/report1.pdf"), Path("./reports/report2.pdf"), ...]
```

**Note:** Requires `docx2pdf` (which requires Microsoft Word on the system).

---

## `core.image_resize`

Resize images with flexible sizing rules.

### `resize_images(input_dir, *, output_dir, width, height, ...) -> List[Path]`

```python
from pathlib import Path
from hsutools.core import resize_images

# Resize to 800px width, maintain aspect ratio
written = resize_images(
    Path("./photos"),
    width=800,
    keep_aspect=True,
)

# Resize to 1920x1080 bounding box, convert to WebP
written = resize_images(
    Path("./photos"),
    output_dir=Path("./photos-webp"),
    width=1920,
    height=1080,
    output_format="webp",
    quality=85,
)
```

**Parameters:**
- `input_dir: Path` — Source directory
- `output_dir: Path | None` — Output directory (default: `input_dir/resized`)
- `width: int | None` — Target width
- `height: int | None` — Target height
- `max_width: int | None` — Maximum width cap
- `max_height: int | None` — Maximum height cap
- `scale: float | None` — Scale factor (e.g., 0.5 = half size)
- `keep_aspect: bool` — Preserve aspect ratio (default: True)
- `allow_upscale: bool` — Allow enlarging (default: False)
- `quality: int` — JPEG/WEBP quality 1-100 (default: 90)
- `output_format: str | None` — Force output format (e.g., "jpeg", "png", "webp")
- `suffix: str | None` — Append suffix before extension
- `overwrite: bool` — Overwrite existing files (default: False)
- `recursive: bool` — Process subdirectories (default: False)
- `dry_run: bool` — Preview without modifying

**Supported formats:** PNG, JPG, JPEG, JFIF, GIF, TIF, TIFF, WebP, BMP, ICO, HEIC, RAW

---

## `core.s2tw`

Simplified Chinese to Traditional Chinese (Taiwan) conversion.

### `check_opencc_available() -> bool`

Check if OpenCC is installed.

### `convert_s2tw_recursive(path, *, extensions, convert_content, convert_names, ...) -> Tuple[list[ConversionResult], ConversionStats]`

```python
from pathlib import Path
from hsutools.core import convert_s2tw_recursive

results, stats = convert_s2tw_recursive(
    Path("./docs"),
    convert_content=True,
    convert_names=True,
    create_backup_files=True,
    backup_dir=Path("./backup"),
)

print(f"Content modified: {stats.files_content_modified}")
print(f"Files renamed: {stats.files_renamed}")
print(f"Errors: {stats.errors}")
```

**Parameters:**
- `path: Path` — Input file or directory
- `extensions: set[str] | None` — File extensions to process (None = common text files)
- `convert_content: bool` — Convert file content (default: True)
- `convert_names: bool` — Convert file/directory names (default: True)
- `create_backup_files: bool` — Create backups before modifying (default: True)
- `backup_dir: Path | None` — Backup directory (default: alongside originals)
- `ignore_names: Iterable[str] | None` — Names to skip
- `include_hidden: bool` — Include hidden files (default: False)

### `ConversionResult` (NamedTuple)

```python
class ConversionResult(NamedTuple):
    path: Path              # Original path
    content_changed: bool   # Was content modified?
    name_changed: bool      # Was name modified?
    backup_path: Path | None  # Backup location (if created)
    new_path: Path | None   # New path (if renamed)
    error: str | None       # Error message (if any)
```

### `ConversionStats` (NamedTuple)

```python
class ConversionStats(NamedTuple):
    files_content_modified: int
    files_renamed: int
    dirs_renamed: int
    files_backed_up: int
    errors: int
```

### Lower-level functions

```python
# Convert a single file's content
from hsutools.core.s2tw import convert_file_content
result = convert_file_content(Path("doc.md"))

# Convert a single string
from hsutools.core.s2tw import convert_text_s2tw
traditional = convert_text_s2tw("简体中文")  # → "繁體中文"

# Convert a filename
from hsutools.core.s2tw import convert_name
new_name = convert_name("文件名.md")  # → "檔案名.md"
```

---

## Utility Functions (`utils.py`)

### `resolve_directory(path: Path) -> Path`

Expand and validate a directory path. Raises `typer.BadParameter` if invalid.

### `resolve_path(path: Path) -> Path`

Expand and validate a file or directory path.

### `iter_files(directory, *, ignore_names, include_hidden, extensions) -> Iterator[Path]`

Iterate over files in a directory with filtering.

### `ensure_directory(path: Path) -> None`

Create directory and parents if they don't exist.
