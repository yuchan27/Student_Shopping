from django.urls import path
from . import views

app_name = 'shops'

urlpatterns = [
    path('create/', views.create_shop, name='create_shop'),
    path('<int:shop_id>/', views.shop_detail, name='shop_detail'),
    # 確認有沒有這行，沒有的話補上去
    path('settings/', views.edit_shop, name='edit_shop'),
]