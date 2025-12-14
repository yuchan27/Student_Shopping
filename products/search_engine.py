import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from .models import Product

# 確保是用這顆多語言模型
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def semantic_search_products(query, top_k=5):
    """
    輸入使用者查詢 (query)，回傳最相關的 Product 物件列表
    """
    products = list(Product.objects.all())
    
    if not products:
        return []

    # 組合文字
    product_texts = [f"{p.name} : {p.description}" for p in products]

    # 轉成向量
    product_embeddings = model.encode(product_texts)
    query_vector = model.encode([query])

    # 建立 FAISS 索引
    dimension = product_embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(product_embeddings)

    # 搜尋
    D, I = index.search(query_vector, top_k)
    
    results = []
    
    print(f"------------ 搜尋關鍵字: {query} ------------")
    
    for distance, idx in zip(D[0], I[0]):
        if idx != -1:
            # 歐幾里德距離設定成 15.0 (因為手機的距離是 5.6)
            if distance < 15.0:
                results.append(products[idx])
            
    print("-------------------------------------------")
            
    return results