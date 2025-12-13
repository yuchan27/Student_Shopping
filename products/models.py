from django.db import models
from shops.models import Shop

class Product(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    price = models.IntegerField()
    stock = models.IntegerField(default=1)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    # 客製化 ID (賣家ID + 商品ID)
    @property
    def custom_sku(self):
        return f"{self.shop.id}-{self.id}"

    def __str__(self):
        return self.name