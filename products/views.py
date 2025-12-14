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

    if category_id:
        # 如果有點擊分類，就只抓該分類的商品
        products = Product.objects.filter(category_id=category_id).order_by('-id')
    else:
        # 沒點分類，就顯示全部 (限制 20 筆)
        products = Product.objects.all().order_by('-id')[:20]

    # [修改] 使用我們自定義的排序邏輯，而不是直接用 objects.all()
    categories = get_sorted_categories()

    return render(request, 'products/index.html', {
        'products': products, 
        'categories': categories, # 傳分類給模板
        'current_category': int(category_id) if category_id else None # 轉成 int 以便模板比對
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

        products = Product.objects.filter(search_condition).order_by('-id')

        # 如果關鍵字找不到，啟動 AI
        if not products.exists():
            print("關鍵字找不到，啟動 AI 語意搜尋...")
            products = semantic_search_products(query)
            search_type = "💡 AI 智慧推薦"
            
    else:
        products = Product.objects.none()
    
    # [修改] 搜尋頁面也要顯示分類側邊欄 (同樣要讓雜項在最下面)
    categories = get_sorted_categories()

    return render(request, 'products/index.html', {
        'products': products, 
        'query': query,
        'search_type': search_type,
        'categories': categories # 傳分類給模板
    })