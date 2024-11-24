import os
import tkinter as tk

def replace_text_in_directory(file_path, find_text, replace_text, include_folder_name):
    if not file_path.endswith('/'):
        file_path += '/'
    directory = os.path.dirname(file_path)

    files = os.listdir(directory)
    for file_name in files:
        file_path = os.path.join(directory, file_name)

        # 檢查是否要包含資料夾名稱
        if os.path.isfile(file_path) or include_folder_name:
            base_name, extension = os.path.splitext(file_name)
            
            # 加入判斷是否有要取代的文字
            if find_text in base_name:
                new_base_name = base_name.replace(find_text, replace_text)
                new_name = new_base_name + extension

                os.rename(file_path, os.path.join(directory, new_name))
                print(f"檔案 {file_name} 已重新命名為 {new_name}")


def main(path='.'):
    root = tk.Tk()
    root.title("檔案名稱取代工具")

    # 預設檔案路徑為程式執行的目前位置
    os.chdir(path)
    default_file_path = os.getcwd()

    # 建立輸入框和按鈕
    file_path_label = tk.Label(root, text="檔案路徑:")
    file_path_entry = tk.Entry(root)
    file_path_entry.insert(0, default_file_path)  # 將預設值插入輸入框
    find_text_label = tk.Label(root, text="要取代的文字:")
    find_text_entry = tk.Entry(root)
    replace_text_label = tk.Label(root, text="取代後的文字:")
    replace_text_entry = tk.Entry(root)
    include_folder_name_var = tk.BooleanVar()
    include_folder_name_checkbox = tk.Checkbutton(root, text="連同資料夾名稱一起取代", variable=include_folder_name_var)

    # 安排元件位置
    file_path_label.grid(row=0, column=0, sticky="E")
    file_path_entry.grid(row=0, column=1, columnspan=2, sticky="WE", pady=5)
    find_text_label.grid(row=1, column=0, sticky="E")
    find_text_entry.grid(row=1, column=1, columnspan=2, sticky="WE", pady=5)
    replace_text_label.grid(row=2, column=0, sticky="E")
    replace_text_entry.grid(row=2, column=1, columnspan=2, sticky="WE", pady=5)
    include_folder_name_checkbox.grid(row=3, column=1, columnspan=2, sticky="W")

    # 建立按鈕觸發主程式
    def execute_replace():
        file_path = file_path_entry.get()
        find_text = find_text_entry.get()
        replace_text = replace_text_entry.get()
        include_folder_name = include_folder_name_var.get()

        replace_text_in_directory(file_path, find_text, replace_text, include_folder_name)

    execute_button = tk.Button(root, text="執行", command=execute_replace)
    execute_button.grid(row=4, column=0, columnspan=3, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
