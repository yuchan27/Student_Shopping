from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Shop

@login_required
def create_shop(request):
    # 如果已經有店了，直接跳轉到他的商店頁面
    if hasattr(request.user, 'shop'):
        return redirect('shops:shop_detail', shop_id=request.user.shop.id)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description') # 順便接收介紹

        # 建立商店
        shop = Shop.objects.create(owner=request.user, name=name, description=description)

        # 【修改這裡】建立成功後，直接跳轉到該商店的詳細頁面！
        return redirect('shops:shop_detail', shop_id=shop.id)

    return render(request, 'shops/create_shop.html')

def shop_detail(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id)
    # 取得該商店下的所有商品
    products = shop.products.all()

    context = {
        'shop': shop,
        'products': products
    }
    return render(request, 'shops/shop_detail.html', context)