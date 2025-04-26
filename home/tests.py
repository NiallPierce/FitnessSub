from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from products.models import Product, Category
from django.test import override_settings


class UsabilityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create a test category
        self.category = Category.objects.create(
            name='Test Category',
            friendly_name='Test Category'
        )

        # Create a test product
        self.product = Product.objects.create(
            category=self.category,
            name='Test Product',
            description='Test Description',
            price=99.99,
            rating=4.5,
            image=None
        )

        # Get or create the default site
        self.site = Site.objects.get_or_create(
            id=1,
            defaults={
                'domain': 'example.com',
                'name': 'example.com'
            }
        )[0]

    def test_navigation_links(self):
        """Test that all navigation links are present and working"""
        response = self.client.get(reverse('home:index'))
        self.assertEqual(response.status_code, 200)

        # Check for main navigation links
        self.assertContains(response, 'Home')
        self.assertContains(response, 'Products')
        self.assertContains(response, 'Subscriptions')
        self.assertContains(response, 'Newsletter')
        self.assertContains(response, 'Community')

        # Check for cart icon
        self.assertContains(response, 'fa-shopping-cart')

        # Check for user-specific links when logged in
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('home:index'))
        self.assertContains(response, self.user.username)  # Username in dropdown
        self.assertContains(response, 'Logout')

    def test_form_validation_feedback(self):
        """Test that form validation provides clear feedback"""
        # Test login form validation
        response = self.client.post(reverse('accounts:login'), {
            'login': '',
            'password': ''
        })
        self.assertEqual(response.status_code, 200)  # Should stay on the same page
        self.assertTrue('form' in response.context)  # Should have a form in context
        self.assertTrue(response.context['form'].errors)  # Should have errors

        # Test registration form validation
        response = self.client.post(reverse('accounts:signup'), {
            'username': '',
            'email': 'invalid-email',
            'password1': 'short',
            'password2': 'different'
        })
        self.assertEqual(response.status_code, 200)  # Should stay on the same page
        self.assertTrue('form' in response.context)  # Should have a form in context
        self.assertTrue(response.context['form'].errors)  # Should have errors

    def test_error_messages(self):
        """Test that error messages are displayed appropriately"""
        # Test 404 page
        response = self.client.get('/nonexistent-page/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

        # Test permission denied
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login

    def test_success_messages(self):
        """Test that success messages are displayed appropriately"""
        # Test successful login using Django's built-in login
        response = self.client.post(reverse('accounts:login'), {
            'username': self.user.username,
            'password': 'testpass123'
        }, follow=True)
        self.assertEqual(response.status_code, 200)

        # Verify we can access a protected page after login
        response = self.client.get(reverse('home:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)

        # Test successful registration using Django's built-in registration
        response = self.client.post(reverse('accounts:signup'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newuserpass123',
            'password2': 'newuserpass123'
        }, follow=True)
        self.assertEqual(response.status_code, 200)

        # Verify the new user can log in
        self.client.login(username='newuser', password='newuserpass123')
        response = self.client.get(reverse('home:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'newuser')


class ResponsivenessTests(TestCase):
    def setUp(self):
        self.client = Client()

    @override_settings(DEBUG=True)
    def test_mobile_view(self):
        """Test that the site is responsive on mobile devices"""
        # Test with mobile user agent
        response = self.client.get(
            reverse('home:index'),
            HTTP_USER_AGENT='Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base.html')

    @override_settings(DEBUG=True)
    def test_tablet_view(self):
        """Test that the site is responsive on tablet devices"""
        # Test with tablet user agent
        response = self.client.get(
            reverse('home:index'),
            HTTP_USER_AGENT='Mozilla/5.0 (iPad; CPU OS 10_3 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E5239e Safari/602.1'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base.html')

    @override_settings(DEBUG=True)
    def test_desktop_view(self):
        """Test that the site displays correctly on desktop"""
        response = self.client.get(
            reverse('home:index'),
            HTTP_USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base.html')
