from django.db import models
from django.conf import settings
from products.models import Product

# 1. 訂單主檔 (Parent)：像發票的「表頭」，記錄整筆交易的資訊
class Order(models.Model):
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    
    # 這裡只記整張單的總金額，不記個別商品
    total_price = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='已下單')
    
    # 電話放在主檔，代表這整批貨都寄給這個人
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"訂單 #{self.id} - {self.buyer}"

# 2. 訂單明細 (Child)：像發票的「列表」，記錄買了哪些東西
class OrderItem(models.Model):
    # 連結到上面的 Order
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    
    # 連結到商品
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=100, default="")
    # 記錄當下的單價 (避免以後商品漲價，歷史訂單金額變動)
    price = models.PositiveIntegerField()
    
    # 購買數量
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        product_name = self.product.name if self.product else "未知商品"
        return f"{product_name} x {self.quantity}"
    
    @property
    def total(self):
        return self.price * self.quantity

# 3. 購物車 (保持不變)
class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.user.username} 的購物車 - {self.product.name}"