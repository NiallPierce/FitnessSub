from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('', views.profile, name='profile'),
    path(
        'order_history/<str:order_number>/',
        views.order_history,
        name='order_history'
    ),
    path(
        'order_tracking/<str:order_number>/',
        views.order_tracking,
        name='order_tracking'
    ),
]
