from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Case, When, Value, IntegerField
from .models import Product, Category
from .forms import ProductForm
from .search_engine import semantic_search_products # 向量搜尋 

# [Helper 函式] 用來處理分類排序：把「雜項」排到最後
def get_sorted_categories():
    # 1. 抓出所有「不是」雜項的分類，依照名稱(或id)排序
    normal_cats = Category.objects.exclude(name='雜項').order_by('id')
    # 2. 單獨抓出「雜項」分類
    misc_cat = Category.objects.filter(name='雜項')
    # 3. 合併成一個列表 (雜項在最後)
    return list(normal_cats) + list(misc_cat)

def index(request):
    # 取得目前網址上的分類參數 (例如 ?category=1)
    category_id = request.GET.get('category')
    # [新增] 取得排序參數，預設為 'newest'
    sort_by = request.GET.get('sort', 'newest')

    if category_id:
        # 如果有點擊分類，就只抓該分類的商品
        products = Product.objects.filter(category_id=category_id)
    else:
        # 沒點分類，就顯示全部
        products = Product.objects.all()

    # [新增] 這裡加入排序邏輯
    if sort_by == 'price_asc':      # 價格由低到高
        products = products.order_by('price')
    elif sort_by == 'price_desc':   # 價格由高到低
        products = products.order_by('-price')
    elif sort_by == 'name_asc':     # 名稱 A-Z
        products = products.order_by('name')
    elif sort_by == 'name_desc':    # 名稱 Z-A
        products = products.order_by('-name')
    else:                           # 預設：最新上架 (ID 倒序)
        products = products.order_by('-id')

    # [注意] 切片 (限制筆數) 必須放在排序之後！
    products = products[:20]

    # 使用我們自定義的分類排序邏輯
    categories = get_sorted_categories()

    return render(request, 'products/index.html', {
        'products': products, 
        'categories': categories, 
        'current_category': int(category_id) if category_id else None,
        'current_sort': sort_by # [新增] 把現在的排序狀態傳回前端
    })

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

# 搜尋功能
def search(request):
    query = request.GET.get('q')
    # [新增] 搜尋頁面也要能排序
    sort_by = request.GET.get('sort', 'newest')
    search_type = "一般搜尋"
    
    if query:
        keywords = query.split()
        search_condition = Q()
        for word in keywords:
            search_condition &= (
                Q(name__icontains=word) | 
                Q(description__icontains=word) | 
                Q(shop__name__icontains=word) |
                Q(category__name__icontains=word)
            )

        products = Product.objects.filter(search_condition)
        
        # [新增] 如果有找到結果，就進行排序 (如果是 AI 搜尋就不排序，保持關聯度)
        if products.exists():
            if sort_by == 'price_asc':
                products = products.order_by('price')
            elif sort_by == 'price_desc':
                products = products.order_by('-price')
            elif sort_by == 'name_asc':
                products = products.order_by('name')
            elif sort_by == 'name_desc':
                products = products.order_by('-name')
            else:
                products = products.order_by('-id')

        # 如果關鍵字找不到，啟動 AI
        else:
            print("關鍵字找不到，啟動 AI 語意搜尋...")
            products = semantic_search_products(query)
            search_type = "💡 AI 智慧推薦"
            # 注意：這裡我不對 AI 結果做額外排序，因為 AI 通常是依照「相似度」排序的
            
    else:
        products = Product.objects.none()
    
    categories = get_sorted_categories()

    return render(request, 'products/index.html', {
        'products': products, 
        'query': query,
        'search_type': search_type,
        'categories': categories,
        'current_sort': sort_by # [新增] 傳回排序狀態
    })