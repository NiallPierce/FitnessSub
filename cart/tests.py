from django.test import TestCase, Client
from django.urls import reverse
from products.models import Product, Category
from django.contrib.auth.models import User

class CartTests(TestCase):
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

    def test_add_to_cart(self):
        """Test adding a product to the cart"""
        response = self.client.post(
            reverse('cart:cart_add', args=[self.product.id]),
            {'quantity': 1, 'redirect_url': reverse('products:products')}
        )
        self.assertEqual(response.status_code, 302)  # Redirect after adding to cart
        self.assertIn('cart', self.client.session)
        self.assertEqual(self.client.session['cart'][str(self.product.id)], 1)

    def test_view_cart(self):
        """Test viewing the cart"""
        # First add an item to the cart
        self.client.post(
            reverse('cart:cart_add', args=[self.product.id]),
            {'quantity': 1, 'redirect_url': reverse('products:products')}
        )
        
        # Then view the cart
        response = self.client.get(reverse('cart:view_cart'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cart/cart.html')
        self.assertContains(response, 'Test Product')

    def test_update_cart(self):
        """Test updating cart quantity"""
        # First add an item to the cart
        self.client.post(
            reverse('cart:cart_add', args=[self.product.id]),
            {'quantity': 1, 'redirect_url': reverse('products:products')}
        )
        
        # Then update the quantity
        response = self.client.post(
            reverse('cart:cart_add', args=[self.product.id]),
            {'quantity': 2, 'override': True}
        )
        self.assertEqual(response.status_code, 302)  # Redirect after update
        self.assertEqual(self.client.session['cart'][str(self.product.id)], 2)

    def test_remove_from_cart(self):
        """Test removing an item from the cart"""
        # First add an item to the cart
        self.client.post(
            reverse('cart:cart_add', args=[self.product.id]),
            {'quantity': 1, 'redirect_url': reverse('products:products')}
        )
        
        # Then remove it
        response = self.client.post(reverse('cart:remove_cart', args=[self.product.id]))
        self.assertEqual(response.status_code, 302)  # Redirect after removal
        self.assertNotIn(str(self.product.id), self.client.session['cart'])

    def test_cart_total(self):
        """Test cart total calculation"""
        # Add two items to the cart
        self.client.post(
            reverse('cart:cart_add', args=[self.product.id]),
            {'quantity': 2, 'redirect_url': reverse('products:products')}
        )
        
        response = self.client.get(reverse('cart:view_cart'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '£199.98')  # 2 * £99.99

    def test_empty_cart(self):
        """Test viewing an empty cart"""
        response = self.client.get(reverse('cart:view_cart'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your cart is empty')
