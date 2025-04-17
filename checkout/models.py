from django.db import models
from django.conf import settings
from products.models import Product
from decimal import Decimal
import uuid
import time
from django.utils import timezone

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='checkout_orders')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    stripe_id = models.CharField(max_length=250, blank=True)
    order_number = models.CharField(max_length=32, unique=True, editable=False)
    
    # New fields for order tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    shipping_date = models.DateTimeField(null=True, blank=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    estimated_delivery = models.DateTimeField(null=True, blank=True)
    tracking_number = models.CharField(max_length=50, blank=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=50, default='card')

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
        ]

    def __str__(self):
        return f'Order {self.order_number}'

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

    def get_total_cost_with_shipping(self):
        return self.get_total_cost() + self.shipping_cost

    def generate_order_number(self):
        """Generate a unique order number using timestamp and UUID"""
        timestamp = int(time.time() * 1000)
        unique_id = uuid.uuid4().hex[:8]
        return f"{timestamp}{unique_id}"

    @property
    def status_color(self):
        """Return the appropriate Bootstrap color class for the status"""
        colors = {
            'pending': 'secondary',
            'processing': 'warning',
            'shipped': 'info',
            'delivered': 'success',
            'cancelled': 'danger',
        }
        return colors.get(self.status, 'secondary')

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        
        # Update shipping date when status changes to shipped
        if self.status == 'shipped' and not self.shipping_date:
            self.shipping_date = timezone.now()
        
        # Update delivery date when status changes to delivered
        if self.status == 'delivered' and not self.delivery_date:
            self.delivery_date = timezone.now()
        
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', related_name='checkout_order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price * self.quantity

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id 