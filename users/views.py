from django.shortcuts import render, redirect
from django.contrib.auth import logout, get_user_model, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from shops.models import Shop
from products.models import Product
from .forms import RegisterForm

User = get_user_model()

# 檢查是否為超級管理員的函式
def is_superuser(user):
    return user.is_superuser

# 總管理員儀表板
@user_passes_test(is_superuser, login_url='/')
def admin_dashboard(request):
    users = User.objects.all().order_by('-date_joined')
    shops = Shop.objects.all().order_by('-id')
    products = Product.objects.all().select_related('shop').order_by('-id')

    context = {
        'users': users,
        'shops': shops,
        'products': products,
        'user_count': users.count(),
        'shop_count': shops.count(),
        'product_count': products.count(),
    }
    return render(request, 'users/admin_dashboard.html', context)

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})

# 登出功能
def logout_view(request):
    logout(request)
    return redirect('/')

# 修改密碼功能
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # 更新 Session，防止被登出
            update_session_auth_hash(request, user)  
            messages.success(request, '您的密碼已成功修改！')
            return redirect('/')
        else:
            messages.error(request, '請修正以下的錯誤。')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'users/change_password.html', {'form': form})