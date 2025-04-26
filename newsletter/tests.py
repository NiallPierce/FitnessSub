from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.http import HttpRequest
from django.core import mail
from django.utils import timezone
from datetime import timedelta
from .models import NewsletterSubscription
from .forms import NewsletterForm

# Create your tests here.


class NewsletterSubscriptionModelTests(TestCase):
    def setUp(self):
        self.subscription = NewsletterSubscription.objects.create(
            email='test@example.com'
        )

    def test_subscription_creation(self):
        """Test that a subscription can be created"""
        self.assertEqual(self.subscription.email, 'test@example.com')
        self.assertFalse(self.subscription.is_active)  # Should be inactive by default
        self.assertIsNotNone(self.subscription.date_subscribed)

    def test_subscription_string_representation(self):
        """Test the string representation of the subscription"""
        self.assertEqual(str(self.subscription), 'test@example.com')

    def test_token_generation(self):
        """Test that a confirmation token is generated correctly"""
        token = self.subscription.generate_confirmation_token()
        self.assertIsNotNone(token)
        self.assertEqual(len(token), 64)
        self.assertIsNotNone(self.subscription.confirmation_sent)

    def test_subscription_confirmation(self):
        """Test that subscription confirmation works correctly"""
        self.subscription.confirm_subscription()
        self.assertTrue(self.subscription.is_active)
        self.assertIsNotNone(self.subscription.confirmed_at)


class NewsletterFormTests(TestCase):
    def test_valid_form(self):
        """Test form with valid data"""
        form_data = {'email': 'test@example.com'}
        form = NewsletterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        """Test form with invalid data"""
        form_data = {'email': 'invalid-email'}
        form = NewsletterForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_duplicate_email(self):
        """Test form with duplicate email"""
        NewsletterSubscription.objects.create(email='test@example.com')
        form_data = {'email': 'test@example.com'}
        form = NewsletterForm(data=form_data)
        self.assertFalse(form.is_valid())


class NewsletterViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('newsletter:newsletter_signup')
        self.valid_data = {
            'email': 'test@example.com'
        }
        self.invalid_data = {
            'email': 'invalid-email'
        }

        # Set up session
        self.request = HttpRequest()
        session_middleware = SessionMiddleware(lambda x: None)
        message_middleware = MessageMiddleware(lambda x: None)
        session_middleware.process_request(self.request)
        message_middleware.process_request(self.request)
        self.request.session.save()

    def test_signup_page_GET(self):
        """Test GET request to signup page"""
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'newsletter/signup.html')
        self.assertIsInstance(response.context['form'], NewsletterForm)

    def test_signup_POST_valid_data(self):
        """Test POST request with valid data"""
        response = self.client.post(self.signup_url, self.valid_data)
        self.assertEqual(response.status_code, 200)

        # Check that subscription was created but not active
        subscription = NewsletterSubscription.objects.get(email='test@example.com')
        self.assertFalse(subscription.is_active)
        self.assertIsNotNone(subscription.confirmation_token)

        # Check that confirmation email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Confirm Your Newsletter Subscription')

    def test_signup_POST_invalid_data(self):
        """Test POST request with invalid data"""
        response = self.client.post(self.signup_url, self.invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(NewsletterSubscription.objects.filter(
            email='invalid-email'
        ).exists())

    def test_confirm_subscription_valid_token(self):
        """Test confirmation with valid token"""
        # Create subscription and get token
        subscription = NewsletterSubscription.objects.create(email='test@example.com')
        token = subscription.generate_confirmation_token()

        # Confirm subscription
        response = self.client.get(reverse('newsletter:confirm_subscription', args=[token]))
        self.assertEqual(response.status_code, 302)  # Should redirect

        # Check subscription is active
        subscription.refresh_from_db()
        self.assertTrue(subscription.is_active)
        self.assertIsNotNone(subscription.confirmed_at)

        # Check welcome email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Welcome to Our Newsletter')

    def test_confirm_subscription_invalid_token(self):
        """Test confirmation with invalid token"""
        response = self.client.get(reverse('newsletter:confirm_subscription', args=['invalid-token']))
        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertFalse(NewsletterSubscription.objects.filter(is_active=True).exists())

    def test_confirm_subscription_expired_token(self):
        """Test confirmation with expired token"""
        # Create subscription with old token
        subscription = NewsletterSubscription.objects.create(email='test@example.com')
        token = subscription.generate_confirmation_token()
        subscription.confirmation_sent = timezone.now() - timedelta(hours=25)
        subscription.save()

        # Try to confirm
        response = self.client.get(reverse('newsletter:confirm_subscription', args=[token]))
        self.assertEqual(response.status_code, 302)  # Should redirect

        # Check subscription is still inactive
        subscription.refresh_from_db()
        self.assertFalse(subscription.is_active)
