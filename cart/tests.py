from django.test import TestCase, Client
from django.urls import reverse
from products.models import Product, Category
from .models import Cart, CartItem
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.http import HttpRequest

class CartTests(TestCase):
    def setUp(self):
        # Create a test product
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=10.00,
            stock=10
        )
        
        # Create a session and cart
        self.client = Client()
        session = self.client.session
        session.create()
        session.save()
        
        self.cart = Cart.objects.create(cart_id=session.session_key)
        
    def _get_cart(self):
        """Helper method to get or create a cart for the current session"""
        session = self.client.session
        if not session.session_key:
            session.create()
            session.save()
            
        try:
            cart = Cart.objects.get(cart_id=session.session_key)
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=session.session_key)
            
        return cart
        
    def test_add_to_cart(self):
        cart = self._get_cart()
        response = self.client.post(
            reverse('cart:cart_add', args=[self.product.id]),
            {'quantity': 1, 'override': False},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(CartItem.objects.filter(product=self.product, cart=cart).exists())

    def test_update_cart(self):
        cart = self._get_cart()
        # First add an item
        cart_item = CartItem.objects.create(
            product=self.product,
            quantity=1,
            cart=cart
        )
        
        response = self.client.post(
            reverse('cart:cart_add', args=[self.product.id]),
            {'quantity': 2, 'override': True},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 2)

    def test_remove_from_cart(self):
        cart = self._get_cart()
        # First add an item
        cart_item = CartItem.objects.create(
            product=self.product,
            quantity=2,
            cart=cart
        )
        
        response = self.client.post(
            reverse('cart:remove_cart', args=[self.product.id]),
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 1)

    def test_view_cart(self):
        cart = self._get_cart()
        response = self.client.get(reverse('cart:view_cart'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('total', response.context)
        self.assertIn('quantity', response.context)
        self.assertIn('cart_items', response.context)

    def test_cart_total(self):
        cart = self._get_cart()
        # Add two items
        CartItem.objects.create(
            product=self.product,
            quantity=2,
            cart=cart
        )
        
        response = self.client.get(reverse('cart:view_cart'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total'], 20.00)

    def test_empty_cart(self):
        cart = self._get_cart()
        response = self.client.get(reverse('cart:view_cart'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total'], 0)
