from django.urls import path
from . import views

# 【關鍵修正】這裡一定要定義 app_name，HTML 裡的 'shops:...' 才能找到它
app_name = 'shops'

urlpatterns = [
    # 【關鍵修正】path 裡面要加上 name='...'
    path('create/', views.create_shop, name='create_shop'),
    path('<int:shop_id>/', views.shop_detail, name='shop_detail'),
]