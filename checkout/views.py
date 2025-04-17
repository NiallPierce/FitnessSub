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
from cart.contexts import cart_contents
from .forms import OrderForm
from .models import Order, OrderItem, Payment
from cart.cart import Cart
from .forms import OrderCreateForm
from products.models import Product

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def checkout(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.save()
            
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            
            try:
                checkout_session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': f'Order #{order.id}',
                            },
                            'unit_amount': int(order.get_total_cost() * 100),
                        },
                        'quantity': 1,
                    }],
                    mode='payment',
                    success_url=request.build_absolute_uri(f'/checkout/success/{order.id}/'),
                    cancel_url=request.build_absolute_uri('/checkout/cancel/'),
                    metadata={
                        'order_id': order.id
                    }
                )
                return redirect(checkout_session.url, code=303)
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
        'cart': cart,
        'form': form,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    })

def payment_success(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        order.paid = True
        order.save()
        
        # Create payment record
        payment = Payment.objects.create(
            order=order,
            payment_id=f"stripe_{order_id}",
            payment_method='stripe',
            amount_paid=order.get_total_cost(),
            status='completed'
        )
        
        # Send confirmation email
        subject = f'Order Confirmation - #{order.id}'
        html_message = render_to_string('checkout/email/order_confirmation.html', {
            'order': order,
            'payment': payment
        })
        plain_message = strip_tags(html_message)
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [order.email],
            html_message=html_message
        )
        
        # Clear the cart
        cart = Cart(request)
        cart.clear()
        
        messages.success(request, 'Payment successful! A confirmation email has been sent.')
        return render(request, 'checkout/success.html', {'order': order})
    except Order.DoesNotExist:
        messages.error(request, 'Order not found')
        return redirect('home')
    except Exception as e:
        messages.error(request, f'Error processing order: {str(e)}')
        return redirect('home')

def payment_cancel(request):
    messages.info(request, 'Payment was cancelled. You can try again if you wish.')
    return render(request, 'checkout/cancel.html')

def order_complete(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number)
        order_items = OrderItem.objects.filter(order=order)
        payment = Payment.objects.get(order=order)
        context = {
            'order': order,
            'order_items': order_items,
            'payment': payment,
        }
        return render(request, 'checkout/order_complete.html', context)
    except Order.DoesNotExist:
        messages.error(request, 'Order not found')
        return redirect('home')

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