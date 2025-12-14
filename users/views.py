from django.shortcuts import render, redirect
from django.contrib.auth import logout
from .forms import RegisterForm

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            # 註冊成功後，跳轉到登入頁面 (Django Admin 預設登入頁)
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})

# 【新增】登出功能
def logout_view(request):
    logout(request)       # 清除使用者的登入狀態 (Session)
    return redirect('/')  # 登出後直接跳回首頁