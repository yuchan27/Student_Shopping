# 🛒 蝦皮大學生版 (Shopee University Edition)

這是一個專為大學生設計的二手交易平台，使用 Django 框架開發。使用者可以註冊帳號、開設自己的商店，並上架二手教科書或生活用品。

## ✨ 功能特色

### 核心功能

- **會員系統**：完整的註冊、登入、登出功能，並限制使用學校信箱 (`@nkust.edu.tw`) 驗證。
- **商店系統**：使用者可以一鍵開設自己的賣場，成為賣家。
- **商品管理**：支援商品上架、編輯、刪除，並可上傳實體照片。
- **RWD 介面**：使用 Bootstrap 5 響應式設計，手機電腦都能完美瀏覽。
- **後台管理**：完整的 Django Admin 後台，方便管理員維護資料與分類。

### 🔥 最新功能 (New Features)

- **購物車系統**：支援加入購物車、移除商品、結帳流程。
- **防止超賣機制**：使用資料庫鎖定 (Lock) 技術，避免多人同時搶購導致庫存錯誤。
- **進階搜尋**：支援關鍵字搜尋（商品名、商店名、分類、描述）。
- **AI 語意搜尋**：當關鍵字找不到結果時，自動啟動 Embedding 向量搜尋推薦相似商品。
- **排序功能**：可依照價格高低、上架時間、名稱排序。
- **圖片優化**：自動修正圖片顯示比例，並支援刪除商品時自動清除硬碟圖片 (使用 `django-cleanup`)。
- **安全性**：實作前後端權限驗證，並提供使用者修改密碼功能。

## 🛠️ 技術棧

- **後端**：Python 3.13, Django
- **前端**：HTML5, CSS3, Bootstrap 5, JavaScript
- **資料庫**：SQLite (開發環境預設)
- **搜尋技術**：Vector Embedding (語意搜尋)

## 🚀 快速開始 (Installation)

開啟終端機 (Terminal) 或 CMD，執行：

```bash
git clone https://github.com/yuchan27/network_database_project.git
cd network_database_project

切換至yuchan分支 
1. git checkout yuchan
如果已經有clone過，執行以下指令更新當前電腦git
git fetch
git checkout yuchan
python manage.py migrate
(記得只要fetch後就要更改資料庫)

然後建立虛擬環境 
python -m venv venv
venv\Scripts\activate

建立完成且設定為venv(左邊會看到一個venv) 
ex: (venv) PS C:\Users\> 

接著引入所有依賴
pip install -r requirements.txt

初始化資料庫
python manage.py migrate
設定帳號密碼和gmail(請測試用(自己填)@nkust.edu.tw)

建立超級管理員(很重要 後端操作基本上都在這裡)
python manage.py createsuperuser

啟動伺服器
python manage.py runserver

進入網址:
http://127.0.0.1:8000/
即可成功
```
