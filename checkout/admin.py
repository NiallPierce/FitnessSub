from django.contrib import admin
from .models import Order, OrderItem, Payment

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product', 'price', 'quantity')
    extra = 0

class PaymentInline(admin.TabularInline):
    model = Payment
    readonly_fields = ('payment_id', 'payment_method', 'amount_paid', 'status')
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'first_name', 'last_name', 'email', 'paid', 'created')
    list_filter = ('paid', 'created')
    search_fields = ('first_name', 'last_name', 'email')
    inlines = [OrderItemInline, PaymentInline]
    readonly_fields = ('user', 'first_name', 'last_name', 'email', 'address', 
                      'postal_code', 'city', 'country', 'created', 'updated', 'paid')
    ordering = ('-created',)

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'order', 'payment_method', 'amount_paid', 
                   'status', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('payment_id', 'order__id')
    readonly_fields = ('payment_id', 'order', 'payment_method', 'amount_paid', 
                      'status', 'created_at')
    ordering = ('-created_at',)

admin.site.register(Order, OrderAdmin)
admin.site.register(Payment, PaymentAdmin)