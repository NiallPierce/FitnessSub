from django.urls import path
from . import views

app_name = 'newsletter'

urlpatterns = [
    path('signup/', views.newsletter_signup, name='newsletter_signup'),
    path('confirm/<str:token>/', views.confirm_subscription, name='confirm_subscription'),
]
