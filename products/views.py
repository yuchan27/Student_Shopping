from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
import sys
import os

from .models import Product, Category
from .forms import ProductForm, CategoryForm
from .search_engine import semantic_search_products

# 嘗試引入爬蟲工具
try:
    from utils.crawler import get_book_info
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.crawler import get_book_info

# [Helper 函式] 分類排序
def get_sorted_categories():
    normal_cats = Category.objects.exclude(name='雜項').order_by('id')
    misc_cat = Category.objects.filter(name='雜項')
    return list(normal_cats) + list(misc_cat)

# 首頁
def index(request):
    category_id = request.GET.get('category')
    sort_by = request.GET.get('sort', 'newest')

    if category_id:
        products = Product.objects.filter(category_id=category_id)
    else:
        products = Product.objects.all()

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

    products = products[:20]
    categories = get_sorted_categories()

    return render(request, 'products/index.html', {
        'products': products, 
        'categories': categories, 
        'current_category': int(category_id) if category_id else None,
        'current_sort': sort_by 
    })

# ==========================================
# [修復] 這裡補回了原本遺失的 add_product
# ==========================================
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
            # [新增] 商品上架成功提示
            messages.success(request, '商品上架成功！')
            return redirect('shops:shop_detail', shop_id=request.user.shop.id)
    else:
        form = ProductForm()
    return render(request, 'products/add_product.html', {'form': form})

# 編輯商品
@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if product.shop.owner != request.user:
        return redirect('/')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            # [新增] 商品編輯成功提示
            messages.success(request, '商品修改成功！')
            return redirect('shops:shop_detail', shop_id=product.shop.id)
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/edit_product.html', {'form': form, 'product': product})

# 刪除商品
@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if product.shop.owner != request.user:
        return redirect('/')

    if request.method == 'POST':
        shop_id = product.shop.id
        product.delete()
        # [新增] 商品刪除成功提示
        messages.success(request, '商品已刪除。')
        return redirect('shops:shop_detail', shop_id=shop_id)
    
    return render(request, 'products/delete_confirm.html', {'product': product})

# 搜尋
def search(request):
    query = request.GET.get('q')
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
        else:
            print("關鍵字找不到，啟動 AI 語意搜尋...")
            products = semantic_search_products(query)
            search_type = "💡 AI 智慧推薦"
            
    else:
        products = Product.objects.none()
    
    categories = get_sorted_categories()

    return render(request, 'products/index.html', {
        'products': products, 
        'query': query,
        'search_type': search_type,
        'categories': categories,
        'current_sort': sort_by 
    })

# ==========================================
# [修復] 這裡補回了 add_category 的訊息功能
# ==========================================
@login_required
@user_passes_test(lambda u: u.is_staff)
def add_category(request):
    categories = Category.objects.all().order_by('-id')

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            # 成功訊息
            messages.success(request, f'成功新增「{category.name}」分類！')
            return redirect('products:add_category')
    else:
        form = CategoryForm()

    return render(request, 'products/add_category.html', {
        'form': form,
        'categories': categories
    })

# 編輯分類
@login_required
@user_passes_test(lambda u: u.is_staff)
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        new_name = request.POST.get('category_name')
        if new_name:
            category.name = new_name
            category.save()
            messages.success(request, f'分類 "{new_name}" 更新成功！')
        else:
            messages.error(request, '分類名稱不能為空！')
    
    return redirect('products:add_category')

# 智慧填單 API
@require_POST
def magic_fill_product(request):
    try:
        keyword = request.POST.get('keyword')
        if not keyword:
            return JsonResponse({'status': 'error', 'message': '請輸入關鍵字或 ISBN'})

        data = get_book_info(keyword)
        
        if data:
            return JsonResponse({'status': 'success', 'data': data})
        else:
            return JsonResponse({'status': 'fail', 'message': '找不到相關書籍，請確認名稱或 ISBN 是否正確'})

    except Exception as e:
        print(f"API Error: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'products/product_detail.html', {'product': product})