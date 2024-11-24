import inquirer
import os
from shutil import move

def files_by_date(files:list[str]) -> None:
    from datetime import datetime
    for file in files:
        # 獲取檔案的修改日期
        modification_time = os.path.getmtime(file)
        # 轉換成可讀日期格式
        date = datetime.fromtimestamp(modification_time)
        date_folder = date.strftime("%m%d")  # m/d 格式
        
        if not os.path.exists(date_folder):
            os.makedirs(date_folder)
        
        move(file, os.path.join(date_folder, file))

def files_by_before(files: list[str]) -> None:
    correct = inquirer.confirm("是否自定義前綴的分類? ", default=False)
    prefix = ""
    if correct:
        prefix = input("請輸入前綴: ")

    for file in files:
        if prefix != '' and file.startswith(prefix):
            before = prefix
        else:
            before = file.split('.')[0]
        
        if not os.path.exists(before):
            os.mkdir(before)
        
        move(file, os.path.join(before, file))

def files_by_after(files:list[str]) -> None:
    # 定義檔案擴展名和對應的類別
    file_extensions = {
        'pdf': 'PDF文件',
        'png': '圖片', 'jpg': '圖片', 'jpeg': '圖片','jfif': '圖片', 'gif': '圖片','tif': '圖片','tiff': '圖片','webp': '圖片',
        'doc': 'Docs文件', 'docx': 'Docs文件','csv': 'Docs文件',
        'xlsx': '試算表',
        'pptx': '簡報',
        'ini': '設定檔',
        'txt': '文字檔', 'srt': '文字檔',
        'zip': '壓縮檔', 'rar': '壓縮檔','7z': '壓縮檔',
        'exe': '執行檔',
        'wav': '音訊', 'mp3': '音訊', 'flac': '音訊','weba': '音訊','wma': '音訊','m4a': '音訊','m4b': '音訊',
        'mp4': '影片', 'avi': '影片','flv': '影片', 'wmv': '影片', 'webm': '影片','ogg': '影片','mov': '影片','m4v': '影片',
        'ai': 'Illustrator','svg': 'Illustrator',
        'psd': 'Photoshop',
    }

    for file in files:
        extension = file.split('.')[-1].lower()
        folder = file_extensions.get(extension, False)

        if folder :
            if not os.path.exists(folder):
                os.mkdir(folder)
            move(file, folder)

def main(path="."):
    from tabulate import tabulate

    # 選擇類型
    questions = [
        inquirer.List('choice',message="檔案管理? 依照什麼類型呢?",choices=['日期','前綴', '後綴'],),
    ]

    answers = inquirer.prompt(questions)
    choice = answers['choice'].lower()

    dir_path = os.path.abspath(path)
    os.chdir(dir_path)

    # 請選擇要忽略的檔案
    files = [f for f in os.listdir() if os.path.isfile(f)]
    questions = [
        inquirer.Checkbox('options', message="請選擇要忽略的檔案:",choices=files),
    ]

    answers = inquirer.prompt(questions)
    ignore_files = answers['options']

    # 取得檔案

    files = sorted([f for f in os.listdir() if os.path.isfile(f) and f not in ignore_files])
    print(tabulate([[f,os.path.splitext(f)[1]] for f in files], headers=['檔案名稱','檔案類型'], tablefmt='orgtbl'))
    checkDo = inquirer.confirm("確定執行? ", default=True)
    
    if checkDo and os.path.isdir(dir_path):
        if choice == "日期":
            files_by_date(files)
        elif choice == "前綴":
            files_by_before(files)
        elif choice == "後綴":
            files_by_after(files)
        else:
            print("error")
        print('檔案整理完成！')
    else:
        print('沒有檔案')
    

if __name__ == "__main__":
    main()
