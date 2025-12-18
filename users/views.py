from django.shortcuts import render, redirect
from django.contrib.auth import logout, get_user_model, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from shops.models import Shop
from products.models import Product
# [修改 1] 記得要在這裡引入 UserProfileForm
from .forms import RegisterForm, UserProfileForm 

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
            # [建議] 註冊成功給個提示
            messages.success(request, '註冊成功！請登入您的帳號。')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})

# 登出功能
def logout_view(request):
    logout(request)
    messages.info(request, '您已成功登出。')
    return redirect('/')

# [新增 2] 會員中心 (個人資料修改)
@login_required
def profile(request):
    if request.method == 'POST':
        # instance=request.user 非常重要！這代表我們是在「修改」目前這個人，而不是「新增」別人
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '個人資料更新成功！')
            return redirect('users:profile') # 存檔後重新導向回同一頁
    else:
        # 如果是剛進來 (GET)，就顯示目前使用者的資料
        form = UserProfileForm(instance=request.user)

    return render(request, 'users/profile.html', {'form': form})

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
            # 修改完密碼，通常會導向回會員中心或首頁
            return redirect('users:profile') 
        else:
            messages.error(request, '請修正以下的錯誤。')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'users/change_password.html', {'form': form})