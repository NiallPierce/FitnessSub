from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Product, Category
from decimal import Decimal


class ProductTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create test categories
        self.category1 = Category.objects.create(
            name='Test Category 1',
            friendly_name='Test Category 1'
        )
        self.category2 = Category.objects.create(
            name='Test Category 2',
            friendly_name='Test Category 2'
        )

        # Create test products
        self.product1 = Product.objects.create(
            category=self.category1,
            name='Test Product 1',
            description='Test Description 1',
            price=99.99,
            rating=4.5,
            stock=10
        )
        self.product2 = Product.objects.create(
            category=self.category2,
            name='Test Product 2',
            description='Test Description 2',
            price=149.99,
            rating=3.5,
            stock=5
        )

    def test_product_list_view(self):
        """Test that the product list view returns a 200 status code"""
        response = self.client.get(reverse('products:products'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product/products.html')
        self.assertContains(response, 'Test Product 1')
        self.assertContains(response, 'Test Product 2')

    def test_product_detail_view(self):
        """Test that the product detail view returns a 200 status code"""
        response = self.client.get(
            reverse('products:product_detail', args=[self.product1.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product/product_detail.html')
        self.assertContains(response, 'Test Product 1')
        self.assertContains(response, 'Test Description 1')

    def test_product_filtering_by_category(self):
        """Test that product filtering by category works"""
        response = self.client.get(
            reverse('products:products'),
            {'category': self.category1.name}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Product 1')
        self.assertNotContains(response, 'Test Product 2')

    def test_product_sorting(self):
        """Test that product sorting works"""
        response = self.client.get(
            reverse('products:products'),
            {'sort': 'price'}
        )
        self.assertEqual(response.status_code, 200)
        products = list(response.context['products'])
        self.assertEqual(products[0].price, Decimal('99.99'))
        self.assertEqual(products[1].price, Decimal('149.99'))

    def test_product_rating_filtering(self):
        """Test that product filtering by rating works"""
        response = self.client.get(
            reverse('products:products'),
            {'rating': '4'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Product 1')
        self.assertNotContains(response, 'Test Product 2')

    def test_product_search(self):
        """Test that product search works"""
        response = self.client.get(
            reverse('products:products'),
            {'q': 'Test Product 1'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Product 1')
        self.assertNotContains(response, 'Test Product 2')

    def test_product_model_str(self):
        """Test the string representation of the Product model"""
        self.assertEqual(str(self.product1), 'Test Product 1')

    def test_category_model_str(self):
        """Test the string representation of the Category model"""
        self.assertEqual(str(self.category1), 'Test Category 1')

    def test_category_friendly_name(self):
        """Test the friendly name property of the Category model"""
        self.assertEqual(self.category1.friendly_name, 'Test Category 1')
