from pathlib import Path

APP_NAME = "hsu"
DEFAULT_OUTPUT_FILE = "path.md"
DEFAULT_IGNORE_NAMES = {".git", "README.md", "path.md", "__pycache__"}
DOCX_EXTENSION = ".docx"
PACKAGE_ROOT = Path(__file__).resolve().parent
PYINSTALLER_DEFAULT_OPTS = ["-F", "-n", APP_NAME]

FILE_SUFFIX_BUCKETS = {
    "png": "Images",
    "jpg": "Images",
    "jpeg": "Images",
    "jfif": "Images",
    "gif": "Images",
    "tif": "Images",
    "tiff": "Images",
    "webp": "Images",
    "bmp": "Images",
    "ico": "Images",
    "heic": "Images",
    "raw": "Images",
    "cr2": "Images",
    "nef": "Images",

    # --- 文件 (Docs) ---
    "pdf": "PDF_files",
    "doc": "Docs",
    "docx": "Docs",
    "rtf": "Docs",
    "odt": "Docs",
    "pages": "Docs",
    "md": "Docs",
    
    # --- 試算表 (Spreadsheets) ---
    "xlsx": "Spreadsheets",
    "xls": "Spreadsheets",
    "csv": "Spreadsheets",
    "ods": "Spreadsheets",
    "numbers": "Spreadsheets",

    # --- 簡報 (Presentations) ---
    "pptx": "Presentations",
    "ppt": "Presentations",
    "odp": "Presentations",
    "key": "Presentations",

    # --- 文字與設定 (Texts / Configs) ---
    "txt": "Texts",
    "srt": "Texts",
    "vtt": "Texts",      
    "log": "Texts",      
    "ini": "Configs",
    "cfg": "Configs",   
    "conf": "Configs",  
    "env": "Configs",   

    # --- 程式碼與資料 (Code & Data) - 新增類別 ---
    "py": "Code",
    "js": "Code",
    "html": "Code",
    "css": "Code",
    "java": "Code",
    "c": "Code",
    "cpp": "Code",
    "h": "Code",
    "cs": "Code",
    "php": "Code",
    "ts": "Code",
    "go": "Code",
    "rs": "Code",
    "swift": "Code",
    "kt": "Code",
    "json": "Data_Files",
    "xml": "Data_Files",
    "yaml": "Data_Files",
    "yml": "Data_Files",
    "sql": "Data_Files",
    "db": "Data_Files",

    # --- 壓縮檔 (Archives) ---
    "zip": "Archives",
    "rar": "Archives",
    "7z": "Archives",
    "tar": "Archives",
    "gz": "Archives",
    "bz2": "Archives",
    "iso": "Archives",
    "dmg": "Archives",

    # --- 執行檔 (Executables) ---
    "exe": "Executables",
    "msi": "Executables",
    "bat": "Executables",
    "sh": "Executables",
    "app": "Executables",
    "apk": "Executables",
    
    # --- 音訊 (Audio) ---
    "wav": "Audio",
    "mp3": "Audio",
    "flac": "Audio",
    "weba": "Audio",
    "wma": "Audio",
    "m4a": "Audio",
    "m4b": "Audio",
    "aac": "Audio",       
    "ogg": "Audio",       
    "aiff": "Audio",      

    # --- 影片 (Videos) ---
    "mp4": "Videos",
    "avi": "Videos",
    "flv": "Videos",
    "wmv": "Videos",
    "webm": "Videos",
    # "ogg": "Videos",    # 註: ogg 通常是音訊，ogv 才是影片，這裡避免重複鍵值衝突
    "ogv": "Videos",
    "mov": "Videos",
    "m4v": "Videos",
    "mkv": "Videos",
    "3gp": "Videos",
    "ts": "Videos",

    # --- 設計與繪圖 (Design) ---
    "ai": "Illustrator",
    "eps": "Illustrator",
    "svg": "Illustrator",
    "psd": "Photoshop",
    "indd": "InDesign",
    "cdr": "CorelDraw",
    "sketch": "Design",
    "fig": "Design",

    # --- 字型 (Fonts) - 新增類別 ---
    "ttf": "Fonts",
    "otf": "Fonts",
    "woff": "Fonts",
    "woff2": "Fonts",

    # --- 3D 模型 (3D_Models) - 新增類別 ---
    "stl": "3D_Models",
    "obj": "3D_Models",
    "fbx": "3D_Models",
    "blend": "3D_Models",

    # --- 電子書 (E-Books) - 新增類別 ---
    "epub": "E-Books",
    "mobi": "E-Books",
    "azw3": "E-Books",
}