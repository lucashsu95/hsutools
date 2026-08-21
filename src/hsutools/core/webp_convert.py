from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

try:
    from PIL import Image
except ImportError:
    Image = None  # type: ignore[assignment,misc]

from .types import FileOperationResult
from ..utils import iter_files

# Supported source formats for WebP conversion
_WEBP_SOURCE_EXTENSIONS: set[str] = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tiff",
    ".tif",
}


def convert_to_webp(
    directory: Path,
    *,
    quality: int = 80,
    ignore_names: Iterable[str] | None = None,
    include_hidden: bool = False,
    recursive: bool = False,
    dry_run: bool = False,
) -> List[FileOperationResult]:
    """Convert JPG/PNG/BMP/TIFF images to WebP format using Pillow.

    Args:
        directory: Root directory to scan for images.
        quality: WebP quality (1-100, default 80).
        ignore_names: Filenames to skip.
        include_hidden: Whether to include hidden files/dirs.
        recursive: Whether to recurse into subdirectories.
        dry_run: If True, report what would be done without writing.

    Returns:
        List of FileOperationResult for each processed file.
    """
    if Image is None:
        raise ImportError(
            "Pillow is required for WebP conversion. "
            "Install it with: pip install Pillow"
        )

    quality = max(1, min(quality, 100))
    results: List[FileOperationResult] = []

    for src_path in iter_files(
        directory,
        ignore_names=ignore_names,
        include_hidden=include_hidden,
        extensions=_WEBP_SOURCE_EXTENSIONS,
        recursive=recursive,
    ):
        dst_path = src_path.with_suffix(".webp")

        # Skip if .webp already exists
        if dst_path.exists():
            results.append(
                FileOperationResult(path=src_path, success=True, detail="skipped: already exists")
            )
            continue

        if dry_run:
            results.append(
                FileOperationResult(path=src_path, success=True, detail="would convert")
            )
            continue

        try:
            with Image.open(src_path) as img:
                # Convert palette/RGBA to RGB for JPEG-compatible sources if needed
                if img.mode in {"RGBA", "P", "LA"}:
                    # Keep alpha for RGBA/LA, only convert palette images
                    if img.mode == "P":
                        img = img.convert("RGBA")
                img.save(dst_path, format="WEBP", quality=quality)
            results.append(
                FileOperationResult(path=src_path, success=True, detail=f"converted -> {dst_path.name}")
            )
        except Exception as exc:
            results.append(
                FileOperationResult(path=src_path, success=False, error=str(exc))
            )

    return results


__all__ = ["convert_to_webp"]
