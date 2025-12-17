from pathlib import Path

APP_NAME = "hsu"
DEFAULT_OUTPUT_FILE = "path.md"
DEFAULT_IGNORE_NAMES = {".git", "README.md", "path.md", "__pycache__"}
DOCX_EXTENSION = ".docx"
PACKAGE_ROOT = Path(__file__).resolve().parent
PYINSTALLER_DEFAULT_OPTS = ["-F", "-n", APP_NAME]

FILE_SUFFIX_BUCKETS = {
    "pdf": "PDF_files",
    "png": "Images",
    "jpg": "Images",
    "jpeg": "Images",
    "jfif": "Images",
    "gif": "Images",
    "tif": "Images",
    "tiff": "Images",
    "webp": "Images",
    "doc": "Docs",
    "docx": "Docs",
    "csv": "Docs",
    "xlsx": "Spreadsheets",
    "pptx": "Presentations",
    "ini": "Configs",
    "txt": "Texts",
    "srt": "Texts",
    "zip": "Archives",
    "rar": "Archives",
    "7z": "Archives",
    "exe": "Executables",
    "wav": "Audio",
    "mp3": "Audio",
    "flac": "Audio",
    "weba": "Audio",
    "wma": "Audio",
    "m4a": "Audio",
    "m4b": "Audio",
    "mp4": "Videos",
    "avi": "Videos",
    "flv": "Videos",
    "wmv": "Videos",
    "webm": "Videos",
    "ogg": "Videos",
    "mov": "Videos",
    "m4v": "Videos",
    "ai": "Illustrator",
    "svg": "Illustrator",
    "psd": "Photoshop",
}
