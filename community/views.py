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

from .forms import OrderForm
from .models import Order, OrderItem, Payment
from cart.models import Cart, CartItem
from cart.contexts import cart_contents
from .forms import OrderCreateForm
from products.models import Product
from profiles.models import UserSubscription

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def checkout(request):
    try:
        cart = Cart.objects.get(cart_id=request.session.session_key)
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        if not cart_items:
            messages.warning(request, 'Your cart is empty')
            return redirect('cart:view_cart')
    except Cart.DoesNotExist:
        messages.warning(request, 'Your cart is empty')
        return redirect('cart:view_cart')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.save()
            
            for cart_item in cart_items:
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
                
                return render(request, 'checkout/checkout.html', {
                    'client_secret': intent.client_secret,
                    'order': order,
                    'cart_items': cart_items,
                    'form': form,
                    'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
                    'order_id': order.id
                })
                
            except stripe.error.CardError as e:
                messages.error(request, f'Card error: {str(e)}')
                return redirect('checkout:checkout')
            except stripe.error.RateLimitError as e:
                messages.error(request, 'Rate limit error. Please try again later.')
                return redirect('checkout:checkout')
            except stripe.error.InvalidRequestError as e:
                messages.error(request, f'Invalid request: {str(e)}')
                return redirect('checkout:checkout')
            except stripe.error.AuthenticationError as e:
                messages.error(request, 'Authentication error. Please contact support.')
                return redirect('checkout:checkout')
            except stripe.error.APIConnectionError as e:
                messages.error(request, 'Network error. Please check your connection.')
                return redirect('checkout:checkout')
            except stripe.error.StripeError as e:
                messages.error(request, 'Something went wrong. Please try again later.')
                return redirect('checkout:checkout')
            except Exception as e:
                messages.error(request, f'Error processing payment: {str(e)}')
                return redirect('checkout:checkout')
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
        print(f"Error parsing webhook payload: {str(e)}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        print(f"Invalid signature: {str(e)}")
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        order_id = session['metadata'].get('order_id')
        plan_id = session['metadata'].get('plan_id')
        user_id = session['metadata'].get('user_id')

        if order_id:
            # Handle product order
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
                print(f"Order not found: {order_id}")
                return HttpResponse(status=404)
        elif plan_id and user_id:
            # Handle subscription
            try:
                subscription = UserSubscription.objects.get(
                    user_id=user_id,
                    plan_id=plan_id
                )
                subscription.stripe_subscription_id = session['subscription']
                subscription.stripe_customer_id = session['customer']
                subscription.is_active = True
                subscription.save()

                # Send subscription confirmation email
                subject = 'Subscription Confirmation'
                html_message = render_to_string('products/email/subscription_confirmation.html', {
                    'subscription': subscription,
                    'site': get_current_site(request)
                })
                plain_message = strip_tags(html_message)
                send_mail(
                    subject,
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [subscription.user.email],
                    html_message=html_message
                )
            except UserSubscription.DoesNotExist:
                print(f"Subscription not found for user {user_id} and plan {plan_id}")
                return HttpResponse(status=404)

    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        try:
            user_subscription = UserSubscription.objects.get(
                stripe_subscription_id=subscription['id']
            )
            user_subscription.is_active = subscription['status'] == 'active'
            user_subscription.save()

            if subscription['status'] == 'canceled':
                # Send subscription cancellation email
                subject = 'Subscription Cancelled'
                html_message = render_to_string('products/email/subscription_cancelled.html', {
                    'subscription': user_subscription,
                    'site': get_current_site(request)
                })
                plain_message = strip_tags(html_message)
                send_mail(
                    subject,
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user_subscription.user.email],
                    html_message=html_message
                )

        except UserSubscription.DoesNotExist:
            print(f"Subscription not found: {subscription['id']}")
            return HttpResponse(status=404)

    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        try:
            user_subscription = UserSubscription.objects.get(
                stripe_subscription_id=subscription['id']
            )
            user_subscription.is_active = False
            user_subscription.save()

            # Send subscription ended email
            subject = 'Subscription Ended'
            html_message = render_to_string('products/email/subscription_ended.html', {
                'subscription': user_subscription,
                'site': get_current_site(request)
            })
            plain_message = strip_tags(html_message)
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [user_subscription.user.email],
                html_message=html_message
            )

        except UserSubscription.DoesNotExist:
            print(f"Subscription not found: {subscription['id']}")
            return HttpResponse(status=404)

    elif event['type'] == 'invoice.payment_succeeded':
        invoice = event['data']['object']
        if invoice['billing_reason'] == 'subscription_create':
            # This is handled by checkout.session.completed
            return HttpResponse(status=200)
        
        try:
            subscription = UserSubscription.objects.get(
                stripe_subscription_id=invoice['subscription']
            )
            # Send payment confirmation email
            subject = 'Payment Confirmation'
            html_message = render_to_string('products/email/payment_confirmation.html', {
                'subscription': subscription,
                'invoice': invoice,
                'site': get_current_site(request)
            })
            plain_message = strip_tags(html_message)
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [subscription.user.email],
                html_message=html_message
            )
        except UserSubscription.DoesNotExist:
            print(f"Subscription not found for invoice: {invoice['subscription']}")
            return HttpResponse(status=404)

    elif event['type'] == 'invoice.payment_failed':
        invoice = event['data']['object']
        try:
            subscription = UserSubscription.objects.get(
                stripe_subscription_id=invoice['subscription']
            )
            # Send payment failure email
            subject = 'Payment Failed'
            html_message = render_to_string('products/email/payment_failed.html', {
                'subscription': subscription,
                'invoice': invoice,
                'site': get_current_site(request)
            })
            plain_message = strip_tags(html_message)
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [subscription.user.email],
                html_message=html_message
            )
        except UserSubscription.DoesNotExist:
            print(f"Subscription not found for invoice: {invoice['subscription']}")
            return HttpResponse(status=404)

    return HttpResponse(status=200) 