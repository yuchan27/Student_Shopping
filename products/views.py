from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Case, When, Value, IntegerField # [新增] 引入更多資料庫工具
from .models import Product
from .forms import ProductForm

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
    query = request.GET.get('q')  # 取得使用者輸入的字串
    
    if query:
        # 1. 關鍵字拆分 (變聰明的關鍵！)
        # 如果使用者輸入 "iPhone 便宜"，split() 會把它拆成 ['iPhone', '便宜']
        keywords = query.split()
        
        # 建立一個基礎的查詢物件
        search_condition = Q()
        
        # 2. 迴圈組裝邏輯
        # 我們希望每一個拆開的關鍵字，都要出現在「名稱」OR「描述」OR「商店名」裡面
        for word in keywords:
            search_condition &= (
                Q(name__icontains=word) | 
                Q(description__icontains=word) |  # [新增] 加入描述搜尋
                Q(shop__name__icontains=word)
            )

        # 3. 執行搜尋並加上「權重排序」 (讓結果更精準)
        # 邏輯：如果關鍵字出現在「名稱(name)」裡，給它 100 分；出現在「描述」只給 10 分。
        # 這樣搜尋出來，「標題就符合」的商品會排在最前面。
        products = Product.objects.filter(search_condition).annotate(
            relevance=Case(
                # 如果名稱包含完整搜尋詞，分數最高 (優先顯示)
                When(name__icontains=query, then=Value(100)),
                # 如果名稱包含部分關鍵字，分數次之
                When(name__icontains=keywords[0], then=Value(50)),
                # 其他情況 (只在描述裡找到) 分數較低
                default=Value(10),
                output_field=IntegerField(),
            )
        ).order_by('-relevance', '-id') # 先照關聯度排，再照新舊排
        
    else:
        products = Product.objects.none()

    return render(request, 'products/index.html', {'products': products, 'query': query})