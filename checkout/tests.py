from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from products.models import Product, Category

class CheckoutTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
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
        
        # Initialize the client
        self.client = Client()
        
        # Add product to cart
        self.client.post(
            reverse('cart:cart_add', args=[self.product.id]),
            {'quantity': 1, 'redirect_url': reverse('products:products')}
        )

    def test_checkout_view(self):
        """Test that the checkout view returns a 200 status code"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('checkout:checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'checkout/checkout.html')
        self.assertContains(response, 'Test Product')

    def test_checkout_with_empty_cart(self):
        """Test that checkout redirects to products page with empty cart"""
        # Clear the cart
        self.client.session['cart'] = {}
        self.client.session.save()
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('checkout:checkout'))
        self.assertRedirects(response, reverse('products:products'))

    def test_checkout_form_validation(self):
        """Test checkout form validation"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('checkout:checkout'), {
            'full_name': 'Test User',
            'email': 'test@example.com',
            'phone_number': '1234567890',
            'country': 'US',
            'postcode': '12345',
            'town_or_city': 'Test City',
            'street_address1': '123 Test St',
            'county': 'Test County'
        })
        self.assertEqual(response.status_code, 200)  # Form should be invalid
        self.assertFormError(response, 'form', 'street_address2', 'This field is required.')

    def test_checkout_success(self):
        """Test successful checkout process"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('checkout:success'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'checkout/success.html')

    def test_checkout_cancel(self):
        """Test checkout cancellation"""
        response = self.client.get(reverse('checkout:cancel'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'checkout/cancel.html')
