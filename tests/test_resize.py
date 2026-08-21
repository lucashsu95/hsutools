"""Unit tests for image_resize."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from hsutools.core.image_resize import _compute_target_size, resize_images


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_image(directory: Path, name: str, size: tuple[int, int] = (200, 100)) -> Path:
    path = directory / name
    Image.new("RGB", size, color=(100, 150, 200)).save(path)
    return path


# ---------------------------------------------------------------------------
# _compute_target_size
# ---------------------------------------------------------------------------

class TestComputeTargetSize:
    def test_scale_down(self):
        result = _compute_target_size(
            (200, 100), width=None, height=None, max_width=None, max_height=None,
            scale=0.5, keep_aspect=True, allow_upscale=False,
        )
        assert result == (100, 50)

    def test_scale_up_blocked(self):
        result = _compute_target_size(
            (200, 100), width=None, height=None, max_width=None, max_height=None,
            scale=2.0, keep_aspect=True, allow_upscale=False,
        )
        assert result == (200, 100)

    def test_scale_up_allowed(self):
        result = _compute_target_size(
            (200, 100), width=None, height=None, max_width=None, max_height=None,
            scale=2.0, keep_aspect=True, allow_upscale=True,
        )
        assert result == (400, 200)

    def test_width_only_with_aspect(self):
        result = _compute_target_size(
            (200, 100), width=100, height=None, max_width=None, max_height=None,
            scale=None, keep_aspect=True, allow_upscale=False,
        )
        assert result == (100, 50)

    def test_height_only_with_aspect(self):
        result = _compute_target_size(
            (200, 100), width=None, height=50, max_width=None, max_height=None,
            scale=None, keep_aspect=True, allow_upscale=False,
        )
        assert result == (100, 50)

    def test_width_and_height_bounding_box(self):
        result = _compute_target_size(
            (400, 200), width=200, height=100, max_width=None, max_height=None,
            scale=None, keep_aspect=True, allow_upscale=False,
        )
        assert result == (200, 100)

    def test_width_and_height_no_aspect(self):
        result = _compute_target_size(
            (400, 200), width=150, height=80, max_width=None, max_height=None,
            scale=None, keep_aspect=False, allow_upscale=False,
        )
        assert result == (150, 80)

    def test_max_width_cap_with_upscale(self):
        # width=300 > original 200, but allow_upscale=False caps at original first
        # then max_width further caps. With upscale=False, result stays at original.
        result = _compute_target_size(
            (200, 100), width=300, height=None, max_width=250, max_height=None,
            scale=None, keep_aspect=True, allow_upscale=False,
        )
        assert result == (200, 100)

    def test_max_height_cap_with_upscale(self):
        result = _compute_target_size(
            (200, 100), width=None, height=200, max_width=None, max_height=150,
            scale=None, keep_aspect=True, allow_upscale=False,
        )
        assert result == (200, 100)

    def test_max_width_cap_allows_shrink(self):
        # width=150 < original 200, so upscale not needed. max_width=100 caps it.
        result = _compute_target_size(
            (200, 100), width=150, height=None, max_width=100, max_height=None,
            scale=None, keep_aspect=True, allow_upscale=False,
        )
        assert result == (100, 50)

    def test_no_upscale_blocks_width(self):
        result = _compute_target_size(
            (100, 50), width=500, height=None, max_width=None, max_height=None,
            scale=None, keep_aspect=True, allow_upscale=False,
        )
        assert result == (100, 50)

    def test_minimum_size_is_one(self):
        result = _compute_target_size(
            (10, 10), width=1, height=1, max_width=None, max_height=None,
            scale=0.01, keep_aspect=True, allow_upscale=True,
        )
        assert result[0] >= 1 and result[1] >= 1

    def test_large_scale_with_max_cap(self):
        result = _compute_target_size(
            (100, 100), width=None, height=None, max_width=50, max_height=50,
            scale=10.0, keep_aspect=True, allow_upscale=True,
        )
        assert result == (50, 50)


# ---------------------------------------------------------------------------
# resize_images
# ---------------------------------------------------------------------------

class TestResizeImages:
    def test_basic_resize(self, tmp_path: Path):
        input_dir = tmp_path / "in"
        input_dir.mkdir()
        _make_image(input_dir, "photo.jpg", (400, 200))
        output_dir = tmp_path / "out"
        result = resize_images(input_dir, output_dir=output_dir, width=200)
        assert len(result) == 1
        with Image.open(result[0]) as img:
            assert img.size == (200, 100)

    def test_resize_with_height(self, tmp_path: Path):
        input_dir = tmp_path / "in"
        input_dir.mkdir()
        _make_image(input_dir, "pic.png", (400, 200))
        output_dir = tmp_path / "out"
        result = resize_images(input_dir, output_dir=output_dir, width=100, height=100)
        assert len(result) == 1
        with Image.open(result[0]) as img:
            assert img.size == (100, 50)

    def test_resize_no_upscale(self, tmp_path: Path):
        input_dir = tmp_path / "in"
        input_dir.mkdir()
        _make_image(input_dir, "small.jpg", (50, 25))
        output_dir = tmp_path / "out"
        result = resize_images(input_dir, output_dir=output_dir, width=200, allow_upscale=False)
        assert len(result) == 1
        with Image.open(result[0]) as img:
            assert img.size == (50, 25)

    def test_resize_with_upscale(self, tmp_path: Path):
        input_dir = tmp_path / "in"
        input_dir.mkdir()
        _make_image(input_dir, "small.jpg", (50, 25))
        output_dir = tmp_path / "out"
        result = resize_images(input_dir, output_dir=output_dir, width=200, allow_upscale=True)
        assert len(result) == 1
        with Image.open(result[0]) as img:
            assert img.size == (200, 100)

    def test_resize_with_scale(self, tmp_path: Path):
        input_dir = tmp_path / "in"
        input_dir.mkdir()
        _make_image(input_dir, "pic.jpg", (200, 100))
        output_dir = tmp_path / "out"
        result = resize_images(input_dir, output_dir=output_dir, scale=0.25, width=None)
        assert len(result) == 1
        with Image.open(result[0]) as img:
            assert img.size == (50, 25)

    def test_resize_format_conversion(self, tmp_path: Path):
        input_dir = tmp_path / "in"
        input_dir.mkdir()
        _make_image(input_dir, "pic.jpg", (100, 50))
        output_dir = tmp_path / "out"
        result = resize_images(input_dir, output_dir=output_dir, width=50, output_format="png")
        assert len(result) == 1
        assert result[0].suffix == ".png"

    def test_resize_with_suffix(self, tmp_path: Path):
        input_dir = tmp_path / "in"
        input_dir.mkdir()
        _make_image(input_dir, "pic.jpg", (100, 50))
        output_dir = tmp_path / "out"
        result = resize_images(input_dir, output_dir=output_dir, width=50, suffix="_thumb")
        assert len(result) == 1
        assert result[0].name == "pic_thumb.jpg"

    def test_resize_overwrite_disabled(self, tmp_path: Path):
        input_dir = tmp_path / "in"
        input_dir.mkdir()
        _make_image(input_dir, "pic.jpg", (100, 50))
        output_dir = tmp_path / "out"
        resize_images(input_dir, output_dir=output_dir, width=50)
        result = resize_images(input_dir, output_dir=output_dir, width=50, overwrite=False)
        assert len(result) == 0

    def test_resize_overwrite_enabled(self, tmp_path: Path):
        input_dir = tmp_path / "in"
        input_dir.mkdir()
        _make_image(input_dir, "pic.jpg", (100, 50))
        output_dir = tmp_path / "out"
        resize_images(input_dir, output_dir=output_dir, width=50)
        result = resize_images(input_dir, output_dir=output_dir, width=50, overwrite=True)
        assert len(result) == 1

    def test_resize_recursive(self, tmp_path: Path):
        input_dir = tmp_path / "in"
        sub = input_dir / "sub"
        sub.mkdir(parents=True)
        _make_image(input_dir, "top.jpg", (100, 50))
        _make_image(sub, "nested.jpg", (100, 50))
        output_dir = tmp_path / "out"
        result = resize_images(input_dir, output_dir=output_dir, width=50, recursive=True)
        assert len(result) == 2

    def test_resize_non_recursive_skips_subdirs(self, tmp_path: Path):
        input_dir = tmp_path / "in"
        sub = input_dir / "sub"
        sub.mkdir(parents=True)
        _make_image(input_dir, "top.jpg", (100, 50))
        _make_image(sub, "nested.jpg", (100, 50))
        output_dir = tmp_path / "out"
        result = resize_images(input_dir, output_dir=output_dir, width=50, recursive=False)
        assert len(result) == 1

    def test_resize_ignores_non_image_files(self, tmp_path: Path):
        input_dir = tmp_path / "in"
        input_dir.mkdir()
        _make_image(input_dir, "pic.jpg", (100, 50))
        (input_dir / "notes.txt").write_text("not an image")
        output_dir = tmp_path / "out"
        result = resize_images(input_dir, output_dir=output_dir, width=50)
        assert len(result) == 1

    def test_resize_ignore_names(self, tmp_path: Path):
        input_dir = tmp_path / "in"
        input_dir.mkdir()
        _make_image(input_dir, "keep.jpg", (100, 50))
        _make_image(input_dir, "skip.jpg", (100, 50))
        output_dir = tmp_path / "out"
        result = resize_images(input_dir, output_dir=output_dir, width=50, ignore_names=["skip.jpg"])
        assert len(result) == 1
        assert result[0].name == "keep.jpg"

    def test_resize_hidden_files_excluded(self, tmp_path: Path):
        input_dir = tmp_path / "in"
        input_dir.mkdir()
        _make_image(input_dir, "visible.jpg", (100, 50))
        _make_image(input_dir, ".hidden.jpg", (100, 50))
        output_dir = tmp_path / "out"
        result = resize_images(input_dir, output_dir=output_dir, width=50, include_hidden=False)
        assert len(result) == 1

    def test_resize_hidden_files_included(self, tmp_path: Path):
        input_dir = tmp_path / "in"
        input_dir.mkdir()
        _make_image(input_dir, ".hidden.jpg", (100, 50))
        output_dir = tmp_path / "out"
        result = resize_images(input_dir, output_dir=output_dir, width=50, include_hidden=True)
        assert len(result) == 1

    def test_resize_quality_parameter(self, tmp_path: Path):
        input_dir = tmp_path / "in"
        input_dir.mkdir()
        _make_image(input_dir, "pic.jpg", (100, 50))
        output_dir = tmp_path / "out"
        result = resize_images(input_dir, output_dir=output_dir, width=50, quality=50)
        assert len(result) == 1

    def test_resize_default_output_dir(self, tmp_path: Path):
        input_dir = tmp_path / "in"
        input_dir.mkdir()
        _make_image(input_dir, "pic.jpg", (100, 50))
        result = resize_images(input_dir, width=50)
        assert len(result) == 1
        assert result[0].parent == (input_dir / "resized").resolve()

    def test_resize_empty_directory(self, tmp_path: Path):
        input_dir = tmp_path / "in"
        input_dir.mkdir()
        output_dir = tmp_path / "out"
        result = resize_images(input_dir, output_dir=output_dir, width=50)
        assert len(result) == 0

    def test_resize_rgba_to_jpeg(self, tmp_path: Path):
        input_dir = tmp_path / "in"
        input_dir.mkdir()
        path = input_dir / "rgba.png"
        Image.new("RGBA", (100, 50), color=(100, 150, 200, 128)).save(path)
        output_dir = tmp_path / "out"
        result = resize_images(input_dir, output_dir=output_dir, width=50, output_format="jpeg")
        assert len(result) == 1
        assert result[0].suffix == ".jpeg"

    def test_resize_max_width_and_height(self, tmp_path: Path):
        input_dir = tmp_path / "in"
        input_dir.mkdir()
        _make_image(input_dir, "big.jpg", (400, 200))
        output_dir = tmp_path / "out"
        result = resize_images(
            input_dir, output_dir=output_dir, width=300, height=300,
            max_width=200, max_height=200,
        )
        assert len(result) == 1
        with Image.open(result[0]) as img:
            assert img.size[0] <= 200
            assert img.size[1] <= 200


# ---------------------------------------------------------------------------
# CLI integration
# ---------------------------------------------------------------------------

class TestResizeCli:
    def test_resize_command(self, tmp_path: Path):
        from typer.testing import CliRunner
        from hsutools.cli import app

        input_dir = tmp_path / "input"
        input_dir.mkdir()
        _make_image(input_dir, "photo.jpg", (100, 50))
        output_dir = tmp_path / "output"

        runner = CliRunner()
        result = runner.invoke(
            app,
            ["resize", "--input", str(input_dir), "--output", str(output_dir), "--width", "50"],
        )
        assert result.exit_code == 0
        assert (output_dir / "photo.jpg").exists()

    def test_resize_invalid_quality(self, tmp_path: Path):
        from typer.testing import CliRunner
        from hsutools.cli import app

        input_dir = tmp_path / "input"
        input_dir.mkdir()

        runner = CliRunner()
        result = runner.invoke(
            app,
            ["resize", "--input", str(input_dir), "--width", "50", "--quality", "0"],
        )
        assert result.exit_code != 0
