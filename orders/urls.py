from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/<int:product_id>/', views.create_order, name='create_order'),
    path('mine/', views.my_orders, name='my_orders'),
    path('seller/', views.seller_dashboard, name='seller_dashboard'),
]