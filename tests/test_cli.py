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
    )

    assert result.exit_code == 0
    assert not original.exists()
    assert (tmp_path / "hello_done.txt").exists()


def test_filem_suffix(tmp_path: Path) -> None:
    image = tmp_path / "pic.png"
    doc = tmp_path / "notes.docx"
    image.write_text("img", encoding="utf-8")
    doc.write_text("doc", encoding="utf-8")

    result = runner.invoke(app, ["filem", "--path", str(tmp_path), "--mode", "suffix"])

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
