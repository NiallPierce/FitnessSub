from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest
from products.models import Product, Category
from cart.models import Cart, CartItem
from .models import Order, OrderItem, Payment
from decimal import Decimal


class OrderManagementTests(TestCase):
    def setUp(self):
        # Create a test user
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

        # Create test products
        self.product1 = Product.objects.create(
            category=self.category,
            name='Test Product 1',
            description='Test Description 1',
            price=10.00,
            rating=4.5,
            image=None
        )

        self.product2 = Product.objects.create(
            category=self.category,
            name='Test Product 2',
            description='Test Description 2',
            price=20.00,
            rating=4.0,
            image=None
        )

        # Initialize the client
        self.client = Client()

        # Set up session
        self.request = HttpRequest()
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(self.request)
        self.request.session.save()

        # Create a test cart
        self.cart = Cart.objects.create(user=self.user)

        # Add items to cart
        CartItem.objects.create(
            cart=self.cart,
            product=self.product1,
            quantity=2
        )
        CartItem.objects.create(
            cart=self.cart,
            product=self.product2,
            quantity=1
        )

        # Create a test order
        self.order = Order.objects.create(
            user=self.user,
            first_name='Test',
            last_name='User',
            email='test@example.com',
            address='123 Test St',
            postal_code='12345',
            city='Test City',
            country='Test Country',
            paid=True
        )

        # Add items to order
        OrderItem.objects.create(
            order=self.order,
            product=self.product1,
            price=10.00,
            quantity=2
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product2,
            price=20.00,
            quantity=1
        )

        # Create a test payment
        self.payment = Payment.objects.create(
            order=self.order,
            payment_id='test_payment_id',
            payment_method='card',
            amount_paid=40.00,
            status='completed'
        )

    def test_order_creation(self):
        """Test that an order can be created successfully"""
        order = Order.objects.create(
            user=self.user,
            first_name='New',
            last_name='Order',
            email='new@example.com',
            address='456 New St',
            postal_code='67890',
            city='New City',
            country='New Country',
            paid=False
        )
        self.assertIsNotNone(order)
        self.assertEqual(order.user, self.user)
        self.assertFalse(order.paid)

    def test_order_status_update(self):
        """Test that order status can be updated"""
        self.order.status = 'processing'
        self.order.save()
        self.assertEqual(self.order.status, 'processing')

    def test_order_history_view(self):
        """Test that order history view works correctly"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('checkout:order_history'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.order.order_number)

    def test_order_detail_view(self):
        """Test that order detail view works correctly"""
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('checkout:order_detail', args=[self.order.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.order.order_number)

    def test_order_payment_status(self):
        """Test that payment status is correctly associated with order"""
        self.assertEqual(self.payment.order, self.order)
        self.assertEqual(self.payment.status, 'completed')

    def test_order_item_cost_calculation(self):
        """Test that order item cost is calculated correctly"""
        order_item = OrderItem.objects.get(
            order=self.order,
            product=self.product1
        )
        self.assertEqual(order_item.get_cost(), Decimal('20.00'))

    def test_order_unauthorized_access(self):
        """Test that unauthorized users cannot access order details"""
        response = self.client.get(
            reverse('checkout:order_detail', args=[self.order.id])
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login
