"""Unit tests for s2tw (Simplified to Traditional Chinese conversion)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


def _write(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def _make_fake_opencc():
    fake_map = {
        "简": "簡", "体": "體", "中": "中", "文": "文",
        "件": "件", "档": "檔", "软": "軟體", "转": "轉",
        "换": "換", "录": "錄", "实": "實", "验": "驗",
        "内": "內",
    }

    def convert(text: str) -> str:
        for s, t in fake_map.items():
            text = text.replace(s, t)
        return text

    mock = MagicMock()
    mock.convert = convert
    return mock


def _inject_opencc(s2tw_module, fake_cc):
    s2tw_module.OpenCC = lambda profile="s2twp": fake_cc


# ---------------------------------------------------------------------------
# check_opencc_available
# ---------------------------------------------------------------------------

class TestCheckOpenccAvailable:
    @patch("hsutools.core.s2tw.HAS_OPENCC", True)
    def test_returns_true_when_installed(self):
        from hsutools.core.s2tw import check_opencc_available
        assert check_opencc_available() is True

    @patch("hsutools.core.s2tw.HAS_OPENCC", False)
    def test_returns_false_when_missing(self):
        from hsutools.core.s2tw import check_opencc_available
        assert check_opencc_available() is False


# ---------------------------------------------------------------------------
# convert_text_s2tw
# ---------------------------------------------------------------------------

class TestConvertTextS2tw:
    @patch("hsutools.core.s2tw.HAS_OPENCC", True)
    def test_converts_text(self):
        from hsutools.core.s2tw import convert_text_s2tw
        fake_cc = _make_fake_opencc()
        result = convert_text_s2tw("简体中文", converter=fake_cc)
        assert result == "簡體中文"

    @patch("hsutools.core.s2tw.HAS_OPENCC", False)
    def test_raises_when_opencc_missing(self):
        from hsutools.core.s2tw import convert_text_s2tw
        with pytest.raises(ImportError, match="OpenCC is not installed"):
            convert_text_s2tw("test")

    @patch("hsutools.core.s2tw.HAS_OPENCC", True)
    def test_unaffected_text_unchanged(self):
        from hsutools.core.s2tw import convert_text_s2tw
        fake_cc = _make_fake_opencc()
        result = convert_text_s2tw("Hello World 123", converter=fake_cc)
        assert result == "Hello World 123"


# ---------------------------------------------------------------------------
# create_backup
# ---------------------------------------------------------------------------

class TestCreateBackup:
    def test_backup_in_same_dir(self, tmp_path: Path):
        from hsutools.core.s2tw import create_backup
        src = _write(tmp_path / "data.md", "content")
        backup = create_backup(src)
        assert backup.exists()
        assert backup.read_text(encoding="utf-8") == "content"
        assert backup.name == "data.md.backup"

    def test_backup_in_custom_dir(self, tmp_path: Path):
        from hsutools.core.s2tw import create_backup
        src = _write(tmp_path / "data.md", "content")
        bdir = tmp_path / "backups"
        backup = create_backup(src, backup_dir=bdir)
        assert backup.parent == bdir
        assert backup.exists()

    def test_backup_appends_timestamp_on_collision(self, tmp_path: Path):
        from hsutools.core.s2tw import create_backup
        src = _write(tmp_path / "data.md", "v1")
        b1 = create_backup(src)
        assert b1.name == "data.md.backup"
        src.write_text("v2", encoding="utf-8")
        b2 = create_backup(src)
        assert b2 != b1
        assert "_20" in b2.name


# ---------------------------------------------------------------------------
# convert_file_content
# ---------------------------------------------------------------------------

class TestConvertFileContent:
    @patch("hsutools.core.s2tw.HAS_OPENCC", True)
    def test_converts_and_creates_backup(self, tmp_path: Path):
        from hsutools.core.s2tw import convert_file_content
        src = _write(tmp_path / "doc.md", "简体内容")
        fake_cc = _make_fake_opencc()
        result = convert_file_content(src, fake_cc, create_backup_file=True)
        assert result.content_changed is True
        assert result.backup_path is not None
        assert result.backup_path.exists()
        assert src.read_text(encoding="utf-8") == "簡體內容"

    @patch("hsutools.core.s2tw.HAS_OPENCC", True)
    def test_no_change_returns_false(self, tmp_path: Path):
        from hsutools.core.s2tw import convert_file_content
        src = _write(tmp_path / "doc.md", "already traditional")
        fake_cc = MagicMock()
        fake_cc.convert = lambda t: t
        result = convert_file_content(src, fake_cc, create_backup_file=True)
        assert result.content_changed is False
        assert result.backup_path is None

    @patch("hsutools.core.s2tw.HAS_OPENCC", False)
    def test_returns_error_when_opencc_missing(self, tmp_path: Path):
        from hsutools.core.s2tw import convert_file_content
        src = _write(tmp_path / "doc.md", "test")
        result = convert_file_content(src)
        assert result.error == "OpenCC is not installed"
        assert result.content_changed is False

    @patch("hsutools.core.s2tw.HAS_OPENCC", True)
    def test_no_backup_when_disabled(self, tmp_path: Path):
        from hsutools.core.s2tw import convert_file_content
        src = _write(tmp_path / "doc.md", "简体")
        fake_cc = _make_fake_opencc()
        result = convert_file_content(src, fake_cc, create_backup_file=False)
        assert result.content_changed is True
        assert result.backup_path is None


# ---------------------------------------------------------------------------
# convert_name
# ---------------------------------------------------------------------------

class TestConvertName:
    @patch("hsutools.core.s2tw.HAS_OPENCC", True)
    def test_converts_filename(self):
        from hsutools.core.s2tw import convert_name
        fake_cc = _make_fake_opencc()
        assert convert_name("简体文件.txt", fake_cc) == "簡體文件.txt"

    @patch("hsutools.core.s2tw.HAS_OPENCC", False)
    def test_returns_original_when_opencc_missing(self):
        from hsutools.core.s2tw import convert_name
        assert convert_name("test.txt") == "test.txt"

    @patch("hsutools.core.s2tw.HAS_OPENCC", True)
    def test_pure_ascii_unchanged(self):
        from hsutools.core.s2tw import convert_name
        fake_cc = _make_fake_opencc()
        assert convert_name("readme.md", fake_cc) == "readme.md"


# ---------------------------------------------------------------------------
# convert_s2tw_recursive
# ---------------------------------------------------------------------------

class TestConvertS2twRecursive:
    @patch("hsutools.core.s2tw.HAS_OPENCC", True)
    def test_single_file_conversion(self, tmp_path: Path):
        import hsutools.core.s2tw as s2tw_mod
        from hsutools.core.s2tw import convert_s2tw_recursive, ConversionResult
        src = _write(tmp_path / "doc.md", "简体内容")
        fake_cc = _make_fake_opencc()
        _inject_opencc(s2tw_mod, fake_cc)
        results, stats = convert_s2tw_recursive(
            src, extensions={".md"}, create_backup_files=False
        )
        assert stats.files_content_modified == 1
        assert stats.errors == 0

    @patch("hsutools.core.s2tw.HAS_OPENCC", True)
    def test_directory_conversion(self, tmp_path: Path):
        import hsutools.core.s2tw as s2tw_mod
        from hsutools.core.s2tw import convert_s2tw_recursive
        _write(tmp_path / "a.md", "简体A")
        _write(tmp_path / "b.md", "简体B")
        _write(tmp_path / "skip.txt", "should not convert")
        fake_cc = _make_fake_opencc()
        _inject_opencc(s2tw_mod, fake_cc)
        results, stats = convert_s2tw_recursive(
            tmp_path, extensions={".md"}, create_backup_files=False
        )
        assert stats.files_content_modified == 2

    @patch("hsutools.core.s2tw.HAS_OPENCC", True)
    def test_name_conversion_renames_files(self, tmp_path: Path):
        import hsutools.core.s2tw as s2tw_mod
        from hsutools.core.s2tw import convert_s2tw_recursive
        src = _write(tmp_path / "简体.md", "content")
        fake_cc = _make_fake_opencc()
        _inject_opencc(s2tw_mod, fake_cc)
        results, stats = convert_s2tw_recursive(
            tmp_path, extensions={".md"}, convert_names=True, create_backup_files=False
        )
        assert stats.files_renamed >= 1
        assert not src.exists()
        assert (tmp_path / "簡體.md").exists()

    @patch("hsutools.core.s2tw.HAS_OPENCC", True)
    def test_ignore_names_excludes(self, tmp_path: Path):
        import hsutools.core.s2tw as s2tw_mod
        from hsutools.core.s2tw import convert_s2tw_recursive
        _write(tmp_path / "keep.md", "简体")
        _write(tmp_path / "skip.md", "简体")
        fake_cc = _make_fake_opencc()
        _inject_opencc(s2tw_mod, fake_cc)
        results, stats = convert_s2tw_recursive(
            tmp_path, extensions={".md"}, ignore_names=["skip.md"],
            create_backup_files=False,
        )
        assert stats.files_content_modified == 1

    @patch("hsutools.core.s2tw.HAS_OPENCC", True)
    def test_hidden_files_excluded_by_default(self, tmp_path: Path):
        import hsutools.core.s2tw as s2tw_mod
        from hsutools.core.s2tw import convert_s2tw_recursive
        _write(tmp_path / "visible.md", "简体")
        _write(tmp_path / ".hidden.md", "简体")
        fake_cc = _make_fake_opencc()
        _inject_opencc(s2tw_mod, fake_cc)
        results, stats = convert_s2tw_recursive(
            tmp_path, extensions={".md"}, create_backup_files=False
        )
        assert stats.files_content_modified == 1

    @patch("hsutools.core.s2tw.HAS_OPENCC", True)
    def test_hidden_files_included_when_flagged(self, tmp_path: Path):
        import hsutools.core.s2tw as s2tw_mod
        from hsutools.core.s2tw import convert_s2tw_recursive
        _write(tmp_path / ".hidden.md", "简体")
        fake_cc = _make_fake_opencc()
        _inject_opencc(s2tw_mod, fake_cc)
        results, stats = convert_s2tw_recursive(
            tmp_path, extensions={".md"}, include_hidden=True,
            create_backup_files=False,
        )
        assert stats.files_content_modified == 1

    @patch("hsutools.core.s2tw.HAS_OPENCC", False)
    def test_raises_when_opencc_missing(self, tmp_path: Path):
        from hsutools.core.s2tw import convert_s2tw_recursive
        with pytest.raises(ImportError, match="OpenCC is not installed"):
            convert_s2tw_recursive(tmp_path)

    @patch("hsutools.core.s2tw.HAS_OPENCC", True)
    def test_backup_files_created(self, tmp_path: Path):
        import hsutools.core.s2tw as s2tw_mod
        from hsutools.core.s2tw import convert_s2tw_recursive
        _write(tmp_path / "doc.md", "简体")
        fake_cc = _make_fake_opencc()
        _inject_opencc(s2tw_mod, fake_cc)
        results, stats = convert_s2tw_recursive(
            tmp_path, extensions={".md"}, create_backup_files=True
        )
        assert stats.files_backed_up == 1
        assert (tmp_path / "doc.md.backup").exists()

    @patch("hsutools.core.s2tw.HAS_OPENCC", True)
    def test_dirname_conversion(self, tmp_path: Path):
        import hsutools.core.s2tw as s2tw_mod
        from hsutools.core.s2tw import convert_s2tw_recursive
        sub = tmp_path / "简体目录"
        sub.mkdir()
        _write(sub / "doc.md", "content")
        fake_cc = _make_fake_opencc()
        _inject_opencc(s2tw_mod, fake_cc)
        results, stats = convert_s2tw_recursive(
            tmp_path, extensions={".md"}, convert_names=True, create_backup_files=False
        )
        assert stats.dirs_renamed >= 1
        assert (tmp_path / "簡體目錄").exists()


# ---------------------------------------------------------------------------
# CLI integration
# ---------------------------------------------------------------------------

class TestS2twCli:
    @patch("hsutools.core.s2tw.HAS_OPENCC", False)
    def test_s2tw_fails_without_opencc(self, tmp_path: Path):
        from typer.testing import CliRunner
        from hsutools.cli import app
        runner = CliRunner()
        result = runner.invoke(app, ["s2tw", "--path", str(tmp_path)])
        assert result.exit_code == 1
        assert "OpenCC" in result.stdout or "opencc" in result.stdout.lower()

    @patch("hsutools.cli.check_opencc_available", return_value=True)
    def test_s2tw_converts_files(self, mock_check, tmp_path: Path):
        from typer.testing import CliRunner
        from hsutools.cli import app
        _write(tmp_path / "doc.md", "简体内容")
        with patch("hsutools.cli.convert_s2tw_recursive") as mock_conv:
            mock_conv.return_value = (
                [],
                MagicMock(
                    files_content_modified=1,
                    files_renamed=0,
                    dirs_renamed=0,
                    files_backed_up=0,
                    errors=0,
                ),
            )
            runner = CliRunner()
            result = runner.invoke(
                app,
                ["s2tw", "--path", str(tmp_path), "--no-backup"],
                input="y\n",
            )
            assert result.exit_code == 0
            mock_conv.assert_called_once()
