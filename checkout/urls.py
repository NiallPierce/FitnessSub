from django.urls import path
from . import views

app_name = 'checkout'

urlpatterns = [
    path('', views.checkout, name='checkout'),
    path('success/<int:order_id>/', views.payment_success, name='success'),
    path('cancel/', views.payment_cancel, name='cancel'),
] 