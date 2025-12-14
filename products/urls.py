from django.urls import path
from . import views

# 【關鍵修正】定義 app_name
app_name = 'products'

urlpatterns = [
    # 【關鍵修正】加上 name='add_product'
    path('add/', views.add_product, name='add_product'),
    path('edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('search/', views.search, name='search'),
    path('', views.index, name='index'),
]