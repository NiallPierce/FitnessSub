from django.contrib import admin
from .models import Order, OrderItem, Payment

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product', 'quantity', 'product_price', 'ordered')
    extra = 0

class PaymentInline(admin.TabularInline):
    model = Payment
    readonly_fields = ('payment_id', 'payment_method', 'amount_paid', 'status')
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'first_name', 'last_name', 'order_total', 
                   'status', 'is_ordered', 'created_at')
    list_filter = ('status', 'is_ordered', 'created_at')
    search_fields = ('order_number', 'first_name', 'last_name', 'email')
    list_editable = ('status', 'is_ordered')
    inlines = [OrderItemInline, PaymentInline]
    readonly_fields = ('order_number', 'user', 'first_name', 'last_name', 'email', 
                      'phone', 'address_line_1', 'address_line_2', 'city', 'state', 
                      'country', 'order_note', 'order_total', 'tax', 'ip')
    ordering = ('-created_at',)

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'order', 'payment_method', 'amount_paid', 
                   'status', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('payment_id', 'order__order_number')
    readonly_fields = ('payment_id', 'order', 'payment_method', 'amount_paid', 
                      'status', 'created_at')
    ordering = ('-created_at',)

admin.site.register(Order, OrderAdmin)
admin.site.register(Payment, PaymentAdmin)