from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from PIL import Image, ImageOps

from ..config import IMAGE_EXTENSIONS
from ..utils import ensure_directory

Resample = getattr(Image, "Resampling", Image)


def _is_hidden(path: Path, root: Path) -> bool:
    """Check whether any part of the relative path is hidden."""
    return any(part.startswith(".") for part in path.relative_to(root).parts)


def _iter_image_files(
    directory: Path,
    *,
    recursive: bool,
    include_hidden: bool,
    ignore_names: Iterable[str] | None = None,
) -> Iterable[Path]:
    ignore = set(ignore_names or [])
    iterator = directory.rglob("*") if recursive else directory.iterdir()
    for path in iterator:
        if path.name in ignore:
            continue
        if not include_hidden and _is_hidden(path, directory):
            continue
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
            yield path


def _compute_target_size(
    original_size: Tuple[int, int],
    *,
    width: Optional[int],
    height: Optional[int],
    max_width: Optional[int],
    max_height: Optional[int],
    scale: Optional[float],
    keep_aspect: bool,
    allow_upscale: bool,
) -> Tuple[int, int]:
    orig_w, orig_h = original_size
    target_w, target_h = orig_w, orig_h

    if scale is not None:
        target_w = int(orig_w * scale)
        target_h = int(orig_h * scale)
    elif width is not None or height is not None:
        target_w = width or orig_w
        target_h = height or orig_h
        if keep_aspect:
            if width and height:
                ratio = min(width / orig_w, height / orig_h)
                target_w = int(orig_w * ratio)
                target_h = int(orig_h * ratio)
            elif width:
                ratio = width / orig_w
                target_h = int(orig_h * ratio)
            elif height:
                ratio = height / orig_h
                target_w = int(orig_w * ratio)
    # Apply bounding box limits
    if max_width is not None or max_height is not None:
        max_w = max_width if max_width is not None else target_w
        max_h = max_height if max_height is not None else target_h
        if keep_aspect:
            ratio = min(max_w / target_w, max_h / target_h)
            if ratio < 1:
                target_w = int(target_w * ratio)
                target_h = int(target_h * ratio)
        else:
            target_w = min(target_w, max_w)
            target_h = min(target_h, max_h)

    if not allow_upscale:
        if keep_aspect:
            ratio = min(1.0, orig_w / target_w, orig_h / target_h)
            target_w = int(target_w * ratio)
            target_h = int(target_h * ratio)
        else:
            target_w = min(target_w, orig_w)
            target_h = min(target_h, orig_h)

    return max(1, target_w), max(1, target_h)


def resize_images(
    input_dir: Path,
    *,
    output_dir: Optional[Path] = None,
    width: int | None = 1920,
    height: int | None = None,
    max_width: int | None = None,
    max_height: int | None = None,
    scale: float | None = None,
    keep_aspect: bool = True,
    allow_upscale: bool = False,
    quality: int = 90,
    output_format: str | None = None,
    suffix: str | None = None,
    overwrite: bool = False,
    recursive: bool = False,
    include_hidden: bool = False,
    ignore_names: Iterable[str] | None = None,
) -> List[Path]:
    """Resize images in a directory.

    Returns a list of written file paths.
    """
    target_dir = (output_dir or (input_dir / "resized")).resolve()
    ensure_directory(target_dir)

    written: List[Path] = []
    for image_path in _iter_image_files(
        input_dir, recursive=recursive, include_hidden=include_hidden, ignore_names=ignore_names
    ):
        relative = image_path.relative_to(input_dir)
        destination_dir = target_dir / relative.parent
        ensure_directory(destination_dir)

        ext = (f".{output_format.lower()}" if output_format else image_path.suffix).lower()
        name_suffix = suffix or ""
        destination_path = destination_dir / f"{image_path.stem}{name_suffix}{ext}"

        if destination_path.exists() and not overwrite:
            continue

        with Image.open(image_path) as img:
            img = ImageOps.exif_transpose(img)
            target_size = _compute_target_size(
                img.size,
                width=width,
                height=height,
                max_width=max_width,
                max_height=max_height,
                scale=scale,
                keep_aspect=keep_aspect,
                allow_upscale=allow_upscale,
            )
            resized = img.resize(target_size, resample=Resample.LANCZOS)

            fmt = (output_format or img.format or ext.lstrip(".") or "png").upper()
            if fmt == "JPG":
                fmt = "JPEG"
            save_kwargs = {"format": fmt}
            if fmt in {"JPEG", "JPG", "WEBP"}:
                save_kwargs["quality"] = max(1, min(quality, 100))
                save_kwargs["optimize"] = True
            if fmt in {"JPEG", "JPG"} and resized.mode in {"RGBA", "P"}:
                resized = resized.convert("RGB")

            resized.save(destination_path, **save_kwargs)
            written.append(destination_path)

    return written


__all__ = ["resize_images"]
