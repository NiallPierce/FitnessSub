from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from profiles.models import UserProfile
from checkout.models import Order
from products.models import Product, Category
import os
import shutil
from PIL import Image
import tempfile

class DataManagementTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create a test profile
        self.profile = UserProfile.objects.get(user=self.user)
        
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
            price=10.00,
            stock=10
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
            paid=True
        )

    def test_user_profile_creation(self):
        """Test that user profile is created automatically"""
        new_user = User.objects.create_user(
            username='newuser',
            email='newuser@example.com',
            password='newpass123'
        )
        self.assertTrue(UserProfile.objects.filter(user=new_user).exists())

    def test_user_profile_update(self):
        """Test that user profile can be updated"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('profiles:profile'), {
            'phone_number': '1234567890',
            'address_line_1': '123 Test St',
            'address_line_2': 'Apt 4B',
            'city': 'Test City',
            'state': 'Test State',
            'country': 'Test Country',
            'postal_code': '12345',
            'newsletter_subscription': True
        })
        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.phone_number, '1234567890')
        self.assertEqual(self.profile.address_line_1, '123 Test St')
        self.assertTrue(self.profile.newsletter_subscription)

    def test_order_data_relationships(self):
        """Test relationships between order, user, and products"""
        # Create order items
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            price=self.product.price,
            quantity=2
        )
        
        # Test relationships
        self.assertEqual(self.order.user, self.user)
        self.assertEqual(self.order.items.count(), 1)
        self.assertEqual(self.order.items.first().product, self.product)

    def test_data_validation(self):
        """Test data validation in profile updates"""
        self.client.login(username='testuser', password='testpass123')
        
        # Test invalid phone number
        response = self.client.post(reverse('profiles:profile'), {
            'phone_number': 'invalid',
            'address_line_1': '123 Test St',
            'city': 'Test City',
            'country': 'Test Country',
            'postal_code': '12345'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enter a valid phone number')
        
        # Test invalid postal code
        response = self.client.post(reverse('profiles:profile'), {
            'phone_number': '1234567890',
            'address_line_1': '123 Test St',
            'city': 'Test City',
            'country': 'Test Country',
            'postal_code': 'invalid'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enter a valid postal code')

    def test_data_deletion(self):
        """Test that related data is handled properly on deletion"""
        # Create an order with items
        order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            price=self.product.price,
            quantity=2
        )
        
        # Delete the order
        self.order.delete()
        
        # Check that order items are also deleted
        self.assertFalse(OrderItem.objects.filter(id=order_item.id).exists())
        
        # Check that user profile is not deleted when user is deleted
        profile_id = self.profile.id
        self.user.delete()
        self.assertFalse(UserProfile.objects.filter(id=profile_id).exists())

    def test_data_integrity(self):
        """Test data integrity constraints"""
        # Test unique email constraint
        with self.assertRaises(Exception):
            User.objects.create_user(
                username='anotheruser',
                email='test@example.com',  # Same email as existing user
                password='anotherpass123'
            )
        
        # Test required fields
        with self.assertRaises(Exception):
            Order.objects.create(
                user=self.user,
                # Missing required fields
            ) 