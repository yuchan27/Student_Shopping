from django.urls import path
from . import views

# 【關鍵修正】定義 app_name
app_name = 'products'

urlpatterns = [
    # 【關鍵修正】加上 name='add_product'
    path('add/', views.add_product, name='add_product'),
]