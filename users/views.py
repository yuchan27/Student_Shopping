from django.shortcuts import render, redirect
from django.contrib.auth import logout, get_user_model, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
# [新增 1] 引入這兩個模組，用於處理 AJAX 回傳
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from shops.models import Shop
from products.models import Product
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
            messages.success(request, '註冊成功！請登入您的帳號。')
            return redirect('login')
        else:
            messages.error(request, '註冊失敗，請檢查輸入資料是否正確。')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})

# 登出功能
def logout_view(request):
    logout(request)
    messages.info(request, '您已成功登出。')
    return redirect('/')

# 會員中心 (個人資料修改)
@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '個人資料更新成功！')
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'users/profile.html', {'form': form})

# [新增 2] AJAX 專用的修改密碼函式 (對應懸浮框)
@login_required
@require_POST
def ajax_password_change(request):
    form = PasswordChangeForm(request.user, request.POST)
    if form.is_valid():
        user = form.save()
        # 更新 Session，防止被登出
        update_session_auth_hash(request, user)
        return JsonResponse({'status': 'success', 'message': '密碼修改成功！'})
    else:
        # 將錯誤訊息轉換成字典格式回傳給前端 JS
        # form.errors.items() 會回傳像 {'old_password': ['密碼錯誤'], ...}
        errors = {field: error_list[0] for field, error_list in form.errors.items()}
        return JsonResponse({'status': 'error', 'errors': errors})