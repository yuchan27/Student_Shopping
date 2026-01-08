from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from products.models import Product
from django.contrib import messages
from django.db import transaction
from .models import Order, OrderItem, CartItem 

# ==========================================
#  購買與結帳核心功能 (新架構)
# ==========================================

# [情況 1] 直接購買 (立即購買單一商品)
@login_required
@transaction.atomic
def create_order(request, product_id):
    if request.method == 'GET':
        product = get_object_or_404(Product, id=product_id)
        return render(request, 'orders/confirm.html', {'product': product})
    
    elif request.method == 'POST':
        try:
            # 鎖定商品庫存防止超賣
            product = Product.objects.select_for_update().get(id=product_id)
        except Product.DoesNotExist:
            return render(request, 'orders/error.html', {'message': '商品不存在！'})

        buy_amount = 1
        if product.stock < buy_amount:
            return render(request, 'orders/error.html', {'message': '庫存不足！'})

        user_phone = request.POST.get('phone')

        # 1. 建立訂單主檔
        new_order = Order.objects.create(
            buyer=request.user,
            phone=user_phone,
            total_price=product.price * buy_amount,
            status='已下單'
        )

        # 2. 建立訂單明細
        OrderItem.objects.create(
            order=new_order,
            product=product,
            product_name=product.name,
            price=product.price,
            quantity=buy_amount
        )

        # 3. 扣庫存
        product.stock -= buy_amount
        product.save()

        return redirect('orders:my_orders')

# [情況 2] 購物車結帳 (將多個商品合併為一張單)
@login_required
@transaction.atomic
def checkout_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)

    if not cart_items:
        return redirect('orders:view_cart')

    if request.method == 'POST':
        phone = request.POST.get('phone')
        
        # 1. 計算總金額
        cart_total = sum(item.product.price * item.quantity for item in cart_items)
        
        # 2. 建立訂單主檔
        new_order = Order.objects.create(
            buyer=request.user,
            phone=phone,
            total_price=cart_total,
            status='已下單'
        )

        # 3. 迴圈建立明細並扣庫存
        for item in cart_items:
            if item.product.stock >= item.quantity:
                OrderItem.objects.create(
                    order=new_order,
                    product=item.product,
                    product_name=item.product.name,
                    price=item.product.price,
                    quantity=item.quantity
                )
                item.product.stock -= item.quantity
                item.product.save()
            else:
                messages.error(request, f'{item.product.name} 庫存不足，未結帳該商品')
        
        # 4. 清空購物車
        cart_items.delete()

        return redirect('orders:my_orders')

    return render(request, 'orders/checkout_cart.html', {'cart_items': cart_items})

# [情況 3] 我的訂單列表
@login_required
def my_orders(request):
    # 使用 prefetch_related 優化查詢
    orders = Order.objects.filter(buyer=request.user).order_by('-created_at').prefetch_related('items__product')
    return render(request, 'orders/my_orders.html', {'orders': orders})

# ==========================================
#  購物車相關功能 (補回遺失的部分)
# ==========================================

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if product.stock < 1:
        messages.error(request, '庫存不足')
        return redirect('/')
    
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
        
    messages.success(request, f'已將 {product.name} 加入購物車！')
    return redirect('/')

@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.total_price() for item in cart_items)
    return render(request, 'orders/cart.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
    cart_item.delete()
    messages.success(request, '已移除商品')
    return redirect('orders:view_cart')

# ==========================================
#  賣家儀表板 (修正為查詢 OrderItem)
# ==========================================

@login_required
def seller_dashboard(request):
    # 1. 確保有開店
    if not hasattr(request.user, 'shop'):
        return redirect('shops:create_shop')
    
    shop = request.user.shop
    
    # [修正邏輯]
    # 因為 Order 已經沒有 product 欄位了，賣家要看的是「訂單明細 (OrderItem)」
    # 這裡找出「商品屬於我的商店」的所有售出紀錄
    sold_items = OrderItem.objects.filter(product__shop=shop).select_related('order', 'product', 'order__buyer').order_by('-order__created_at')

    # 注意：這裡傳給 template 的是 "sold_items" (明細列表)，不是舊的 orders
    return render(request, 'orders/seller_dashboard.html', {'sold_items': sold_items})