# orders/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from products.models import Product
from .models import Order

@login_required
def buy_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # 1. 檢查庫存夠不夠
    if product.stock <= 0:
        return HttpResponse("抱歉，賣光了！")

    if request.method == 'POST':
        # 2. 確定購買，執行扣庫存
        product.stock -= 1
        product.save()
        
        # 3. 建立訂單紀錄
        Order.objects.create(
            buyer=request.user,
            product=product,
            amount=1,
            total_price=product.price
        )
        return HttpResponse(f"購買成功！你買到了 {product.name}")

    # 顯示確認購買頁面
    return render(request, 'orders/confirm.html', {'product': product})