from __future__ import annotations

import os
from typing import Dict

ENV_LANG = "HSU_LANG"
DEFAULT_LANG = "en"
SUPPORTED_LANGS = {"en", "zh"}


def _normalize_lang(value: str | None) -> str:
    if not value:
        return DEFAULT_LANG
    lower = value.lower()
    if lower.startswith("zh"):
        return "zh"
    if lower.startswith("en"):
        return "en"
    return DEFAULT_LANG

_current_lang = _normalize_lang(os.getenv(ENV_LANG))


def set_lang(lang: str | None) -> None:
    global _current_lang
    _current_lang = _normalize_lang(lang)


def get_lang() -> str:
    return _current_lang


def tr(key: str, *, lang: str | None = None, **kwargs: object) -> str:
    chosen = lang or _current_lang
    entry = TEXTS.get(key, {})
    template = entry.get(chosen) or entry.get(DEFAULT_LANG) or key
    try:
        return template.format(**kwargs)
    except Exception:
        return template


TEXTS: Dict[str, Dict[str, str]] = {
    "app.help": {
        "en": "hsutools: utilities for paths, renaming, conversions, and image resizing.",
        "zh": "hsutools：檔案路徑、重新命名、轉檔與圖片調整工具。",
    },
    "option.lang": {
        "en": "Interface language (en, zh). Env: HSU_LANG.",
        "zh": "介面語言（en, zh），可用環境變數 HSU_LANG。",
    },
    "option.version": {
        "en": "Show version and exit.",
        "zh": "顯示版本後離開。",
    },
    # cpath
    "cpath.help": {
        "en": "Generate a markdown tree listing for the given directory.",
        "zh": "為指定目錄產生 Markdown 樹狀清單。",
    },
    "cpath.path": {
        "en": "Target directory.",
        "zh": "目標目錄。",
    },
    "cpath.output": {
        "en": "Output markdown file name.",
        "zh": "輸出 Markdown 檔名。",
    },
    "cpath.max_depth": {
        "en": "Limit traversal depth (None for unlimited).",
        "zh": "限制遞迴深度（空值為不限）。",
    },
    "cpath.ignore": {
        "en": "Names to ignore in the tree output.",
        "zh": "樹狀輸出時要忽略的名稱。",
    },
    "cpath.created": {
        "en": "Created {path}",
        "zh": "已建立 {path}",
    },
    # filem
    "filem.help": {
        "en": "Categorize files by date, prefix, or suffix.",
        "zh": "依日期、前綴或副檔名分門別類。",
    },
    "filem.path": {"en": "Directory to manage.", "zh": "要整理的目錄。"},
    "filem.mode": {
        "en": "Grouping strategy: date | prefix | suffix.",
        "zh": "分組策略：date | prefix | suffix。",
    },
    "filem.prefix": {
        "en": "Prefix bucket name when mode=prefix.",
        "zh": "當模式為 prefix 時使用的前綴群組名稱。",
    },
    "filem.ignore": {"en": "Names to ignore.", "zh": "要忽略的名稱。"},
    "filem.include_hidden": {"en": "Include hidden files.", "zh": "包含隱藏檔。"},
    "filem.prompt_mode": {
        "en": "Choose grouping strategy",
        "zh": "選擇分組方式",
    },
    "filem.prompt_prefix": {
        "en": "Enter the prefix to group by (or press Enter to group by each file's prefix)",
        "zh": "輸入要分組的前綴（直接 Enter 則依各檔案前綴分組）",
    },
    "filem.none_found": {
        "en": "No files found to categorize.",
        "zh": "沒有可分類的檔案。",
    },
    "filem.preview": {
        "en": "Found {count} file(s) to categorize in mode: {mode}",
        "zh": "找到 {count} 個檔案，將以 {mode} 模式分類",
    },
    "filem.directory": {"en": "Directory: {path}", "zh": "目錄：{path}"},
    "filem.confirm": {
        "en": "Proceed with file categorization?",
        "zh": "要開始分類檔案嗎？",
    },
    "filem.none_moved": {
        "en": "No files were moved (check ignore filters or mode).",
        "zh": "沒有檔案被移動（請檢查忽略條件或模式）。",
    },
    "filem.success": {
        "en": "Successfully moved {count} files.",
        "zh": "已成功移動 {count} 個檔案。",
    },
    "filem.invalid_mode": {
        "en": "mode must be one of: date, prefix, suffix",
        "zh": "mode 必須是 date、prefix 或 suffix",
    },
    # rename
    "rename.help": {
        "en": "Batch rename file or directory names by replacing text.",
        "zh": "批次以文字取代方式重新命名檔案或資料夾。",
    },
    "rename.path": {"en": "Directory to operate.", "zh": "要操作的目錄。"},
    "rename.find": {"en": "Text to replace.", "zh": "要尋找的文字。"},
    "rename.replace": {"en": "Replacement text.", "zh": "替換文字。"},
    "rename.include_dirs": {"en": "Allow renaming directories as well.", "zh": "允許同時重新命名資料夾。"},
    "rename.ignore": {"en": "Names to ignore.", "zh": "要忽略的名稱。"},
    "rename.include_hidden": {"en": "Include hidden entries.", "zh": "包含隱藏項目。"},
    "rename.prompt_find": {"en": "Enter text to find", "zh": "輸入要尋找的文字"},
    "rename.prompt_replace": {"en": "Enter replacement text", "zh": "輸入替換文字"},
    "rename.none_found": {"en": "No entries found containing '{text}'.", "zh": "找不到包含 '{text}' 的項目。"},
    "rename.preview_header": {
        "en": "Found {count} entry(s) to rename:",
        "zh": "找到 {count} 個待重新命名的項目：",
    },
    "rename.find_replace": {
        "en": "Find: '{find}' → Replace with: '{replace}'",
        "zh": "尋找：'{find}' → 取代為：'{replace}'",
    },
    "rename.more": {"en": "... and {count} more", "zh": "…以及另外 {count} 個"},
    "rename.confirm": {"en": "Proceed with rename?", "zh": "要開始重新命名嗎？"},
    "rename.none_updated": {
        "en": "No entries matched the criteria.",
        "zh": "沒有符合條件的項目。",
    },
    "rename.success": {
        "en": "Successfully renamed {count} entries.",
        "zh": "已成功重新命名 {count} 個項目。",
    },
    # topdf
    "topdf.help": {
        "en": "Convert .docx files in the directory to .pdf using docx2pdf.",
        "zh": "將目錄中的 .docx 轉換為 .pdf（使用 docx2pdf）。",
    },
    "topdf.path": {"en": "Directory containing .docx files.", "zh": "包含 .docx 的目錄。"},
    "topdf.ignore": {"en": "Names to ignore.", "zh": "要忽略的名稱。"},
    "topdf.include_hidden": {"en": "Include hidden files.", "zh": "包含隱藏檔。"},
    "topdf.none": {"en": "No .docx files found to convert.", "zh": "沒有可轉換的 .docx 檔。"},
    "topdf.preview": {"en": "Found {count} .docx file(s) to convert:", "zh": "找到 {count} 個待轉換的 .docx："},
    "topdf.more": {"en": "... and {count} more", "zh": "…以及另外 {count} 個"},
    "topdf.confirm": {"en": "Proceed with conversion?", "zh": "要開始轉換嗎？"},
    "topdf.none_converted": {
        "en": "No .docx files were converted.",
        "zh": "沒有 .docx 被轉換。",
    },
    "topdf.success": {"en": "Successfully converted {count} file(s) to PDF.", "zh": "已成功轉成 PDF：{count} 個檔案。"},
    # resize
    "resize.help": {
        "en": "Resize images with flexible sizing rules.",
        "zh": "以彈性規則調整圖片大小。",
    },
    "resize.input": {"en": "Directory containing images to resize.", "zh": "包含待調整圖片的目錄。"},
    "resize.output": {
        "en": "Directory to write resized images (defaults to INPUT/resized).",
        "zh": "輸出目錄（預設為輸入目錄下的 resized）。",
    },
    "resize.width": {"en": "Target width. Combine with height for bounding box.", "zh": "目標寬度，可與高度組合為邊界框。"},
    "resize.height": {"en": "Target height. Combine with width for bounding box.", "zh": "目標高度，可與寬度組合為邊界框。"},
    "resize.max_width": {"en": "Maximum width cap after other calculations.", "zh": "最終寬度上限。"},
    "resize.max_height": {"en": "Maximum height cap after other calculations.", "zh": "最終高度上限。"},
    "resize.scale": {"en": "Scale factor (e.g., 0.5 halves the size).", "zh": "縮放倍數（如 0.5 代表縮小一半）。"},
    "resize.keep_aspect": {"en": "Preserve aspect ratio when resizing.", "zh": "保持長寬比。"},
    "resize.allow_upscale": {"en": "Permit enlarging images.", "zh": "允許放大。"},
    "resize.quality": {"en": "Quality (1-100) for JPEG/WEBP outputs.", "zh": "JPEG/WEBP 輸出品質（1-100）。"},
    "resize.format": {"en": "Force output format, e.g., jpeg/png/webp.", "zh": "強制輸出格式（例如 jpeg/png/webp）。"},
    "resize.suffix": {"en": "Append suffix before the file extension.", "zh": "在副檔名之前加上後綴。"},
    "resize.overwrite": {"en": "Overwrite if destination exists.", "zh": "若檔案已存在則覆寫。"},
    "resize.recursive": {"en": "Process subdirectories recursively.", "zh": "遞迴處理子目錄。"},
    "resize.include_hidden": {"en": "Include hidden files.", "zh": "包含隱藏檔。"},
    "resize.ignore": {"en": "Names to ignore (applied to files and directories).", "zh": "要忽略的名稱（檔案與資料夾）。"},
    "resize.bad_quality": {"en": "quality must be between 1 and 100", "zh": "quality 必須介於 1 到 100"},
    "resize.need_size": {
        "en": "Provide at least one of width, height, max-width, max-height, or scale",
        "zh": "至少要提供 width、height、max-width、max-height 或 scale 其中之一",
    },
    "resize.none": {"en": "No images were resized (check filters or overwrite settings).", "zh": "沒有圖片被處理（請檢查篩選或覆寫設定）。"},
    "resize.success": {"en": "Resized {count} image(s). Output: {output}", "zh": "已調整 {count} 張圖片。輸出目錄：{output}"},
}
