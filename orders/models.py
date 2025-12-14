from django.db import models
from django.conf import settings
from products.models import Product

class Order(models.Model):
    # 買家是誰
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    # 買了什麼商品
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sold_orders')
    # 數量
    amount = models.PositiveIntegerField(default=1)
    # 總價 (因為商品價格可能會變，建議下單時就把價格記下來)
    total_price = models.PositiveIntegerField()
    # 訂單時間
    created_at = models.DateTimeField(auto_now_add=True)
    # 訂單狀態 (未付款、已出貨...)
    status = models.CharField(max_length=20, default='已下單')

    def __str__(self):
        return f"訂單 #{self.id} - {self.product.name}"