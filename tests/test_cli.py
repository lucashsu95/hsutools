from pathlib import Path

from typer.testing import CliRunner

from PIL import Image

from hsutools.cli import app

runner = CliRunner()


def test_cpath_creates_markdown(tmp_path: Path) -> None:
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "file.txt").write_text("demo", encoding="utf-8")

    result = runner.invoke(app, ["cpath", "--path", str(tmp_path), "--max-depth", "2"])

    assert result.exit_code == 0
    assert (tmp_path / "path.md").exists()


def test_rename_command(tmp_path: Path) -> None:
    original = tmp_path / "hello_test.txt"
    original.write_text("data", encoding="utf-8")

    result = runner.invoke(
        app,
        ["rename", "--path", str(tmp_path), "--find", "test", "--replace", "done"],
        input="y\n",
    )

    assert result.exit_code == 0
    assert not original.exists()
    assert (tmp_path / "hello_done.txt").exists()


def test_filem_suffix(tmp_path: Path) -> None:
    image = tmp_path / "pic.png"
    doc = tmp_path / "notes.docx"
    image.write_text("img", encoding="utf-8")
    doc.write_text("doc", encoding="utf-8")

    result = runner.invoke(app, ["filem", "--path", str(tmp_path), "--mode", "suffix"], input="y\n")

    assert result.exit_code == 0
    assert (tmp_path / "Images" / "pic.png").exists()
    assert (tmp_path / "Docs" / "notes.docx").exists()


def test_topdf_no_files(tmp_path: Path) -> None:
    result = runner.invoke(app, ["topdf", "--path", str(tmp_path)])

    assert result.exit_code == 0
    assert "No .docx files" in result.stdout


def test_help_lang_flag_zh() -> None:
    result = runner.invoke(app, ["--lang", "zh", "--help"])

    assert result.exit_code == 0
    assert "介面語言" in result.stdout
    assert "轉換" in result.stdout  # should surface translated command help


def test_help_env_lang_zh(monkeypatch) -> None:
    monkeypatch.setenv("HSU_LANG", "zh")
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "介面語言" in result.stdout


def test_resize_command(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    sample = input_dir / "photo.jpg"
    Image.new("RGB", (100, 50), color=(255, 0, 0)).save(sample)

    result = runner.invoke(
        app,
        [
            "resize",
            "--input",
            str(input_dir),
            "--output",
            str(output_dir),
            "--width",
            "50",
        ],
    )

    assert result.exit_code == 0
    resized = output_dir / "photo.jpg"
    assert resized.exists()
    with Image.open(resized) as img:
        assert img.size == (50, 25)


def test_rename_dry_run(tmp_path: Path) -> None:
    original = tmp_path / "hello_test.txt"
    original.write_text("data", encoding="utf-8")

    result = runner.invoke(
        app,
        ["rename", "--path", str(tmp_path), "--find", "test", "--replace", "done", "--dry-run"],
        input="y\n",
    )

    assert result.exit_code == 0
    # Original should still exist (dry run)
    assert original.exists()
    assert not (tmp_path / "hello_done.txt").exists()


def test_filem_dry_run(tmp_path: Path) -> None:
    image = tmp_path / "pic.png"
    doc = tmp_path / "notes.docx"
    image.write_text("img", encoding="utf-8")
    doc.write_text("doc", encoding="utf-8")

    result = runner.invoke(app, ["filem", "--path", str(tmp_path), "--mode", "suffix", "--dry-run"], input="y\n")

    assert result.exit_code == 0
    # Files should still be in original location (dry run)
    assert image.exists()
    assert doc.exists()
    assert not (tmp_path / "Images").exists()


def test_topdf_dry_run(tmp_path: Path) -> None:
    docx_file = tmp_path / "test.docx"
    docx_file.write_text("content", encoding="utf-8")

    result = runner.invoke(app, ["topdf", "--path", str(tmp_path), "--dry-run"], input="y\n")

    assert result.exit_code == 0
    # PDF should not be created (dry run)
    assert not (tmp_path / "test.pdf").exists()


def test_resize_dry_run(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    sample = input_dir / "photo.jpg"
    Image.new("RGB", (100, 50), color=(255, 0, 0)).save(sample)

    result = runner.invoke(
        app,
        [
            "resize",
            "--input",
            str(input_dir),
            "--output",
            str(output_dir),
            "--width",
            "50",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    # Output directory should not be created (dry run)
    assert not output_dir.exists()


def test_file_conversion_result_type() -> None:
    from hsutools.core.types import FileConversionResult

    result = FileConversionResult(path=Path("/tmp/test.docx"), success=True)
    assert result.path == Path("/tmp/test.docx")
    assert result.success is True
    assert result.content_changed is False
    assert result.name_changed is False
    assert result.new_path is None
    assert result.backup_path is None
    assert result.error is None

    full = FileConversionResult(
        path=Path("/tmp/test.docx"),
        success=True,
        content_changed=True,
        name_changed=True,
        new_path=Path("/tmp/test.pdf"),
        backup_path=Path("/tmp/backup/test.docx"),
        error=None,
    )
    assert full.content_changed is True
    assert full.name_changed is True
    assert full.new_path == Path("/tmp/test.pdf")
    assert full.backup_path == Path("/tmp/backup/test.docx")

    r1 = FileConversionResult(path=Path("/a"), success=True)
    r2 = FileConversionResult(path=Path("/a"), success=True)
    assert r1 == r2

    p, s, cc, nc, np, bp, e = full
    assert p == Path("/tmp/test.docx")
    assert s is True
    assert cc is True
    assert nc is True


def test_topdf_recursive_flag(tmp_path: Path) -> None:
    sub = tmp_path / "subdir"
    sub.mkdir()
    (tmp_path / "root.docx").write_text("root", encoding="utf-8")
    (sub / "nested.docx").write_text("nested", encoding="utf-8")

    result = runner.invoke(
        app,
        ["topdf", "--path", str(tmp_path), "--recursive", "--dry-run"],
        input="y\n",
    )

    assert result.exit_code == 0
    assert "root.docx" in result.stdout
    assert "nested.docx" in result.stdout


def test_filem_recursive_flag(tmp_path: Path) -> None:
    sub = tmp_path / "subdir"
    sub.mkdir()
    (tmp_path / "image.png").write_text("img", encoding="utf-8")
    (sub / "nested.png").write_text("nested", encoding="utf-8")

    result = runner.invoke(
        app,
        ["filem", "--path", str(tmp_path), "--mode", "suffix", "--recursive"],
        input="y\n",
    )

    assert result.exit_code == 0
    assert (tmp_path / "Images" / "image.png").exists()
    assert (sub / "Images" / "nested.png").exists()
