# orders/models.py
from django.db import models
from django.conf import settings
from products.models import Product

class Order(models.Model):
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.IntegerField(default=1) # 購買數量
    total_price = models.IntegerField()     # 總金額
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"訂單: {self.buyer} 買了 {self.product.name}"