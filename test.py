# test_ai.py
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# 載入多語言模型
print("正在載入模型，請稍候...")
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# 定義我們要測試的句子
text_1 = "手機"
text_2 = "Phone"
text_3 = "Banana"  # 用來對照的不相關詞

# 轉成向量
embeddings = model.encode([text_1, text_2, text_3])

# 計算相似度 (越高代表越像)
score_phone = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
score_banana = cosine_similarity([embeddings[0]], [embeddings[2]])[0][0]

print(f"-----------------------------")
print(f"「{text_1}」 跟 「{text_2}」 的相似度: {score_phone:.4f}")
print(f"「{text_1}」 跟 「{text_3}」 的相似度: {score_banana:.4f}")
print(f"-----------------------------")

if score_phone > 0.5:
    print("✅ 成功！模型知道 Phone 就是 手機！")
else:
    print("❌ 失敗，模型不夠聰明。")