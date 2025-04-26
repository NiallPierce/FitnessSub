from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from profiles.models import UserProfile
from checkout.models import Order
from products.models import Product
import os
import shutil
from PIL import Image
import tempfile

class ProfileTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create a test profile (should be created automatically via signal)
        self.profile = UserProfile.objects.get(user=self.user)
        
        # Create a temporary test image
        self.image = self.create_test_image()
        
        # Create a test product
        self.product = Product.objects.create(
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
        
        # Profile update data
        self.profile_data = {
            'phone_number': '1234567890',
            'address_line_1': '123 Test St',
            'address_line_2': 'Apt 4B',
            'city': 'Test City',
            'state': 'Test State',
            'country': 'Test Country',
            'postal_code': '12345',
            'newsletter_subscription': True
        }

    def create_test_image(self):
        """Helper method to create a test image"""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            image = Image.new('RGB', (100, 100), 'white')
            image.save(f, 'JPEG')
        return f.name

    def tearDown(self):
        """Clean up after tests"""
        # Remove test image
        if hasattr(self, 'image') and os.path.exists(self.image):
            os.unlink(self.image)
        
        # Clean up any uploaded files
        if os.path.exists(os.path.join(settings.MEDIA_ROOT, f'user_{self.user.id}')):
            shutil.rmtree(os.path.join(settings.MEDIA_ROOT, f'user_{self.user.id}'))

    def test_profile_creation(self):
        """Test that profile is created automatically when user is created"""
        new_user = User.objects.create_user(
            username='newuser',
            email='newuser@example.com',
            password='newpass123'
        )
        self.assertTrue(UserProfile.objects.filter(user=new_user).exists())

    def test_profile_update(self):
        """Test profile update functionality"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('profiles:profile'), self.profile_data)
        self.assertEqual(response.status_code, 200)  # Should stay on same page after update
        
        # Refresh profile from database
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.phone_number, '1234567890')
        self.assertEqual(self.profile.address_line_1, '123 Test St')
        self.assertTrue(self.profile.newsletter_subscription)

    def test_profile_picture_upload(self):
        """Test profile picture upload and resizing"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create the POST data with image
        with open(self.image, 'rb') as img:
            post_data = self.profile_data.copy()
            post_data['profile_picture'] = SimpleUploadedFile(
                name='test_image.jpg',
                content=img.read(),
                content_type='image/jpeg'
            )
            response = self.client.post(reverse('profiles:profile'), post_data)
        
        self.assertEqual(response.status_code, 200)  # Should stay on same page after upload
        
        # Refresh profile from database
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.profile_picture)
        
        # Check if image was resized
        with Image.open(self.profile.profile_picture.path) as img:
            self.assertLessEqual(img.height, 300)
            self.assertLessEqual(img.width, 300)

    def test_profile_view_authentication(self):
        """Test that profile view requires authentication"""
        # Test without login
        response = self.client.get(reverse('profiles:profile'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login
        
        # Test with login
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profiles:profile'))
        self.assertEqual(response.status_code, 200)

    def test_order_history_view(self):
        """Test order history view"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profiles:order_history', args=[self.order.order_number]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'checkout/checkout_success.html')

    def test_profile_data_validation(self):
        """Test profile data validation"""
        self.client.login(username='testuser', password='testpass123')
        
        # Test with invalid phone number
        invalid_data = self.profile_data.copy()
        invalid_data['phone_number'] = 'invalid-phone'
        response = self.client.post(reverse('profiles:profile'), invalid_data)
        self.assertEqual(response.status_code, 200)  # Should stay on same page
        
        # Test with invalid postal code
        invalid_data = self.profile_data.copy()
        invalid_data['postal_code'] = 'invalid-postal'
        response = self.client.post(reverse('profiles:profile'), invalid_data)
        self.assertEqual(response.status_code, 200)

    def test_newsletter_subscription_toggle(self):
        """Test newsletter subscription toggle"""
        self.client.login(username='testuser', password='testpass123')
        
        # Test subscribing
        response = self.client.post(reverse('profiles:profile'), {
            **self.profile_data,
            'newsletter_subscription': True
        })
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.newsletter_subscription)
        
        # Test unsubscribing
        response = self.client.post(reverse('profiles:profile'), {
            **self.profile_data,
            'newsletter_subscription': False
        })
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.newsletter_subscription) 