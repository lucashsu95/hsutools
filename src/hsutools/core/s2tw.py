"""Simplified Chinese to Traditional Chinese (Taiwan) conversion."""

from __future__ import annotations

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Iterable, Iterator, Literal, NamedTuple

try:
    from opencc import OpenCC
    HAS_OPENCC = True
except ImportError:
    HAS_OPENCC = False


class ConversionResult(NamedTuple):
    """Result of a single file or directory conversion."""
    path: Path
    content_changed: bool
    name_changed: bool
    backup_path: Path | None
    new_path: Path | None
    error: str | None


class ConversionStats(NamedTuple):
    """Statistics for the conversion operation."""
    files_content_modified: int
    files_renamed: int
    dirs_renamed: int
    files_backed_up: int
    errors: int


def check_opencc_available() -> bool:
    """Check if OpenCC library is available."""
    return HAS_OPENCC


def create_backup(
    file_path: Path,
    backup_dir: Path | None = None,
    backup_suffix: str = ".backup",
) -> Path:
    """
    Create a backup of a file.
    
    Args:
        file_path: Path to the file to backup
        backup_dir: Directory to store backups (default: same directory)
        backup_suffix: Suffix to add to backup files
    
    Returns:
        Path to the backup file
    """
    if backup_dir:
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = backup_dir / (file_path.name + backup_suffix)
    else:
        backup_path = file_path.parent / (file_path.name + backup_suffix)
    
    # If backup already exists, add timestamp
    if backup_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        stem = file_path.stem
        suffix = file_path.suffix
        backup_path = backup_path.parent / f"{stem}_{timestamp}{suffix}{backup_suffix}"
    
    shutil.copy2(file_path, backup_path)
    return backup_path


def convert_text_s2tw(text: str, converter: "OpenCC | None" = None) -> str:
    """
    Convert Simplified Chinese text to Traditional Chinese (Taiwan).
    
    Args:
        text: Text to convert
        converter: Optional OpenCC converter instance
    
    Returns:
        Converted text
    """
    if not HAS_OPENCC:
        raise ImportError("OpenCC is not installed. Install it with: pip install opencc-python-reimplemented")
    
    if converter is None:
        converter = OpenCC("s2twp")  # Simplified to Taiwan with phrases
    
    return converter.convert(text)


def convert_file_content(
    file_path: Path,
    converter: "OpenCC | None" = None,
    *,
    create_backup_file: bool = True,
    backup_dir: Path | None = None,
) -> ConversionResult:
    """
    Convert the content of a file from Simplified to Traditional Chinese.
    
    Args:
        file_path: Path to the file
        converter: Optional OpenCC converter instance
        create_backup_file: Whether to create a backup before modifying
        backup_dir: Directory for backups
    
    Returns:
        ConversionResult with details of the operation
    """
    if not HAS_OPENCC:
        return ConversionResult(
            path=file_path,
            content_changed=False,
            name_changed=False,
            backup_path=None,
            new_path=None,
            error="OpenCC is not installed",
        )
    
    if converter is None:
        converter = OpenCC("s2twp")
    
    try:
        # Read file content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Convert content
        converted_content = converter.convert(content)
        
        # Check if content changed
        if converted_content == content:
            return ConversionResult(
                path=file_path,
                content_changed=False,
                name_changed=False,
                backup_path=None,
                new_path=None,
                error=None,
            )
        
        # Create backup if requested
        backup_path = None
        if create_backup_file:
            backup_path = create_backup(file_path, backup_dir)
        
        # Write converted content
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(converted_content)
        
        return ConversionResult(
            path=file_path,
            content_changed=True,
            name_changed=False,
            backup_path=backup_path,
            new_path=None,
            error=None,
        )
    
    except Exception as e:
        return ConversionResult(
            path=file_path,
            content_changed=False,
            name_changed=False,
            backup_path=None,
            new_path=None,
            error=str(e),
        )


def convert_name(
    name: str,
    converter: "OpenCC | None" = None,
) -> str:
    """
    Convert a file or directory name from Simplified to Traditional Chinese.
    
    Args:
        name: Name to convert
        converter: Optional OpenCC converter instance
    
    Returns:
        Converted name
    """
    if not HAS_OPENCC:
        return name
    
    if converter is None:
        converter = OpenCC("s2twp")
    
    return converter.convert(name)


def iter_files_for_conversion(
    path: Path,
    *,
    extensions: set[str] | None = None,
    ignore_names: Iterable[str] | None = None,
    include_hidden: bool = False,
) -> Iterator[Path]:
    """
    Iterate over files for conversion.
    
    Args:
        path: Input path (file or directory)
        extensions: File extensions to include (e.g., {".md", ".txt"})
        ignore_names: Names to ignore
        include_hidden: Include hidden files/directories
    
    Yields:
        Paths to files
    """
    ignore_set = set(ignore_names or [])
    
    if path.is_file():
        if extensions is None or path.suffix.lower() in extensions:
            yield path
        return
    
    for root, dirs, files in os.walk(path, topdown=False):
        root_path = Path(root)
        
        # Filter directories
        dirs[:] = [
            d for d in dirs
            if d not in ignore_set
            and (include_hidden or not d.startswith("."))
        ]
        
        for filename in files:
            if filename in ignore_set:
                continue
            if not include_hidden and filename.startswith("."):
                continue
            
            file_path = root_path / filename
            if extensions is None or file_path.suffix.lower() in extensions:
                yield file_path


def convert_s2tw_recursive(
    path: Path,
    *,
    extensions: set[str] | None = None,
    convert_content: bool = True,
    convert_names: bool = True,
    create_backup_files: bool = True,
    backup_dir: Path | None = None,
    ignore_names: Iterable[str] | None = None,
    include_hidden: bool = False,
) -> tuple[list[ConversionResult], ConversionStats]:
    """
    Recursively convert files and directories from Simplified to Traditional Chinese.
    
    Uses bottom-up traversal to safely rename directories.
    
    Args:
        path: Input path (file or directory)
        extensions: File extensions to process (None = all text files)
        convert_content: Convert file content
        convert_names: Convert file/directory names
        create_backup_files: Create backups before modifying
        backup_dir: Directory for backups (default: alongside originals)
        ignore_names: Names to ignore
        include_hidden: Include hidden files/directories
    
    Returns:
        Tuple of (list of ConversionResult, ConversionStats)
    """
    if not HAS_OPENCC:
        raise ImportError("OpenCC is not installed. Install it with: pip install opencc-python-reimplemented")
    
    # 當 extensions 為 None 時，使用常見文字檔案擴展名
    # 這樣可以處理大部分需要轉換的檔案類型
    text_extensions = {
        ".md", ".txt", ".json", ".yaml", ".yml", ".xml", ".html", ".htm",
        ".css", ".js", ".ts", ".jsx", ".tsx", ".vue", ".py", ".java",
        ".c", ".cpp", ".h", ".hpp", ".cs", ".go", ".rs", ".rb", ".php",
        ".sh", ".bat", ".ps1", ".sql", ".csv", ".ini", ".cfg", ".conf",
        ".toml", ".rst", ".tex", ".log", ".properties", ".env",
    }
    
    # 如果未指定 extensions，使用所有文字檔案擴展名
    effective_extensions = extensions if extensions is not None else text_extensions
    
    converter = OpenCC("s2twp")
    results: list[ConversionResult] = []
    ignore_set = set(ignore_names or [])
    
    stats = {
        "files_content_modified": 0,
        "files_renamed": 0,
        "dirs_renamed": 0,
        "files_backed_up": 0,
        "errors": 0,
    }
    
    input_path = Path(path)
    
    if input_path.is_file():
        # Single file mode
        if input_path.suffix.lower() in effective_extensions:
            if convert_content:
                result = convert_file_content(
                    input_path,
                    converter,
                    create_backup_file=create_backup_files,
                    backup_dir=backup_dir,
                )
                results.append(result)
                if result.content_changed:
                    stats["files_content_modified"] += 1
                if result.backup_path:
                    stats["files_backed_up"] += 1
                if result.error:
                    stats["errors"] += 1
        
        return results, ConversionStats(**stats)
    
    # Directory mode - use bottom-up traversal
    for root, dirs, files in os.walk(input_path, topdown=False):
        root_path = Path(root)
        
        # Process files
        for filename in files:
            if filename in ignore_set:
                continue
            if not include_hidden and filename.startswith("."):
                continue
            
            file_path = root_path / filename
            
            # Check extension - 檢查檔案是否為文字檔案
            if file_path.suffix.lower() not in effective_extensions:
                continue
            
            content_changed = False
            name_changed = False
            backup_path = None
            new_path = None
            error = None
            
            # Convert content
            if convert_content:
                result = convert_file_content(
                    file_path,
                    converter,
                    create_backup_file=create_backup_files,
                    backup_dir=backup_dir,
                )
                content_changed = result.content_changed
                backup_path = result.backup_path
                error = result.error
                
                if content_changed:
                    stats["files_content_modified"] += 1
                if backup_path:
                    stats["files_backed_up"] += 1
                if error:
                    stats["errors"] += 1
            
            # Convert filename (after content, in case path changes)
            current_path = file_path
            if convert_names and not error:
                new_name = convert_name(filename, converter)
                if new_name != filename:
                    new_file_path = root_path / new_name
                    if not new_file_path.exists():
                        try:
                            os.rename(current_path, new_file_path)
                            name_changed = True
                            new_path = new_file_path
                            stats["files_renamed"] += 1
                        except Exception as e:
                            error = str(e)
                            stats["errors"] += 1
            
            if content_changed or name_changed or error:
                results.append(ConversionResult(
                    path=file_path,
                    content_changed=content_changed,
                    name_changed=name_changed,
                    backup_path=backup_path,
                    new_path=new_path,
                    error=error,
                ))
        
        # Process directories (rename)
        if convert_names:
            for dirname in dirs:
                if dirname in ignore_set:
                    continue
                if not include_hidden and dirname.startswith("."):
                    continue
                
                new_dirname = convert_name(dirname, converter)
                if new_dirname != dirname:
                    old_dir_path = root_path / dirname
                    new_dir_path = root_path / new_dirname
                    
                    if not new_dir_path.exists():
                        try:
                            os.rename(old_dir_path, new_dir_path)
                            stats["dirs_renamed"] += 1
                            results.append(ConversionResult(
                                path=old_dir_path,
                                content_changed=False,
                                name_changed=True,
                                backup_path=None,
                                new_path=new_dir_path,
                                error=None,
                            ))
                        except Exception as e:
                            stats["errors"] += 1
                            results.append(ConversionResult(
                                path=old_dir_path,
                                content_changed=False,
                                name_changed=False,
                                backup_path=None,
                                new_path=None,
                                error=str(e),
                            ))
    
    return results, ConversionStats(**stats)


__all__ = [
    "check_opencc_available",
    "convert_file_content",
    "convert_name",
    "convert_s2tw_recursive",
    "convert_text_s2tw",
    "ConversionResult",
    "ConversionStats",
    "create_backup",
]
