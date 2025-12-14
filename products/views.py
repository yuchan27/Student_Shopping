from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Case, When, Value, IntegerField # [新增] 引入更多資料庫工具
from .models import Product
from .forms import ProductForm
from .search_engine import semantic_search_products #向量搜尋 

def index(request):
    products = Product.objects.all().order_by('-id')[:20]
    return render(request, 'products/index.html', {'products': products})

@login_required
def add_product(request):
    if not hasattr(request.user, 'shop'):
        return redirect('shops:create_shop')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.shop = request.user.shop
            product.save()
            return redirect('shops:shop_detail', shop_id=request.user.shop.id)
    else:
        form = ProductForm()
    return render(request, 'products/add_product.html', {'form': form})

# [這就是消失的編輯功能]
@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if product.shop.owner != request.user:
        return redirect('/')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('shops:shop_detail', shop_id=product.shop.id)
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/edit_product.html', {'form': form, 'product': product})

# [這就是消失的刪除功能]
@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if product.shop.owner != request.user:
        return redirect('/')

    if request.method == 'POST':
        shop_id = product.shop.id
        product.delete()
        return redirect('shops:shop_detail', shop_id=shop_id)
    
    return render(request, 'products/delete_confirm.html', {'product': product})

# [新增] 搜尋功能
def search(request):
    query = request.GET.get('q')
    search_type = "一般搜尋" # 用來告訴前端現在是用哪種搜尋
    
    if query:
        # --- 第一階段：原本的精準關鍵字搜尋 ---
        keywords = query.split()
        search_condition = Q()
        for word in keywords:
            search_condition &= (
                Q(name__icontains=word) | 
                Q(description__icontains=word) | 
                Q(shop__name__icontains=word)
            )

        products = Product.objects.filter(search_condition).order_by('-id')

        # --- 第二階段：如果關鍵字找不到東西，就啟動 AI 向量搜尋 ---
        if not products.exists():
            print("關鍵字找不到，啟動 AI 語意搜尋...") # 可以在終端機看日誌
            products = semantic_search_products(query)
            search_type = "💡 AI 智慧推薦" 
            
    else:
        products = Product.objects.none()

    return render(request, 'products/index.html', {
        'products': products, 
        'query': query,
        'search_type': search_type # 傳給前端顯示
    })