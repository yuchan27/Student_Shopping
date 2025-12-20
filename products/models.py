from django.db import models
from shops.models import Shop

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="分類名稱")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "商品分類"

class Product(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='products')
    # null=True, blank=True 是為了讓舊的商品不會報錯，之後你可以去後台補設定
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')

    name = models.CharField(max_length=200)
    price = models.IntegerField()
    stock = models.IntegerField(default=1)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_DEFAULT, # 如果分類被刪除，商品會變回預設值
        default=1, # 假設「雜項」的 ID 是 1 (請根據你的資料庫實際 ID 修改)
        verbose_name="商品分類"
    )
    @property
    def custom_sku(self):
        return f"{self.shop.id}-{self.id}"

    def __str__(self):
        return self.name