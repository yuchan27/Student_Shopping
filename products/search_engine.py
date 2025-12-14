import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from .models import Product

# 1. 初始化模型
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def semantic_search_products(query, top_k=5):
    """
    輸入使用者查詢 (query)，回傳最相關的 Product 物件列表
    """
    # 2. 準備資料
    products = list(Product.objects.all())
    
    if not products:
        return []

    # 組合文字
    product_texts = [f"{p.name} : {p.description}" for p in products]

    # 3. 轉成向量
    product_embeddings = model.encode(product_texts)

    # 4. 查詢詞轉向量
    query_vector = model.encode([query])

    # 5. 建立 FAISS 索引
    dimension = product_embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(product_embeddings)

    # 6. 開始搜尋
    # D 是距離 (數值越小代表越像)，I 是索引
    D, I = index.search(query_vector, top_k)
    
    # 7. [修正重點] 這裡要同時取出「索引(idx)」和「距離(distance)」來判斷
    results = []
    
    # 使用 zip 把 D[0] (距離) 和 I[0] (索引) 打包在一起跑迴圈
    for distance, idx in zip(D[0], I[0]):
        # FAISS 如果找不到會回傳 -1，我們跳過它
        if idx != -1:
            # [過濾門檻] 這裡設定 1.5 (你可以根據測試結果調整，越小越嚴格)
            # 如果距離太大 (> 1.5)，代表 AI 覺得這兩個東西其實不太像，就不顯示了
            if distance < 1.5:
                results.append(products[idx])
            
    return results