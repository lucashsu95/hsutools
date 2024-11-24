# hsutools

## How to Start ?

1. 下載後用**以系統管理員身份執行**`setup.exe`檔
2. 就可以把資料夾刪除了
3. 到需要使用的地方下指令(ex:hsutools mfile)

## Introduce

### create_path

這個Python腳本的功能是讀取指定資料夾的結構，並生成一個包含目錄信息的demo.md文件。具體而言，它執行以下操作：

1. 使用深度優先搜索 (DFS) 遍歷資料夾結構。
2. 對於每個資料夾，生成一個以"第{章節編號}章"為標題的段落，後接資料夾名稱。
3. 對於每個檔案，生成以"{章節編號}-{檔案編號}"為標題的條目，後接檔案名稱和相對路徑。
4. 在demo.md文件中按深度遞增的順序列出所有檔案和資料夾。

這樣的demo文件可用於清晰地展示資料夾結構，以方便他人了解和瀏覽。為了實現這一目的，腳本通過將空格替換為'%20'並將反斜線替換為斜線，以生成相對於根目錄的檔案路徑。

你可以運行這個腳本，它將生成一個名為demo.md的文件，該文件包含整理過的目錄結構。

### file_manage
這一個用python做的簡單的檔案分類器

## Feature

可以依照**修改日期**、**檔案名稱**、**檔案的副檔名**生成資料夾，再把檔案放進資料夾

其中檔案名稱還可以自定義想要的前綴

## Build

```shell
.venv\Scripts\activate
pip install -r requirements.txt
```

```shell
python src/build.py
```

儲存到`requirements.txt`
```shell
pip freeze > requirements.txt
```