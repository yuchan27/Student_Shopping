from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from products.models import Product
from django.contrib import messages
from django.db import transaction
from .models import Order, CartItem 

@login_required
@transaction.atomic
def create_order(request, product_id):
    
    # [情況 A] 剛點進來 (GET) -> 顯示確認頁面
    if request.method == 'GET':
        # 這裡只需要普通讀取，讓使用者看到商品資訊即可
        product = get_object_or_404(Product, id=product_id)
        return render(request, 'orders/confirm.html', {'product': product})
    
    # [情況 B] 按下確認購買 (POST) -> 建立訂單
    elif request.method == 'POST':
        try:
            # [關鍵修改] 使用 select_for_update() 鎖住這筆商品
            # 這時候資料庫會把這行資料鎖起來，其他人要讀取必須排隊等待
            product = Product.objects.select_for_update().get(id=product_id)
        except Product.DoesNotExist:
            return render(request, 'orders/error.html', {'message': '商品不存在或已被刪除！'})

        buy_amount = 1

        # 再次檢查庫存 (這是最重要的一步，防止排隊的人買到沒貨的商品)
        if product.stock < buy_amount:
            return render(request, 'orders/error.html', {'message': '抱歉！剛好被搶光了，下次請早！'})

        user_phone = request.POST.get('phone')

        # 建立訂單
        Order.objects.create(
            buyer=request.user,
            product=product,
            amount=buy_amount,
            total_price=product.price * buy_amount,
            phone=user_phone
        )

        # 扣庫存
        product.stock -= buy_amount
        product.save() # 儲存後，鎖定會自動解除，換下一位排隊的人進來處理

        return redirect('orders:my_orders')
    
@login_required
def my_orders(request):
    orders = Order.objects.filter(buyer=request.user).order_by('-created_at')
    return render(request, 'orders/my_orders.html', {'orders': orders})

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

# [新增] 移除購物車項目
@login_required
def remove_from_cart(request, cart_item_id):
    # 找到該購物車項目，如果找不到就回傳 404
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    
    # 安全檢查：確保這個項目是屬於目前登入的使用者的
    if cart_item.user == request.user:
        cart_item.delete() # 刪除資料庫紀錄
        messages.success(request, '商品已從購物車移除！')
    
    # 刪除完後，重新導向回購物車頁面
    return redirect('orders:view_cart')

@login_required
def seller_dashboard(request):
    # 1. 確保使用者有開店
    if not hasattr(request.user, 'shop'):
        return redirect('shops:create_shop')
    
    shop = request.user.shop
    
    # 2. 搜尋訂單：條件是 "商品的商店 = 我的商店"
    # select_related 是為了優化效能，一次把買家和商品資料抓出來
    orders = Order.objects.filter(product__shop=shop).select_related('product', 'buyer').order_by('-created_at')

    return render(request, 'orders/seller_dashboard.html', {'orders': orders})