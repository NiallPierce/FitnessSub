from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from .models import UserSubscription

class SubscriptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of URLs that require an active subscription
        protected_urls = [
            '/workouts/premium/',
            '/nutrition/premium/',
            '/community/premium/',
        ]

        # Check if the current URL requires a subscription
        if any(request.path.startswith(url) for url in protected_urls):
            if not request.user.is_authenticated:
                messages.error(request, 'Please log in to access this content.')
                return redirect('account_login')

            try:
                subscription = UserSubscription.objects.get(
                    user=request.user,
                    is_active=True
                )
                # Check if subscription is still valid
                if subscription.is_expired():
                    messages.error(request, 'Your subscription has expired. Please renew to access premium content.')
                    return redirect('products:subscription_plans')
            except UserSubscription.DoesNotExist:
                messages.error(request, 'This content requires an active subscription.')
                return redirect('products:subscription_plans')

        response = self.get_response(request)
        return response 