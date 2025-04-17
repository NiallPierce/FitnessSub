from django.urls import path
from . import views

app_name = 'checkout'

urlpatterns = [
    path('', views.checkout, name='checkout'),
    path('success/<int:order_id>/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
    path('complete/<str:order_number>/', views.order_complete, name='order_complete'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
] 