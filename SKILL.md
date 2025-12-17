# SKILL: 專案現代化與打包流程

> 目標：將散落腳本重整為標準 Python package，採 Typer CLI 與 Poetry 依賴管理，支援 pipx 安裝與可選 PyInstaller 打包。

## 工作步驟
1) **盤點現況**：閱讀 README、requirements、主要腳本，確認已有子功能與交互方式。
2) **設計結構**：採用 `src/hsutools` 佈局，建立 `cli.py`(Typer 入口)、`config.py`(常數/預設值)、`utils.py`(共用輔助)、`core/`(各子功能模組)。
3) **遷移邏輯**：將舊 `create_path`, `file_manage`, `file_renamer`, `docxToPdf` 的邏輯封裝為可測函式，減少全域副作用，保留原功能意圖。
4) **CLI 改寫**：使用 Typer 建立子命令 (`cpath`, `filem`, `rename`, `topdf`)，提供型別標註、選項預設值、說明文字與確認流程。
5) **依賴與打包**：以 Poetry 管理依賴，設定 `tool.poetry.scripts` 暴露 `hsu` 指令；加入可選 PyInstaller 助手命令作為自動化打包的入口。
6) **文件更新**：更新 README，說明安裝 (poetry/pipx)、基本用法與打包方式；移除過時檔案說明。
7) **測試與自檢**：撰寫/更新基本測試（至少覆蓋 CLI 匯入），檢查目標清單 (見下方)，確保步驟可重複。

## 自檢清單（全部需通過）
- **專案結構標準化**：採 `src/hsutools` 佈局，含 `__init__.py`、`cli.py`、`core/`；舊的頂層 `main.py/build.py/setup.py` 已淘汰或標記為不再使用。
- **現代 CLI**：主入口使用 Typer，所有子命令透過 Typer 命令/選項管理，提供說明與型別。
- **依賴管理與打包**：存在 `pyproject.toml` (Poetry)，記錄依賴與 `tool.poetry.scripts`；提供 `poetry build` 指令說明。
- **自動化打包**：提供 PyInstaller 打包流程（例如 Typer 子命令或 helper），並在 README 說明如何從 Poetry 環境觸發。

若任一項未通過，先更新本文件的步驟或清單，再回到程式碼修正，直到全部通過。
