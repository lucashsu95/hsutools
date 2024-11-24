import argparse

def run_create_path(path):
    from create_path.main import main as create_path_main
    create_path_main(path)

def run_file_manage(path):
    from file_manage.main import main as file_manage_main
    file_manage_main(path)

def run_file_renamer(path):
    from file_renamer.main import main as file_renamer_main
    file_renamer_main(path)

def run_docx_to_pdf(path):
    from docxToPdf.main import main as docx_to_pdf_main
    docx_to_pdf_main(path)

def main():
    parser:argparse.ArgumentParser = argparse.ArgumentParser(description="hsutools 命令行工具")
    parser.add_argument("command")
    parser.add_argument("--path", type=str, default=".", help="要操作的目錄")
    
    subparsers = parser.add_subparsers(dest="command")

    # # cpath command
    subparsers.add_parser("cpath", help="創建路徑到demo.md")

    # # filem command
    subparsers.add_parser("filem", help="分類檔案，可以依照(日期、前綴、後綴)做分類")

    # # rename command
    subparsers.add_parser("rename", help="檔案重新命名")

    # # docxToPdf command
    subparsers.add_parser("topdf", help="將docx轉換為pdf")

    args = parser.parse_args()

    command = args.command
    path = args.path
    print(f'path: {path}')

    if command == "cpath":
        run_create_path(path)
    elif command == "filem":
        run_file_manage(path)
    elif command == "rename":
        run_file_renamer(path)
    elif command == "topdf":
        run_docx_to_pdf(path)
    else:
        print(f"未知的功能: {command}")

if __name__ == "__main__":
    main()