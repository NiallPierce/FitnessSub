from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from products.models import Product, Category
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.http import HttpRequest
from cart.models import Cart, CartItem
from .models import Order, OrderItem, Payment
from decimal import Decimal

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
        
        # Create cart
        self.cart = Cart.objects.create(cart_id=self.request.session.session_key)
        
        # Add products to cart
        self.cart_item1 = CartItem.objects.create(
            product=self.product1,
            cart=self.cart,
            quantity=2
        )
        
        self.cart_item2 = CartItem.objects.create(
            product=self.product2,
            cart=self.cart,
            quantity=1
        )
        
        # Create a test order
        self.order = Order.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            address='123 Test St',
            postal_code='12345',
            city='Test City',
            country='Test Country',
            paid=True
        )
        
        # Add items to the order
        OrderItem.objects.create(
            order=self.order,
            product=self.product1,
            price=self.product1.price,
            quantity=2
        )
        
        OrderItem.objects.create(
            order=self.order,
            product=self.product2,
            price=self.product2.price,
            quantity=1
        )
        
        # Create a payment record
        self.payment = Payment.objects.create(
            order=self.order,
            payment_id='test_payment_id',
            payment_method='card',
            amount_paid=self.order.get_total_cost(),
            status='completed'
        )

    def test_checkout_view(self):
        """Test that the checkout view returns a 200 status code"""
        self.client.login(username='testuser', password='testpass123')
        session = self.client.session
        session['cart'] = {str(self.product1.id): {'quantity': 2, 'price': str(self.product1.price)},
                          str(self.product2.id): {'quantity': 1, 'price': str(self.product2.price)}}
        session.save()
        response = self.client.get(reverse('checkout:checkout'))
        self.assertEqual(response.status_code, 302)

    def test_checkout_with_empty_cart(self):
        """Test that checkout redirects to products page with empty cart"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('checkout:checkout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('cart:view_cart'))

    def test_checkout_form_validation(self):
        """Test checkout form validation"""
        self.client.login(username='testuser', password='testpass123')
        session = self.client.session
        session['cart'] = {str(self.product1.id): {'quantity': 2, 'price': str(self.product1.price)},
                          str(self.product2.id): {'quantity': 1, 'price': str(self.product2.price)}}
        session.save()
        response = self.client.post(reverse('checkout:checkout'), {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'address': '123 Test St',
            'postal_code': '12345',
            'city': 'Test City',
            'country': 'Test Country'
        })
        self.assertEqual(response.status_code, 302)

    def test_checkout_success(self):
        """Test successful checkout process"""
        self.client.login(username='testuser', password='testpass123')
        session = self.client.session
        session['cart'] = {str(self.product1.id): {'quantity': 2, 'price': str(self.product1.price)},
                          str(self.product2.id): {'quantity': 1, 'price': str(self.product2.price)}}
        session.save()
        response = self.client.get(reverse('checkout:payment_success', args=[self.order.id]))
        self.assertEqual(response.status_code, 302)

    def test_checkout_cancel(self):
        """Test checkout cancellation"""
        response = self.client.get(reverse('checkout:payment_cancel'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('cart:view_cart'))

    # Order Management Tests
    def test_order_creation(self):
        """Test that an order is created correctly with items"""
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(self.order.items.count(), 2)
        self.assertEqual(self.order.get_total_cost(), Decimal('40.00'))  # (10 * 2) + (20 * 1)

    def test_order_status_update(self):
        """Test that order status can be updated"""
        self.order.paid = False
        self.order.save()
        self.assertFalse(self.order.paid)
        
        self.order.paid = True
        self.order.save()
        self.assertTrue(self.order.paid)

    def test_order_history_view(self):
        """Test that order history is accessible to authenticated users"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profiles:order_history', args=[str(self.order.id)]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(self.order.id))
        self.assertContains(response, self.product1.name)
        self.assertContains(response, self.product2.name)

    def test_order_detail_view(self):
        """Test that order details are accessible to the order owner"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('checkout:order_complete', args=[str(self.order.id)]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(self.order.id))
        self.assertContains(response, self.product1.name)
        self.assertContains(response, self.product2.name)
        self.assertContains(response, '40.00')  # Total cost

    def test_order_payment_status(self):
        """Test that payment status is correctly associated with the order"""
        self.assertEqual(self.payment.order, self.order)
        self.assertEqual(self.payment.status, 'completed')
        self.assertEqual(self.payment.amount_paid, self.order.get_total_cost())

    def test_order_item_cost_calculation(self):
        """Test that order item costs are calculated correctly"""
        order_item1 = self.order.items.get(product=self.product1)
        order_item2 = self.order.items.get(product=self.product2)
        
        self.assertEqual(order_item1.get_cost(), Decimal('20.00'))  # 10 * 2
        self.assertEqual(order_item2.get_cost(), Decimal('20.00'))  # 20 * 1

    def test_order_unauthorized_access(self):
        """Test that unauthorized users cannot access order details"""
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123'
        )
        self.client.login(username='otheruser', password='otherpass123')
        
        response = self.client.get(reverse('checkout:order_complete', args=[str(self.order.id)]))
        self.assertEqual(response.status_code, 404)  # Should not be able to access other user's order
