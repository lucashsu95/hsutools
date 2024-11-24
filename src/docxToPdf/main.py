import os
from docx2pdf import convert

def convert_docx_to_pdf(docx_files: list[str]) -> None:
    
    if not docx_files:
        print('目錄中沒有找到 .docx 文件')
        return
    
    for docx_file in docx_files:
        docx_path = os.path.join('.', docx_file)
        pdf_path = os.path.splitext(docx_path)[0] + ".pdf"
        
        convert(docx_path, pdf_path)
        print(f"已轉換：{docx_file} -> {pdf_path}")

def main(path):
    from tabulate import tabulate
    import inquirer

    os.chdir(path)

    # 請選擇要忽略的檔案
    files = [f for f in os.listdir() if os.path.isfile(f) and f.endswith('.docx')]
    questions = [
        inquirer.Checkbox('options', message="請選擇要忽略的檔案:",choices=files),
    ]

    answers = inquirer.prompt(questions)
    ignore_files = answers['options']

    # 取得檔案
    dir_path = os.getcwd()
    docx_files = sorted([f for f in os.listdir() if os.path.isfile(f) and f.endswith('.docx') and f not in ignore_files])
    print(tabulate([[f,os.path.splitext(f)[1]] for f in docx_files], headers=['檔案名稱','檔案類型'], tablefmt='orgtbl'))
    checkDo = inquirer.confirm("確定執行? ", default=True)
    
    if checkDo and os.path.isdir(dir_path):
        convert_docx_to_pdf(docx_files)
    else:
        print('沒有檔案')
    

if __name__ == "__main__":
    main()