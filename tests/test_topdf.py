"""Unit tests for docx_to_pdf (DOCX → PDF conversion)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write(path: Path, content: str = "") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# convert_docx_directory
# ---------------------------------------------------------------------------

class TestConvertDocxDirectory:
    @patch("hsutools.core.docx_to_pdf.convert")
    def test_converts_all_docx_files(self, mock_convert: MagicMock, tmp_path: Path):
        from hsutools.core.docx_to_pdf import convert_docx_directory

        _write(tmp_path / "a.docx", "A")
        _write(tmp_path / "b.docx", "B")
        _write(tmp_path / "c.txt", "skip")

        result = convert_docx_directory(tmp_path)

        assert len(result) == 2
        assert all(p.suffix == ".pdf" for p in result)
        assert mock_convert.call_count == 2

    @patch("hsutools.core.docx_to_pdf.convert")
    def test_returns_empty_when_no_docx(self, mock_convert: MagicMock, tmp_path: Path):
        from hsutools.core.docx_to_pdf import convert_docx_directory

        _write(tmp_path / "notes.txt", "no docx here")

        result = convert_docx_directory(tmp_path)

        assert result == []
        mock_convert.assert_not_called()

    @patch("hsutools.core.docx_to_pdf.convert")
    def test_ignores_hidden_files(self, mock_convert: MagicMock, tmp_path: Path):
        from hsutools.core.docx_to_pdf import convert_docx_directory

        _write(tmp_path / "visible.docx")
        _write(tmp_path / ".hidden.docx")

        result = convert_docx_directory(tmp_path, include_hidden=False)

        assert len(result) == 1
        mock_convert.assert_called_once()

    @patch("hsutools.core.docx_to_pdf.convert")
    def test_includes_hidden_when_flagged(self, mock_convert: MagicMock, tmp_path: Path):
        from hsutools.core.docx_to_pdf import convert_docx_directory

        _write(tmp_path / ".secret.docx")

        result = convert_docx_directory(tmp_path, include_hidden=True)

        assert len(result) == 1
        mock_convert.assert_called_once()

    @patch("hsutools.core.docx_to_pdf.convert")
    def test_ignore_names_excludes_files(self, mock_convert: MagicMock, tmp_path: Path):
        from hsutools.core.docx_to_pdf import convert_docx_directory

        _write(tmp_path / "keep.docx")
        _write(tmp_path / "skip.docx")

        result = convert_docx_directory(tmp_path, ignore_names=["skip.docx"])

        assert len(result) == 1
        assert "skip.pdf" not in [str(p) for p in result]

    @patch("hsutools.core.docx_to_pdf.convert")
    def test_output_path_matches_input(self, mock_convert: MagicMock, tmp_path: Path):
        from hsutools.core.docx_to_pdf import convert_docx_directory

        docx = _write(tmp_path / "report.docx")

        result = convert_docx_directory(tmp_path)

        assert len(result) == 1
        assert result[0] == tmp_path / "report.pdf"

    @patch("hsutools.core.docx_to_pdf.convert")
    def test_empty_directory(self, mock_convert: MagicMock, tmp_path: Path):
        from hsutools.core.docx_to_pdf import convert_docx_directory

        result = convert_docx_directory(tmp_path)

        assert result == []
        mock_convert.assert_not_called()

    @patch("hsutools.core.docx_to_pdf.convert")
    def test_subdirectories_not_scanned(self, mock_convert: MagicMock, tmp_path: Path):
        """convert_docx_directory uses iter_files which does not recurse."""
        from hsutools.core.docx_to_pdf import convert_docx_directory

        sub = tmp_path / "subdir"
        sub.mkdir()
        _write(sub / "nested.docx")

        result = convert_docx_directory(tmp_path)

        assert len(result) == 0
        mock_convert.assert_not_called()


# ---------------------------------------------------------------------------
# CLI integration
# ---------------------------------------------------------------------------

class TestTopdfCli:
    @patch("hsutools.core.docx_to_pdf.convert")
    def test_topdf_no_files_message(self, mock_convert: MagicMock, tmp_path: Path):
        from typer.testing import CliRunner
        from hsutools.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["topdf", "--path", str(tmp_path)])

        assert result.exit_code == 0
        assert "No .docx" in result.stdout

    @patch("hsutools.core.docx_to_pdf.convert")
    def test_topdf_converts_with_confirmation(self, mock_convert: MagicMock, tmp_path: Path):
        from typer.testing import CliRunner
        from hsutools.cli import app

        _write(tmp_path / "doc.docx")

        runner = CliRunner()
        result = runner.invoke(
            app,
            ["topdf", "--path", str(tmp_path)],
            input="y\n",
        )

        assert result.exit_code == 0
        mock_convert.assert_called_once()

    @patch("hsutools.core.docx_to_pdf.convert")
    def test_topdf_cancelled_by_user(self, mock_convert: MagicMock, tmp_path: Path):
        from typer.testing import CliRunner
        from hsutools.cli import app

        _write(tmp_path / "doc.docx")

        runner = CliRunner()
        result = runner.invoke(
            app,
            ["topdf", "--path", str(tmp_path)],
            input="n\n",
        )

        assert result.exit_code == 0
        assert "cancelled" in result.stdout.lower() or "Operation" in result.stdout
        mock_convert.assert_not_called()

    @patch("hsutools.core.docx_to_pdf.convert")
    def test_topdf_with_ignore(self, mock_convert: MagicMock, tmp_path: Path):
        from typer.testing import CliRunner
        from hsutools.cli import app

        _write(tmp_path / "keep.docx")
        _write(tmp_path / "skip.docx")

        runner = CliRunner()
        result = runner.invoke(
            app,
            ["topdf", "--path", str(tmp_path), "--ignore", "skip.docx"],
            input="y\n",
        )

        assert result.exit_code == 0
        assert mock_convert.call_count == 1

    @patch("hsutools.cli.check_docx2pdf_available", return_value=False)
    def test_topdf_fails_without_docx2pdf(self, mock_check, tmp_path: Path):
        from typer.testing import CliRunner
        from hsutools.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["topdf", "--path", str(tmp_path)])

        assert result.exit_code == 1
        assert "docx2pdf" in result.stdout.lower() or "docx2pdf" in result.stdout
