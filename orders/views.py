from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from products.models import Product
from django.contrib import messages
from .models import Order, CartItem 

@login_required
def create_order(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # [情況 A] 剛點進來 (GET) -> 顯示確認頁面
    if request.method == 'GET':
        return render(request, 'orders/confirm.html', {'product': product})
    
    # [情況 B] 按下確認購買 (POST) -> 建立訂單
    elif request.method == 'POST':
        buy_amount = 1
        if product.stock < buy_amount:
            # 記得確認你有沒有 orders/error.html，沒有的話這裡會報錯
            return render(request, 'orders/error.html', {'message': '庫存不足！'})

        user_phone = request.POST.get('phone')

        Order.objects.create(
            buyer=request.user,
            product=product,
            amount=buy_amount,
            total_price=product.price * buy_amount,
            phone=user_phone
        )

        product.stock -= buy_amount
        product.save()

        return redirect('orders:my_orders')

# 其他 view (my_orders, seller_dashboard) 應該還在，不用動
@login_required
def my_orders(request):
    orders = Order.objects.filter(buyer=request.user).order_by('-created_at')
    return render(request, 'orders/my_orders.html', {'orders': orders})

@login_required
def seller_dashboard(request):
    if not hasattr(request.user, 'shop'):
        return redirect('shops:create_shop')
    shop = request.user.shop
    orders = Order.objects.filter(product__shop=shop).order_by('-created_at')
    return render(request, 'orders/seller_dashboard.html', {'orders': orders})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # 檢查庫存
    if product.stock < 1:
        messages.error(request, '庫存不足，無法加入購物車')
        return redirect('/')

    # 取得或建立購物車項目 (get_or_create)
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user, 
        product=product
    )

    if not created:
        # 如果已經在車子裡，數量+1
        cart_item.quantity += 1
        cart_item.save()
    
    messages.success(request, f'已將 {product.name} 加入購物車！')
    return redirect('/')

# [新增 2] 查看購物車
@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    
    # 計算總金額
    total_price = sum(item.total_price() for item in cart_items)

    return render(request, 'orders/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

# [新增 3] 購物車結帳
@login_required
def checkout_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)

    if not cart_items:
        return redirect('orders:view_cart')

    if request.method == 'POST':
        phone = request.POST.get('phone')
        
        # 把每個購物車項目變成一張訂單
        for item in cart_items:
            # 再次檢查庫存
            if item.product.stock >= item.quantity:
                Order.objects.create(
                    buyer=request.user,
                    product=item.product,
                    amount=item.quantity,
                    total_price=item.total_price(),
                    phone=phone
                )
                # 扣庫存
                item.product.stock -= item.quantity
                item.product.save()
            
            # 結帳完刪除該項目
            item.delete()

        return redirect('orders:my_orders')

    return render(request, 'orders/checkout_cart.html', {'cart_items': cart_items})