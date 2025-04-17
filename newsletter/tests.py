from django.test import TestCase, Client
from django.urls import reverse
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
        self.assertTrue(self.subscription.is_active)
        self.assertIsNotNone(self.subscription.date_subscribed)

    def test_subscription_string_representation(self):
        """Test the string representation of the subscription"""
        self.assertEqual(str(self.subscription), 'test@example.com')

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
        self.signup_url = reverse('newsletter_signup')

    def test_signup_page_GET(self):
        """Test GET request to signup page"""
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'newsletter/signup.html')
        self.assertIsInstance(response.context['form'], NewsletterForm)

    def test_signup_POST_valid_data(self):
        """Test POST request with valid data"""
        response = self.client.post(self.signup_url, {
            'email': 'test@example.com'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(NewsletterSubscription.objects.filter(
            email='test@example.com'
        ).exists())

    def test_signup_POST_invalid_data(self):
        """Test POST request with invalid data"""
        response = self.client.post(self.signup_url, {
            'email': 'invalid-email'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(NewsletterSubscription.objects.filter(
            email='invalid-email'
        ).exists())

    def test_signup_POST_duplicate_email(self):
        """Test POST request with duplicate email"""
        NewsletterSubscription.objects.create(email='test@example.com')
        response = self.client.post(self.signup_url, {
            'email': 'test@example.com'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            NewsletterSubscription.objects.filter(email='test@example.com').count(),
            1
        )