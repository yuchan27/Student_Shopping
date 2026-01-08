import requests
import re
import time
import random
import json

# ==========================================
# 引擎 A: PChome 24h 購物 (Debug 版)
# ==========================================
def search_pchome(keyword):
    print(f"   🛍️ [PChome] 正在搜尋: {keyword}")
    
    url = "https://ecshweb.pchome.com.tw/search/v3.3/all/results"
    params = {'q': keyword, 'page': 1, 'sort': 'rnk/dc'}
    
    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        
        # 除錯：印出 API 回傳狀態
        prod_count = data.get('totalRows', 0)
        print(f"   🛍️ [PChome] API 回應成功，找到 {prod_count} 筆相關資料")

        if 'prods' not in data or not data['prods']:
            print("   ⚠️ [PChome] 回傳資料中沒有商品列表 (prods is empty)")
            return []

        results = []
        for item in data['prods'][:10]: # 抓前 5 筆
            try:
                title = item.get('name', '未知商品')
                price = item.get('price', 0)
                
                # 圖片處理
                img_filename = item.get('picS', '') or item.get('picB', '')
                img_url = f"https://cs-a.ecimg.tw{img_filename}" if img_filename else ""

                # 描述處理
                describe = item.get('describe', '')
                if not describe: describe = title # 如果沒描述，用標題代替

                print(f"      ✅ 抓到: {title} (${price})") # [新增] 印出來給你看！

                results.append({
                    'title': title,
                    'author': 'PChome 來源',
                    'price': price,
                    'image': img_url,
                    'source': 'PChome 24h'
                })
            except Exception as e:
                print(f"      ❌ 解析單筆失敗: {e}")
                continue
        
        return results
    except Exception as e:
        print(f"   ❌ [PChome] 連線或解析錯誤: {e}")
        return []

# ==========================================
# 引擎 B: Google Books API (Debug 版)
# ==========================================
def search_google_books(keyword):
    print(f"   📚 [Google Books] 正在搜尋: {keyword}")
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {"q": keyword, "maxResults": 3, "langRestrict": "zh-TW", "printType": "books"}

    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        
        if "items" not in data:
            print("   ⚠️ [Google] 找不到書籍資料")
            return []

        results = []
        for item in data["items"]:
            try:
                info = item.get("volumeInfo", {})
                title = info.get("title", "未知書名")
                authors = info.get("authors", ["未知作者"])
                
                print(f"      ✅ 抓到書: {title}")

                # 圖片
                image_links = info.get("imageLinks", {})
                img_url = image_links.get("thumbnail") or image_links.get("smallThumbnail") or ""
                if img_url.startswith("http://"): img_url = img_url.replace("http://", "https://")

                # 價格
                price = 0
                if "listPrice" in item.get("saleInfo", {}):
                    price = int(item["saleInfo"]["listPrice"].get("amount", 0))

                results.append({
                    'title': title,
                    'author': ", ".join(authors),
                    'price': price,
                    'image': img_url,
                    'source': 'Google Books'
                })
            except: continue
        return results
    except Exception as e:
        print(f"   ❌ [Google] 錯誤: {e}")
        return []

# ==========================================
# 主入口 (Controller)
# ==========================================
def get_book_info(keyword):
    if not keyword: return []
    keyword = keyword.strip()

    print(f"--- 開始搜尋: {keyword} ---")

    # 1. 判斷是否為 ISBN
    if keyword.isdigit() and len(keyword) in [10, 13]:
        print("   🔢 偵測到 ISBN格式")
        res = search_google_books(keyword)
        if res: return res

    # 2. PChome 優先
    res = search_pchome(keyword)
    if res: 
        print(f"--- 搜尋結束，回傳 {len(res)} 筆資料 ---")
        return res

    # 3. Google 補救
    print("   ⚠️ PChome 沒結果，嘗試 Google Books...")
    res = search_google_books(keyword)
    print(f"--- 搜尋結束，回傳 {len(res)} 筆資料 ---")
    return res