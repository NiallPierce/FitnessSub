from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string

class NewsletterSubscription(models.Model):
    email = models.EmailField(max_length=254, unique=True)
    date_subscribed = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)  # Changed to False until confirmed
    confirmation_token = models.CharField(max_length=64, unique=True, blank=True)
    confirmation_sent = models.DateTimeField(null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.email

    def generate_confirmation_token(self):
        """Generate a unique confirmation token"""
        token = get_random_string(length=64)
        self.confirmation_token = token
        self.confirmation_sent = timezone.now()
        self.save()
        return token

    def confirm_subscription(self):
        """Confirm the subscription"""
        self.is_active = True
        self.confirmed_at = timezone.now()
        self.save()