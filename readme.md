# 🛒 蝦皮大學生版 (Shopee University Edition)

這是一個專為大學生設計的二手交易平台，使用 Django 框架開發。使用者可以註冊帳號、開設自己的商店，並上架二手教科書或生活用品。

## ✨ 功能特色

- **會員系統**：完整的註冊、登入、登出功能。
- **商店系統**：使用者可以一鍵開設自己的賣場。
- **商品管理**：支援商品上架、編輯，並可上傳實體照片。
- **RWD 介面**：使用 Bootstrap 5 設計，手機電腦都好看。
- **後台管理**：完整的 Django Admin 後台，方便管理員維護資料。

## 🛠️ 技術棧

- **後端**：Python 3, Django
- **前端**：HTML5, Bootstrap 5
- **資料庫**：SQLite (預設)

### 1. 下載專案

開啟終端機 (Terminal) 或 CMD，執行：

```bash
git clone https://github.com/yuchan27/network_database_project.git
cd network_database_project

然後建立虛擬環境 
python -m venv venv
venv\Scripts\activate

建立完成且設定為venv(左邊會看到一個venv) 
ex: (venv) PS C:\Users\> 

初始化資料庫
python manage.py migrate
設定帳號密碼和gmail(請測試用(自己填)@nkust.edu.tw)

python manage.py createsuperuser

啟動伺服器
python manage.py runserver

進入網址:
http://127.0.0.1:8000/
即可成功
```
