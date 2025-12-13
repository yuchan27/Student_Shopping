from django.contrib import admin
from .models import Product

# 註冊 Product 模型，讓它顯示在後台
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'shop') # 在列表頁顯示這些欄位
    search_fields = ('name',) # 增加搜尋框