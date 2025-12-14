from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from products.models import Product
from .models import Order

# 買家點擊「購買」後會觸發這個
@login_required
def create_order(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        # 1. 檢查庫存
        buy_amount = int(request.POST.get('amount', 1))
        if product.stock < buy_amount:
            return render(request, 'orders/error.html', {'message': '庫存不足！'})

        # 2. 建立訂單
        Order.objects.create(
            buyer=request.user,
            product=product,
            amount=buy_amount,
            total_price=product.price * buy_amount
        )

        # 3. 扣除庫存
        product.stock -= buy_amount
        product.save()

        # 4. 購買成功，導向「我的訂單」頁面 (稍後建立)
        return redirect('orders:my_orders')
    
    # 如果不是 POST 請求，導回首頁
    return redirect('/')

# 買家查看自己的訂單
@login_required
def my_orders(request):
    orders = Order.objects.filter(buyer=request.user).order_by('-created_at')
    return render(request, 'orders/my_orders.html', {'orders': orders})

# 【商家專用】查看誰買了我的東西
@login_required
def seller_dashboard(request):
    # 如果使用者沒有商店，就踢回去
    if not hasattr(request.user, 'shop'):
        return redirect('shops:create_shop')
        
    shop = request.user.shop
    # 找出所有「商品屬於這家店」的訂單
    orders = Order.objects.filter(product__shop=shop).order_by('-created_at')
    
    return render(request, 'orders/seller_dashboard.html', {'orders': orders})