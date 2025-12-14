from django.shortcuts import render, redirect
from django.contrib.auth import logout, get_user_model # [修正] 這裡原本拼錯了
from django.contrib.auth.decorators import user_passes_test
from shops.models import Shop       # 引入商店
from products.models import Product # 引入商品
from .forms import RegisterForm

User = get_user_model()

# 檢查是否為超級管理員的函式
def is_superuser(user):
    return user.is_superuser

# [新增] 總管理員儀表板
@user_passes_test(is_superuser, login_url='/') # 如果不是管理員，直接踢回首頁
def admin_dashboard(request):
    # 抓取所有資料
    users = User.objects.all().order_by('-date_joined')
    shops = Shop.objects.all().order_by('-id')
    products = Product.objects.all().select_related('shop').order_by('-id')

    # 計算總數 (給儀表板上面的數字卡片用)
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
            # 註冊成功後，跳轉到登入頁面
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})

# 登出功能
def logout_view(request):
    logout(request)       # 清除使用者的登入狀態 (Session)
    return redirect('/')  # 登出後直接跳回首頁