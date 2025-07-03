from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('add/', views.add_to_cart, name='add_to_cart_ajax'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/data/', views.get_cart_data, name='get_cart_data'),
    path('checkout/', views.checkout, name='checkout'),
    path('cart/delete/<int:product_id>/', views.delete_from_cart, name='delete_from_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('my_orders/', views.my_orders, name='my_orders'),
]