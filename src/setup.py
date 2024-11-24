import os
import shutil
import time

source_file = "hsu.exe"
destination_file = os.path.join("C:\\Windows", "hsu.exe")

try:
    shutil.copy(source_file, destination_file)
    print(f"安裝成功！")
    time.sleep(2)
except PermissionError as e:
    print("安裝失敗！權限不足，請以系統管理員身份運行此程式！")
    time.sleep(5)
except Exception as e:
    print(f"安裝失敗！{e}")
    time.sleep(5)
