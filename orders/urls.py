from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/<int:product_id>/', views.create_order, name='create_order'),
    path('mine/', views.my_orders, name='my_orders'),
    path('seller/', views.seller_dashboard, name='seller_dashboard'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/checkout/', views.checkout_cart, name='checkout_cart'),
    path('dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('remove/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
]