from django.test import TestCase, Client
from django.urls import reverse
from products.models import Product, Category
from .models import Cart, CartItem
from .forms import CartAddProductForm

class CartTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(
            name='Test Category',
            friendly_name='Test Category'
        )
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=10.00,
            category=self.category
        )
        self.cart_url = reverse('cart:view_cart')
        self.add_cart_url = reverse('cart:add_cart', args=[self.product.id])
        self.remove_cart_url = reverse('cart:remove_cart', args=[self.product.id])
        self.remove_item_url = reverse('cart:remove_cart_item', args=[self.product.id])

    def test_add_to_cart(self):
        """Test adding a product to cart"""
        response = self.client.post(self.add_cart_url, {
            'quantity': 2,
            'override': False
        })
        self.assertEqual(response.status_code, 302)  # Redirect after adding
        cart = Cart.objects.get(cart_id=self.client.session.session_key)
        cart_item = CartItem.objects.get(cart=cart, product=self.product)
        self.assertEqual(cart_item.quantity, 2)

    def test_update_cart_quantity(self):
        """Test updating cart item quantity"""
        # First add item
        self.client.post(self.add_cart_url, {
            'quantity': 1,
            'override': False
        })
        # Then update quantity
        response = self.client.post(self.add_cart_url, {
            'quantity': 3,
            'override': True
        })
        self.assertEqual(response.status_code, 302)
        cart = Cart.objects.get(cart_id=self.client.session.session_key)
        cart_item = CartItem.objects.get(cart=cart, product=self.product)
        self.assertEqual(cart_item.quantity, 3)

    def test_remove_from_cart(self):
        """Test removing one item from cart"""
        # First add item
        self.client.post(self.add_cart_url, {
            'quantity': 2,
            'override': False
        })
        # Then remove one
        response = self.client.get(self.remove_cart_url)
        self.assertEqual(response.status_code, 302)
        cart = Cart.objects.get(cart_id=self.client.session.session_key)
        cart_item = CartItem.objects.get(cart=cart, product=self.product)
        self.assertEqual(cart_item.quantity, 1)

    def test_remove_cart_item(self):
        """Test removing entire cart item"""
        # First add item
        self.client.post(self.add_cart_url, {
            'quantity': 2,
            'override': False
        })
        # Then remove item completely
        response = self.client.get(self.remove_item_url)
        self.assertEqual(response.status_code, 302)
        cart = Cart.objects.get(cart_id=self.client.session.session_key)
        self.assertFalse(CartItem.objects.filter(cart=cart, product=self.product).exists())

    def test_view_cart(self):
        """Test viewing cart page"""
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cart/cart.html')

    def test_cart_context_processor(self):
        """Test cart context processor"""
        # Add item to cart
        self.client.post(self.add_cart_url, {
            'quantity': 2,
            'override': False
        })
        # Get cart contents through context processor
        response = self.client.get(self.cart_url)
        self.assertIn('cart_items', response.context)
        self.assertIn('total', response.context)
        self.assertIn('quantity', response.context)
        self.assertEqual(response.context['quantity'], 2)
        self.assertEqual(response.context['total'], 20.00)  # 2 items * $10.00
