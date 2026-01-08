from django.contrib import admin
from .models import Product, Category

# [升級 1] 註冊分類模型，並顯示 ID
# 這樣你就能看到分類的 ID (例如: 手機是 ID 1)，方便除錯
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')

# [升級 2] 商品管理介面優化
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # 在列表頁多顯示 'category' (分類)
    list_display = ('name', 'price', 'stock', 'category', 'shop')
    
    # [新增] 右側篩選器：可以依照「分類」或「商店」快速過濾
    list_filter = ('category', 'shop')
    
    # [新增] 搜尋設定：除了搜尋商品名，也可以搜尋分類名稱 (例如搜 "手機" 也會出現)
    search_fields = ('name', 'category__name')