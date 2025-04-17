from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('', views.profile, name='profile'),
    path('order_history/<int:order_id>/', views.order_history, name='order_history'),
]