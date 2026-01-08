from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Shop
from .forms import ShopForm 

@login_required
def create_shop(request):
    if hasattr(request.user, 'shop'):
        return redirect('shops:shop_detail', shop_id=request.user.shop.id)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        shop = Shop.objects.create(owner=request.user, name=name, description=description)
        return redirect('shops:shop_detail', shop_id=shop.id)

    return render(request, 'shops/create_shop.html')

def shop_detail(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id)
    products = shop.products.all()
    context = {'shop': shop, 'products': products}
    return render(request, 'shops/shop_detail.html', context)

# [這就是消失的修改功能]
@login_required
def edit_shop(request):
    try:
        shop = request.user.shop
    except Shop.DoesNotExist:
        return redirect('shops:create_shop')

    if request.method == 'POST':
        form = ShopForm(request.POST, instance=shop)
        if form.is_valid():
            form.save()
            return redirect('shops:shop_detail', shop_id=shop.id)
    else:
        form = ShopForm(instance=shop)
    
    return render(request, 'shops/edit_shop.html', {'form': form, 'shop': shop})