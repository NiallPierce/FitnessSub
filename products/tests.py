from django.test import TestCase, Client
from django.urls import reverse
from .models import Product, Category
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
import os

class ProductTests(TestCase):
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

    def test_product_list_view(self):
        """Test that the product list view returns a 200 status code"""
        response = self.client.get(reverse('products:products'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/products.html')
        self.assertContains(response, 'Test Product')

    def test_product_detail_view(self):
        """Test that the product detail view returns a 200 status code"""
        response = self.client.get(reverse('products:product_detail', args=[self.product.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_detail.html')
        self.assertContains(response, 'Test Product')

    def test_product_search(self):
        """Test that the product search functionality works"""
        response = self.client.get(reverse('products:products'), {'q': 'Test'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Product')

    def test_product_filtering(self):
        """Test that product filtering by category works"""
        response = self.client.get(reverse('products:products'), {'category': self.category.name}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Product')

    def test_product_creation(self):
        """Test that a new product can be created"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('products:add_product'), {
            'category': self.category.id,
            'name': 'New Test Product',
            'description': 'New Test Description',
            'price': 49.99,
            'rating': 4.0
        }, follow=True)
        self.assertEqual(response.status_code, 200)  # After redirect
        self.assertTrue(Product.objects.filter(name='New Test Product').exists())

    def test_product_update(self):
        """Test that a product can be updated"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('products:edit_product', args=[self.product.id]),
            {
                'category': self.category.id,
                'name': 'Updated Test Product',
                'description': 'Updated Test Description',
                'price': 149.99,
                'rating': 5.0
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)  # After redirect
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Updated Test Product')

    def test_product_deletion(self):
        """Test that a product can be deleted"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('products:delete_product', args=[self.product.id]), follow=True)
        self.assertEqual(response.status_code, 200)  # After redirect
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())

    def test_product_model_str(self):
        """Test the string representation of the Product model"""
        self.assertEqual(str(self.product), 'Test Product')

    def test_category_model_str(self):
        """Test the string representation of the Category model"""
        self.assertEqual(str(self.category), 'Test Category')

    def test_category_friendly_name(self):
        """Test the friendly name property of the Category model"""
        self.assertEqual(self.category.get_friendly_name(), 'Test Category')
