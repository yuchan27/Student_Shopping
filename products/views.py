from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Product

# 功能一：首頁
def index(request):
    # 抓出最新的 10 筆商品
    products = Product.objects.all().order_by('-id')[:10]
    return render(request, 'products/index.html', {'products': products})

# 功能二：上架商品
@login_required
def add_product(request):
    # 檢查使用者有沒有商店，沒有就請他去開
    # 注意：這行前提是你的 User model 有跟 Shop 建立 OneToOne 關聯
    if not hasattr(request.user, 'shop'):
        return redirect('shops:create_shop')

    if request.method == 'POST':
        # 1. 獲取文字資料
        name = request.POST.get('name')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        image = request.FILES.get('image') 

        if not stock: 
            stock = 1

        # 3. 儲存到資料庫
        Product.objects.create(
            shop=request.user.shop, 
            name=name, 
            price=price,
            stock=stock,
            image=image  # [關鍵新增] 把圖片存進去
        )
        
        # 上架成功後，直接跳轉回自己的商店頁面
        return redirect('shops:shop_detail', shop_id=request.user.shop.id)

    return render(request, 'products/add_product.html')