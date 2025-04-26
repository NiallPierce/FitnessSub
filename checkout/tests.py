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
from unittest.mock import patch
import json
import stripe

class CheckoutTests(TestCase):
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
            first_name='Test',
            last_name='User',
            email='test@example.com',
            address='123 Test St',
            postal_code='12345',
            city='Test City',
            country='US',
            order_number='TEST123',
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
        """Test that checkout view works with items in cart"""
        self.client.login(username='testuser', password='testpass123')
        session = self.client.session
        session['cart'] = {str(self.product1.id): {'quantity': 2, 'price': str(self.product1.price)},
                          str(self.product2.id): {'quantity': 1, 'price': str(self.product2.price)}}
        session.save()
        response = self.client.get(reverse('checkout:checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'checkout/checkout.html')

    def test_checkout_with_empty_cart(self):
        """Test that checkout redirects to cart with empty cart"""
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
            'country': 'US'
        })
        self.assertEqual(response.status_code, 200)  # Should return JSON response
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertIn('clientSecret', response_data)

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
        response = self.client.get(reverse('profiles:order_history', args=[self.order.order_number]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.order.order_number)
        self.assertContains(response, self.product1.name)
        self.assertContains(response, self.product2.name)

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
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        self.client.login(username='otheruser', password='otherpass123')
        
        response = self.client.get(reverse('checkout:payment_success', args=[self.order.order_number]))
        self.assertEqual(response.status_code, 404)  # Should not be able to access other user's order

    @patch('checkout.views.stripe.PaymentIntent.create')
    def test_stripe_payment_intent_creation(self, mock_payment_intent):
        """Test that a Stripe PaymentIntent is created correctly"""
        # Create a proper mock PaymentIntent object
        mock_intent = type('PaymentIntent', (), {
            'id': 'test_payment_intent_id',
            'client_secret': 'test_client_secret',
            'status': 'requires_payment_method'
        })()
        mock_payment_intent.return_value = mock_intent
        
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
            'country': 'US'
        })
        
        if response.status_code == 400:
            print("Form errors:", json.loads(response.content))
        
        self.assertEqual(response.status_code, 200)  # Should return JSON response
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['clientSecret'], 'test_client_secret')
        mock_payment_intent.assert_called_once()

    def test_payment_success_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('checkout:payment_success', args=[self.order.order_number]))
        # Expecting redirect to order history
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profiles:order_history', args=[self.order.order_number]))

    def test_payment_cancel_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('checkout:payment_cancel'))
        # Expecting redirect to cart
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('cart:view_cart'))

    def test_payment_success_unauthorized(self):
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        self.client.login(username='otheruser', password='testpass123')
        response = self.client.get(reverse('checkout:payment_success', args=[self.order.order_number]))
        # Expecting 404 for unauthorized access
        self.assertEqual(response.status_code, 404)

    def test_payment_success_nonexistent_order(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('checkout:payment_success', args=['NONEXISTENT']))
        # Expecting redirect to checkout for nonexistent order
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('checkout:checkout'))

    @patch('checkout.views.stripe.PaymentIntent.retrieve')
    def test_payment_success_flow(self, mock_payment_retrieve):
        """Test the complete payment success flow"""
        # Mock the Stripe API response
        mock_payment_retrieve.return_value = stripe.PaymentIntent.construct_from({
            'id': 'test_payment_intent',
            'status': 'succeeded',
            'payment_method_types': ['card'],
            'amount': 4000,  # $40.00
            'currency': 'usd',
            'customer': None,
            'metadata': {}
        }, 'test_key')

        self.client.login(username='testuser', password='testpass123')
        
        # Create a cart and add items
        cart = Cart.objects.create(cart_id=self.client.session.session_key)
        CartItem.objects.create(
            cart=cart,
            product=self.product1,
            quantity=2
        )
        
        # Save the session
        session = self.client.session
        session.save()
        
        # Create a test order with stripe_id
        order = Order.objects.create(
            user=self.user,
            first_name='Test',
            last_name='User',
            email='test@example.com',
            address='123 Test St',
            postal_code='12345',
            city='Test City',
            country='Test Country',
            order_number='TEST456',
            stripe_id='test_payment_intent'
        )
        
        # Add items to the order
        OrderItem.objects.create(
            order=order,
            product=self.product1,
            price=self.product1.price,
            quantity=2
        )
        
        # Simulate successful payment
        response = self.client.get(reverse('checkout:payment_success', args=[order.order_number]))
        self.assertEqual(response.status_code, 302)  # Should redirect to order history
        
        # Check that order is marked as paid
        order.refresh_from_db()
        self.assertTrue(order.paid)
        
        # Check that payment record was created
        payment = Payment.objects.get(order=order)
        self.assertEqual(payment.status, 'completed')
        
        # Check that cart was cleared
        self.assertFalse(Cart.objects.filter(cart_id=session.session_key).exists())

    def test_payment_cancel_flow(self):
        """Test the payment cancellation flow"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('checkout:payment_cancel'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('cart:view_cart'))

    @patch('checkout.views.stripe.Webhook.construct_event')
    def test_webhook_handling(self, mock_construct_event):
        """Test Stripe webhook handling"""
        # Create a test order
        order = Order.objects.create(
            user=self.user,
            first_name='Test',
            last_name='User',
            email='test@example.com',
            address='123 Test St',
            postal_code='12345',
            city='Test City',
            country='Test Country',
            stripe_id='test_payment_intent'
        )
        
        # Create a test payment
        payment = Payment.objects.create(
            order=order,
            payment_id='test_payment_id',
            payment_method='card',
            amount_paid=order.get_total_cost(),
            status='pending'
        )
        
        # Mock the Stripe webhook event
        mock_construct_event.return_value = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'payment_intent': 'test_payment_intent',
                    'metadata': {
                        'order_id': str(order.id)
                    }
                }
            }
        }
        
        # Simulate webhook payload
        webhook_payload = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'payment_intent': 'test_payment_intent',
                    'metadata': {
                        'order_id': str(order.id)
                    }
                }
            }
        }
        
        response = self.client.post(
            reverse('checkout:stripe_webhook'),
            data=json.dumps(webhook_payload),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_signature'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Check that payment status was updated
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'completed')
        
        # Check that order was marked as paid
        order.refresh_from_db()
        self.assertTrue(order.paid)

    def test_payment_error_handling(self):
        """Test payment error handling"""
        self.client.login(username='testuser', password='testpass123')
        
        # Test with invalid payment data
        response = self.client.post(reverse('checkout:checkout'), {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'invalid-email',
            'address': '123 Test St',
            'postal_code': '12345',
            'city': 'Test City',
            'country': 'Test Country'
        })
        
        self.assertEqual(response.status_code, 302)  # Should redirect to payment page
        self.assertFalse(Order.objects.filter(email='invalid-email').exists())
