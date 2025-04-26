import datetime
import json
import stripe
from django.conf import settings
from django.shortcuts import render, redirect, reverse, get_object_or_404, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_exempt
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from decimal import Decimal

from .forms import OrderForm
from .models import Order, OrderItem, Payment
from cart.models import Cart, CartItem
from cart.contexts import cart_contents
from .forms import OrderCreateForm
from products.models import Product

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def checkout(request):
    # Try to get cart from database first
    try:
        cart = Cart.objects.get(cart_id=request.session.session_key)
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
    except Cart.DoesNotExist:
        # If no database cart, check session cart
        cart_items = []
        if 'cart' in request.session:
            cart_items_data = request.session['cart']
            for product_id, item_data in cart_items_data.items():
                try:
                    product = Product.objects.get(id=product_id)
                    cart_items.append({
                        'product': product,
                        'quantity': item_data['quantity'],
                        'price': Decimal(item_data['price'])
                    })
                except Product.DoesNotExist:
                    continue

    if not cart_items:
        messages.warning(request, 'Your cart is empty')
        return redirect('cart:view_cart')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.save()
            
            # Create order items from cart items
            for cart_item in cart_items:
                if isinstance(cart_item, dict):
                    # Handle session-based cart items
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item['product'],
                        price=cart_item['price'],
                        quantity=cart_item['quantity']
                    )
                else:
                    # Handle database-based cart items
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        price=cart_item.product.price,
                        quantity=cart_item.quantity
                    )
            
            try:
                # Create a PaymentIntent with the order amount and currency
                intent = stripe.PaymentIntent.create(
                    amount=int(order.get_total_cost() * 100),
                    currency='usd',
                    automatic_payment_methods={
                        'enabled': True,
                    },
                    metadata={
                        'order_id': order.id
                    }
                )
                
                # Update the order with the payment intent ID
                order.stripe_id = intent.id
                order.save()
                
                # For testing purposes, if the order number starts with 'TEST', skip payment
                if order.order_number.startswith('TEST'):
                    # Mark the order as paid and redirect to success
                    order.paid = True
                    order.save()
                    return JsonResponse({
                        'success': True,
                        'order_id': order.order_number,
                        'redirect_url': reverse('checkout:payment_success', args=[order.order_number])
                    })
                
                # Return the client secret to the frontend
                return JsonResponse({
                    'success': True,
                    'clientSecret': intent.client_secret,
                    'order_id': order.order_number
                })
                
            except stripe.error.CardError as e:
                return JsonResponse({
                    'success': False,
                    'error': f'Card error: {str(e)}'
                }, status=400)
            except stripe.error.RateLimitError as e:
                return JsonResponse({
                    'success': False,
                    'error': 'Rate limit error. Please try again later.'
                }, status=400)
            except stripe.error.InvalidRequestError as e:
                return JsonResponse({
                    'success': False,
                    'error': f'Invalid request: {str(e)}'
                }, status=400)
            except stripe.error.AuthenticationError as e:
                return JsonResponse({
                    'success': False,
                    'error': 'Authentication error. Please contact support.'
                }, status=400)
            except stripe.error.APIConnectionError as e:
                return JsonResponse({
                    'success': False,
                    'error': 'Network error. Please check your connection.'
                }, status=400)
            except stripe.error.StripeError as e:
                return JsonResponse({
                    'success': False,
                    'error': 'Something went wrong. Please try again later.'
                }, status=400)
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': f'Error processing payment: {str(e)}'
                }, status=400)
        else:
            return JsonResponse({
                'success': False,
                'error': 'Invalid form data',
                'errors': form.errors
            }, status=400)
    else:
        form = OrderCreateForm()
    
    return render(request, 'checkout/checkout.html', {
        'cart_items': cart_items,
        'form': form,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'order_id': None
    })

def payment_success(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number)
        
        # Check if the user is authorized to view this order
        if not request.user.is_authenticated or (order.user and order.user != request.user):
            return HttpResponse(status=404)
        
        # If the order already has a stripe_id, verify the payment
        if order.stripe_id:
            # Retrieve the PaymentIntent to confirm the payment status
            intent = stripe.PaymentIntent.retrieve(order.stripe_id)
            
            if intent.status == 'succeeded':
                order.paid = True
                order.save()
                
                # Create a Payment record
                Payment.objects.create(
                    order=order,
                    payment_id=intent.id,
                    payment_method=intent.payment_method_types[0] if intent.payment_method_types else 'card',
                    amount_paid=order.get_total_cost(),
                    status='completed'
                )
        else:
            # If no stripe_id, mark as paid anyway (for testing purposes)
            order.paid = True
            order.save()
            
            # Create a Payment record
            Payment.objects.create(
                order=order,
                payment_id='test_payment_id',
                payment_method='card',
                amount_paid=order.get_total_cost(),
                status='completed'
            )
        
        # Clear the cart
        try:
            cart = Cart.objects.get(cart_id=request.session.session_key)
            cart_items = CartItem.objects.filter(cart=cart)
            cart_items.delete()
            cart.delete()
        except Cart.DoesNotExist:
            pass
        
        # Send confirmation email
        subject = f'Order Confirmation - #{order.order_number}'
        html_message = render_to_string('checkout/email/order_confirmation.html', {
            'order': order,
            'site': get_current_site(request)
        })
        plain_message = strip_tags(html_message)
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [order.email],
            html_message=html_message
        )
        
        messages.success(request, f'Payment successful! Your order number is #{order.order_number}.')
        
        # Redirect to order history
        return redirect('profiles:order_history', order_number=order.order_number)
        
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('checkout:checkout')
    except stripe.error.StripeError as e:
        messages.error(request, f'Error verifying payment: {str(e)}')
        return redirect('checkout:checkout')
    except Exception as e:
        messages.error(request, f'An unexpected error occurred: {str(e)}')
        return redirect('checkout:checkout')

def payment_cancel(request):
    messages.info(request, 'Payment was cancelled. You can try again if you wish.')
    return redirect('cart:view_cart')

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        order_id = session['metadata']['order_id']
        try:
            order = Order.objects.get(id=order_id)
            order.paid = True
            order.stripe_id = session['payment_intent']
            order.save()
            
            # Update payment record
            payment = Payment.objects.get(order=order)
            payment.status = 'completed'
            payment.save()
            
        except Order.DoesNotExist:
            return HttpResponse(status=404)

    return HttpResponse(status=200) 