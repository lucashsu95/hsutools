"""Core features for hsutools."""

from .create_path import generate_path_md
from .docx_to_pdf import check_docx2pdf_available, convert_docx_directory
from .file_manage import categorize_files
from .file_renamer import replace_names
from .image_resize import resize_images
from .s2tw import convert_s2tw_recursive, check_opencc_available, ConversionStats
from .types import FileConversionResult, FileOperationResult, OperationStats

__all__ = [
    "categorize_files",
    "check_docx2pdf_available",
    "check_opencc_available",
    "convert_docx_directory",
    "convert_s2tw_recursive",
    "ConversionStats",
    "FileConversionResult",
    "FileOperationResult",
    "generate_path_md",
    "OperationStats",
    "resize_images",
    "replace_names",
]
