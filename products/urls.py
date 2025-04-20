from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.products, name='products'),
    path('<int:product_id>/', views.product_detail, name='product_detail'),
    path('add/', views.add_product, name='add_product'),
    path('edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete/<int:product_id>/', views.delete_product, name='delete_product'),
    
    # Subscription URLs
    path('subscription-plans/', views.subscription_plans, name='subscription_plans'),
    path('subscriptions/<int:plan_id>/', views.subscription_detail, name='subscription_detail'),
    path('subscribe/<int:plan_id>/', views.subscribe, name='subscribe'),
    path('subscriptions/cancel/', views.subscription_cancel, name='subscription_cancel'),
    path('subscription-history/', views.subscription_history, name='subscription_history'),
    path('subscription-success/', views.subscription_success, name='subscription_success'),
    path('debug/stripe-config/', views.debug_stripe_config, name='debug_stripe_config'),
]