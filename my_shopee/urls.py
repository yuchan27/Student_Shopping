# my_shopee/urls.py

from django.contrib import admin
from django.urls import path, include
from products.views import index  # 你原本的 index
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', index),  # 首頁
    path('admin/', admin.site.urls),
    
    # [新增] 這一行是為了加入「忘記密碼」與「登入登出」功能
    # Django 會自動對應到 accounts/password_reset/ 等網址
    path('accounts/', include('django.contrib.auth.urls')),
    path('users/', include('users.urls')),
    path('shops/', include('shops.urls')),
    path('products/', include('products.urls')),
    path('orders/', include('orders.urls')), 
]

# 圖片上傳設定 (你原本寫得很好，保留即可)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)