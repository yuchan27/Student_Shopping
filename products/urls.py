from django.urls import path
from . import views

# 【關鍵修正】定義 app_name
app_name = 'products'

urlpatterns = [
    path('<int:product_id>/', views.product_detail, name='product_detail'),
    path('add/', views.add_product, name='add_product'),
    path('delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('search/', views.search, name='search'),
    path('category/add/', views.add_category, name='add_category'),
    path('category/edit/<int:category_id>/', views.edit_category, name='edit_category'),
    path('api/magic-fill/', views.magic_fill_product, name='magic_fill'),
    path('api/magic-fill/', views.magic_fill_product, name='magic_fill_product'),
    path('', views.index, name='index'),
]