from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Product, Category, Review, SubscriptionPlan, UserSubscription
from .forms import ReviewForm, ProductForm
from cart.forms import CartAddProductForm
from django.conf import settings
import stripe
from datetime import datetime, timedelta
from django.urls import reverse
from django.http import JsonResponse
import re

stripe.api_key = settings.STRIPE_SECRET_KEY

def clean_search_query(query):
    """Clean the search query by removing special characters and extra spaces"""
    # Remove special characters and convert to lowercase
    cleaned = re.sub(r'[^\w\s]', '', query.lower())
    # Replace multiple spaces with single space
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()

def products(request):
    """Display all products with search, filter, and sort functionality"""
    products = Product.objects.filter(is_available=True)
    categories = Category.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        cleaned_query = clean_search_query(search_query)
        # Create a list of search terms
        search_terms = cleaned_query.split()
        # Build a complex Q object for flexible searching
        search_filter = Q()
        for term in search_terms:
            search_filter |= Q(name__icontains=term) | Q(description__icontains=term)
        products = products.filter(search_filter)
    
    # Category filter
    category_slug = request.GET.get('category', '')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    # Price range filter
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    if min_price:
        products = products.filter(price__gte=float(min_price))
    if max_price:
        products = products.filter(price__lte=float(max_price))
    
    # Sorting
    sort_by = request.GET.get('sort_by', 'newest')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'name_asc':
        products = products.order_by('name')
    elif sort_by == 'name_desc':
        products = products.order_by('-name')
    else:  # newest
        products = products.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_slug,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
        'is_paginated': paginator.num_pages > 1
    }
    return render(request, 'product/products.html', context)

def product_detail(request, product_id):
    """Display individual product details with reviews and related products"""
    product = get_object_or_404(
        Product,
        id=product_id,
        is_available=True
    )
    
    # Get related products (same category)
    related_products = Product.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(id=product.id)[:4]
    
    # Get product reviews
    reviews = Review.objects.filter(product=product, active=True)
    
    # Handle review submission
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to leave a review.')
            return redirect('account_login')
            
        review_form = ReviewForm(data=request.POST)
        if review_form.is_valid():
            new_review = review_form.save(commit=False)
            new_review.product = product
            new_review.user = request.user
            new_review.save()
            messages.success(request, 'Your review has been submitted.')
            return redirect('products:product_detail', product_id=product.id)
    else:
        review_form = ReviewForm()
    
    # Cart form
    cart_product_form = CartAddProductForm()
    
    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'review_form': review_form,
        'cart_product_form': cart_product_form,
    }
    return render(request, 'product/product_detail.html', context)

def category_list(request):
    """Display all categories"""
    categories = Category.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'product/category_list.html', context)

def category_detail(request, category_slug):
    """Display products in a specific category"""
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category)
    
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'product/category_detail.html', context)

@login_required
def add_product(request):
    """Add a new product"""
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect('products:products')
        
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Successfully added product!')
            return redirect('products:product_detail', product_id=product.id)
        else:
            messages.error(request, 'Failed to add product. Please ensure the form is valid.')
    else:
        form = ProductForm()
        
    template = 'products/add_product.html'
    context = {
        'form': form,
    }
    return render(request, template, context)

@login_required
def edit_product(request, product_id):
    """Edit a product"""
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect('products:products')
        
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated product!')
            return redirect('products:product_detail', product_id=product.id)
        else:
            messages.error(request, 'Failed to update product. Please ensure the form is valid.')
    else:
        form = ProductForm(instance=product)
        messages.info(request, f'You are editing {product.name}')
        
    template = 'products/edit_product.html'
    context = {
        'form': form,
        'product': product,
    }
    return render(request, template, context)

@login_required
def delete_product(request, product_id):
    """Delete a product"""
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect('products:products')
        
    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, 'Product deleted!')
    return redirect('products:products')

def subscription_plans(request):
    """Display all available subscription plans"""
    plans = SubscriptionPlan.objects.filter(is_active=True)
    user_subscription = None
    if request.user.is_authenticated:
        user_subscription = UserSubscription.objects.filter(
            user=request.user,
            is_active=True
        ).first()
    
    context = {
        'plans': plans,
        'user_subscription': user_subscription,
    }
    return render(request, 'product/subscription_plans.html', context)

def subscription_detail(request, plan_id):
    """Display details of a specific subscription plan"""
    plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
    user_subscription = None
    if request.user.is_authenticated:
        user_subscription = UserSubscription.objects.filter(
            user=request.user,
            is_active=True
        ).first()
    
    context = {
        'plan': plan,
        'user_subscription': user_subscription,
    }
    return render(request, 'product/subscription_detail.html', context)

@login_required
def subscribe(request, plan_id):
    try:
        plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
        
        if not plan.stripe_price_id:
            messages.error(request, "This plan is not properly configured. Please contact support.")
            return redirect('products:subscription_plans')
        
        # Create Stripe checkout session
        try:
            print(f"Creating checkout session for plan: {plan.name} with price_id: {plan.stripe_price_id}")
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': plan.stripe_price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=request.build_absolute_uri(
                    reverse('products:subscription_success')
                ) + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.build_absolute_uri(reverse('products:subscription_plans')),
                customer_email=request.user.email if request.user.is_authenticated else None,
                metadata={
                    'plan_id': str(plan.id),
                    'user_id': str(request.user.id) if request.user.is_authenticated else None,
                }
            )
            print(f"Checkout session created successfully: {checkout_session.id}")
            return redirect(checkout_session.url)
        except stripe.error.StripeError as e:
            print(f"Stripe error: {str(e)}")
            print(f"Error type: {type(e)}")
            print(f"Error code: {getattr(e, 'code', 'No code')}")
            print(f"Error param: {getattr(e, 'param', 'No param')}")
            messages.error(request, f"Payment processing error: {str(e)}")
            return redirect('products:subscription_plans')
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(traceback.format_exc())
            messages.error(request, "An unexpected error occurred. Please try again.")
            return redirect('products:subscription_plans')
    except Exception as e:
        print(f"General error: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(traceback.format_exc())
        messages.error(request, "An unexpected error occurred. Please try again.")
        return redirect('products:subscription_plans')

@login_required
def subscription_cancel(request):
    """Handle subscription cancellation"""
    subscription = get_object_or_404(
        UserSubscription,
        user=request.user,
        is_active=True
    )
    
    try:
        # Cancel Stripe subscription
        stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=True
        )
        
        # Update local subscription record
        subscription.is_active = False
        subscription.save()
        
        messages.success(request, 'Your subscription has been cancelled. It will remain active until the end of the current billing period.')
        return redirect('products:subscription_history')
        
    except stripe.error.StripeError as e:
        messages.error(request, f'Error cancelling subscription: {str(e)}')
        return redirect('products:subscription_history')
    except Exception as e:
        messages.error(request, f'An unexpected error occurred: {str(e)}')
        return redirect('products:subscription_history')

@login_required
def subscription_history(request):
    """Display user's subscription history"""
    subscriptions = UserSubscription.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    context = {
        'subscriptions': subscriptions,
    }
    return render(request, 'product/subscription_history.html', context)

def subscription_success(request):
    """Handle successful subscription creation"""
    session_id = request.GET.get('session_id')
    if not session_id:
        messages.error(request, 'Invalid session ID')
        return redirect('products:subscription_plans')
    
    try:
        # Retrieve the checkout session
        session = stripe.checkout.Session.retrieve(session_id)
        
        # Get the plan_id from the session metadata
        plan_id = session.metadata.get('plan_id')
        if not plan_id:
            messages.error(request, 'Invalid plan ID')
            return redirect('products:subscription_plans')
        
        # Get the user_id from the session metadata
        user_id = session.metadata.get('user_id')
        if not user_id:
            messages.error(request, 'Invalid user ID')
            return redirect('products:subscription_plans')
        
        # Create or update the subscription
        subscription, created = UserSubscription.objects.get_or_create(
            user_id=user_id,
            plan_id=plan_id,
            defaults={
                'stripe_subscription_id': session.subscription,
                'stripe_customer_id': session.customer,
                'end_date': datetime.now() + timedelta(days=30),  # Default 30-day period
            }
        )
        
        if not created:
            subscription.stripe_subscription_id = session.subscription
            subscription.stripe_customer_id = session.customer
            subscription.is_active = True
            subscription.save()
        
        messages.success(request, 'Your subscription has been activated successfully!')
        return redirect('products:subscription_detail', plan_id=plan_id)
        
    except stripe.error.StripeError as e:
        messages.error(request, f'Error verifying payment: {str(e)}')
        return redirect('products:subscription_plans')
    except Exception as e:
        messages.error(request, f'An unexpected error occurred: {str(e)}')
        return redirect('products:subscription_plans')

def debug_stripe_config(request):
    """Debug view to check Stripe configuration"""
    config = {
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'stripe_secret_key': settings.STRIPE_SECRET_KEY[:5] + '...' if settings.STRIPE_SECRET_KEY else None,
        'stripe_webhook_secret': settings.STRIPE_WEBHOOK_SECRET[:5] + '...' if settings.STRIPE_WEBHOOK_SECRET else None,
        'active_plans': list(SubscriptionPlan.objects.filter(is_active=True).values('id', 'name', 'stripe_price_id'))
    }
    return JsonResponse(config)

@login_required
def subscription_management(request):
    """View for managing subscription details"""
    try:
        subscription = UserSubscription.objects.get(user=request.user, is_active=True)
        try:
            # Get Stripe subscription details
            stripe_subscription = stripe.Subscription.retrieve(subscription.stripe_subscription_id)
            stripe_customer = stripe.Customer.retrieve(subscription.stripe_customer_id)
            
            # Get payment method details
            payment_methods = stripe.PaymentMethod.list(
                customer=stripe_customer.id,
                type="card"
            )
            
            # Get billing history
            invoices = stripe.Invoice.list(
                customer=stripe_customer.id,
                limit=5
            )
            
            context = {
                'subscription': subscription,
                'stripe_subscription': stripe_subscription,
                'payment_methods': payment_methods.data,
                'invoices': invoices.data,
            }
            return render(request, 'product/subscription_management.html', context)
            
        except stripe.error.StripeError as e:
            messages.error(request, f"Error retrieving subscription details: {str(e)}")
            return redirect('products:subscription_plans')
            
    except UserSubscription.DoesNotExist:
        messages.info(request, "You don't have an active subscription.")
        return redirect('products:subscription_plans')

@login_required
def update_payment_method(request):
    """View for updating payment method"""
    if request.method == 'POST':
        try:
            # Get the active subscription for the user
            subscription = UserSubscription.objects.get(user=request.user, is_active=True)
            payment_method_id = request.POST.get('payment_method_id')
            
            if not payment_method_id:
                messages.error(request, "No payment method provided.")
                return redirect('products:update_payment_method')
            
            # Attach the payment method to the customer
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=subscription.stripe_customer_id,
            )
            
            # Set it as the default payment method
            stripe.Customer.modify(
                subscription.stripe_customer_id,
                invoice_settings={
                    'default_payment_method': payment_method_id
                }
            )
            
            # Update the subscription to use the new payment method
            stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                default_payment_method=payment_method_id
            )
            
            messages.success(request, "Payment method updated successfully!")
            return redirect('products:subscription_management')
            
        except stripe.error.StripeError as e:
            print(f"Stripe error: {str(e)}")
            messages.error(request, f"Error updating payment method: {str(e)}")
            return redirect('products:update_payment_method')
        except UserSubscription.DoesNotExist:
            messages.error(request, "No active subscription found.")
            return redirect('products:subscription_plans')
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            messages.error(request, "An unexpected error occurred. Please try again.")
            return redirect('products:update_payment_method')
    
    # For GET requests, render the update payment method form
    try:
        subscription = UserSubscription.objects.get(user=request.user, is_active=True)
        context = {
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'subscription': subscription
        }
        return render(request, 'product/update_payment_method.html', context)
    except UserSubscription.DoesNotExist:
        messages.error(request, "No active subscription found.")
        return redirect('products:subscription_plans')
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        messages.error(request, "An unexpected error occurred. Please try again.")
        return redirect('products:subscription_plans')

@login_required
def cancel_subscription(request):
    """View for canceling subscription"""
    if request.method == 'POST':
        try:
            subscription = UserSubscription.objects.get(user=request.user, is_active=True)
            
            # Cancel the subscription at the end of the billing period
            stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                cancel_at_period_end=True
            )
            
            subscription.is_active = False
            subscription.save()
            
            messages.success(request, "Your subscription has been cancelled. It will remain active until the end of the current billing period.")
            return redirect('products:subscription_management')
            
        except stripe.error.StripeError as e:
            messages.error(request, f"Error cancelling subscription: {str(e)}")
            return redirect('products:subscription_management')
        except UserSubscription.DoesNotExist:
            messages.error(request, "No active subscription found.")
            return redirect('products:subscription_plans')
    
    return render(request, 'product/cancel_subscription.html')