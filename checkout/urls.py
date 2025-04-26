from django.urls import path
from . import views

app_name = 'checkout'

urlpatterns = [
    path('', views.checkout, name='checkout'),
    path(
        'payment/success/<str:order_number>/',
        views.payment_success,
        name='payment_success'
    ),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('orders/', views.order_history, name='order_history'),
    path(
        'orders/<int:order_id>/',
        views.order_detail,
        name='order_detail'
    ),
]
