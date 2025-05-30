from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.view_cart, name='view_cart'),
    path('add/<int:product_id>/', views.add_cart, name='cart_add'),
    path('remove/<int:product_id>/', views.remove_cart, name='remove_cart'),
    path(
        'remove_item/<int:product_id>/',
        views.remove_cart_item,
        name='remove_cart_item'
    ),
]
