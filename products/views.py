# Django imports
from django.shortcuts import (
    render, get_object_or_404, redirect
)
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import (
    Paginator, EmptyPage, PageNotAnInteger
)
from django.conf import settings
from django.urls import reverse
from django.http import JsonResponse

# Standard library imports
from datetime import datetime, timedelta
import re

# Third-party imports
import stripe
from cart.forms import CartAddProductForm

# Local imports
from .models import (
    Product, Category, Review, SubscriptionPlan, UserSubscription
)
from .forms import ReviewForm, ProductForm

stripe.api_key = settings.STRIPE_SECRET_KEY


def clean_search_query(query):
    """Clean the search query by removing special characters
    and extra spaces."""
    cleaned = re.sub(r'[^\w\s]', '', query.lower())
    return re.sub(r'\s+', ' ', cleaned).strip()


def products(request):
    """Display all products with search, filter, and sort functionality."""
    products = Product.objects.filter(is_available=True)
    categories = Category.objects.all()
    search_query = request.GET.get('q', '')

    if search_query:
        cleaned_query = clean_search_query(search_query)
        search_terms = cleaned_query.split()
        search_filter = Q()

        for term in search_terms:
            name_match = Q(name__iregex=r'\b' + term + r'\b')
            desc_match = Q(description__iregex=r'\b' + term + r'\b')
            search_filter &= (
                name_match | desc_match
            )

        products = products.filter(search_filter)

    category = request.GET.get('category', '')
    if category:
        category_obj = get_object_or_404(Category, name=category)
        products = products.filter(category=category_obj)

    rating = request.GET.get('rating', '')
    if rating:
        products = products.filter(rating__gte=float(rating))

    sort = request.GET.get('sort', '')
    sort_options = {
        'price': 'price',
        '-price': '-price',
        'name': 'name',
        '-name': '-name',
    }
    products = products.order_by(sort_options.get(sort, '-created_at'))

    paginator = Paginator(products, 12)
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
        'selected_category': category,
        'sort': sort,
        'is_paginated': paginator.num_pages > 1
    }
    return render(request, 'product/products.html', context)


def product_detail(request, product_id):
    """Display individual product details with reviews and related products."""
    product = get_object_or_404(Product, id=product_id, is_available=True)

    related_products = Product.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(id=product.id)[:4]

    reviews = Review.objects.filter(product=product, active=True)

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

    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'review_form': review_form,
        'cart_product_form': CartAddProductForm(),
    }
    return render(request, 'product/product_detail.html', context)


def category_list(request):
    """Display all categories."""
    categories = Category.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'product/category_list.html', context)


def category_detail(request, category_slug):
    """Display products in a specific category."""
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category)

    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'product/category_detail.html', context)


@login_required
def add_product(request):
    """Add a new product."""
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect('products:products')
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Successfully added product!')
            return redirect('products:product_detail', product_id=product.id)
        messages.error(
            request,
            'Failed to add product. '
            'Please ensure the form is valid.'
        )
    else:
        form = ProductForm()
    template = 'products/add_product.html'
    context = {
        'form': form,
    }
    return render(request, template, context)


@login_required
def edit_product(request, product_id):
    """Edit a product."""
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
        messages.error(
            request,
            'Failed to update product. '
            'Please ensure the form is valid.'
        )
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
    """Delete a product."""
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect('products:products')

    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, 'Product deleted!')
    return redirect('products:products')


def subscription_plans(request):
    """Display all available subscription plans."""
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
    """Display details of a specific subscription plan."""
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
    """Handle subscription creation through Stripe."""
    plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)

    if not plan.stripe_price_id:
        messages.error(
            request,
            "This plan is not properly configured. Please contact support."
        )
        return redirect('products:subscription_plans')

    try:
        success_url = (
            request.build_absolute_uri(
                reverse('products:subscription_success')
            ) + '?session_id={CHECKOUT_SESSION_ID}'
        )

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': plan.stripe_price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=success_url,
            cancel_url=request.build_absolute_uri(
                reverse('products:subscription_plans')
            ),
            customer_email=request.user.email,
            metadata={
                'plan_id': str(plan.id),
                'user_id': str(request.user.id),
            }
        )
        return redirect(checkout_session.url)

    except stripe.error.StripeError as e:
        messages.error(request, f"Payment processing error: {str(e)}")
    except Exception:
        messages.error(request, "An unexpected error occurred.")

    return redirect('products:subscription_plans')


@login_required
def subscription_cancel(request):
    """Handle subscription cancellation."""
    try:
        subscription = UserSubscription.objects.filter(
            user=request.user,
            is_active=True
        ).latest('created_at')

        try:
            stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                cancel_at_period_end=True
            )

            subscription.is_active = False
            subscription.save()

            msg = (
                'Your subscription has been cancelled. '
                'It will remain active until the end of the current '
                'billing period.'
            )
            messages.success(request, msg)
            return redirect('products:subscription_history')

        except stripe.error.StripeError as e:
            messages.error(
                request,
                f'Error cancelling subscription: {str(e)}'
            )
        except Exception as e:
            messages.error(
                request,
                f'An unexpected error occurred: {str(e)}'
            )

    except UserSubscription.DoesNotExist:
        messages.error(request, 'No active subscription found.')
    except Exception as e:
        messages.error(
            request,
            f'An unexpected error occurred: {str(e)}'
        )

    return redirect('products:subscription_plans')


@login_required
def subscription_history(request):
    """Display user's subscription history."""
    subscriptions = UserSubscription.objects.filter(
        user=request.user
    ).order_by('-created_at')

    context = {
        'subscriptions': subscriptions,
    }
    return render(request, 'product/subscription_history.html', context)


def subscription_success(request):
    """Handle successful subscription creation."""
    session_id = request.GET.get('session_id')
    if not session_id:
        messages.error(request, 'Invalid session ID')
        return redirect('products:subscription_plans')

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        plan_id = session.metadata.get('plan_id')
        user_id = session.metadata.get('user_id')

        if not all([plan_id, user_id]):
            messages.error(request, 'Invalid subscription data')
            return redirect('products:subscription_plans')

        defaults = {
            'stripe_subscription_id': session.subscription,
            'stripe_customer_id': session.customer,
            'end_date': datetime.now() + timedelta(days=30),
        }

        subscription, created = UserSubscription.objects.update_or_create(
            user_id=user_id,
            plan_id=plan_id,
            defaults=defaults
        )

        if not created:
            subscription.is_active = True
            subscription.save()

        messages.success(request, 'Subscription activated successfully!')
        return redirect('products:subscription_detail', plan_id=plan_id)

    except stripe.error.StripeError:
        messages.error(request, 'Error verifying payment')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')

    return redirect('products:subscription_plans')


def debug_stripe_config(request):
    """Debug view to check Stripe configuration."""
    config = {
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'stripe_secret_key': (
            settings.STRIPE_SECRET_KEY[:5] + '...'
            if settings.STRIPE_SECRET_KEY else None
        ),
        'stripe_webhook_secret': (
            settings.STRIPE_WEBHOOK_SECRET[:5] + '...'
            if settings.STRIPE_WEBHOOK_SECRET else None
        ),
        'active_plans': list(
            SubscriptionPlan.objects.filter(is_active=True).values(
                'id', 'name', 'stripe_price_id'
            )
        )
    }
    return JsonResponse(config)


@login_required
def subscription_management(request):
    """View for managing subscription details."""
    try:
        subscription = UserSubscription.objects.get(
            user=request.user,
            is_active=True
        )
        stripe_sub = stripe.Subscription.retrieve(
            subscription.stripe_subscription_id
        )
        customer = stripe.Customer.retrieve(
            subscription.stripe_customer_id
        )
        payment_methods = stripe.PaymentMethod.list(
            customer=customer.id,
            type="card"
        )
        invoices = stripe.Invoice.list(
            customer=customer.id,
            limit=5
        )
        context = {
            'subscription': subscription,
            'stripe_subscription': stripe_sub,
            'payment_methods': payment_methods.data,
            'invoices': invoices.data,
        }
        return render(request, 'product/subscription_management.html', context)
    except UserSubscription.DoesNotExist:
        messages.info(request, "No active subscription found.")
    except stripe.error.StripeError as e:
        messages.error(
            request,
            f"Error retrieving details: {str(e)}"
        )
    return redirect('products:subscription_plans')


@login_required
def update_payment_method(request):
    """View for updating payment method."""
    if request.method == 'POST':
        try:
            subscription = UserSubscription.objects.get(
                user=request.user,
                is_active=True
            )
            payment_method_id = request.POST.get('payment_method_id')

            if not payment_method_id:
                messages.error(request, "No payment method provided.")
                return redirect('products:update_payment_method')

            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=subscription.stripe_customer_id,
            )

            stripe.Customer.modify(
                subscription.stripe_customer_id,
                invoice_settings={
                    'default_payment_method': payment_method_id
                }
            )

            stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                default_payment_method=payment_method_id
            )

            messages.success(request, "Payment method updated successfully!")
            return redirect('products:subscription_management')

        except stripe.error.StripeError as e:
            messages.error(request, f"Error updating payment method: {str(e)}")
        except UserSubscription.DoesNotExist:
            messages.error(request, "No active subscription found.")
        except Exception:
            messages.error(request, "An unexpected error occurred.")

        return redirect('products:update_payment_method')

    try:
        subscription = UserSubscription.objects.get(
            user=request.user,
            is_active=True
        )
        context = {
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'subscription': subscription
        }
        return render(request, 'product/update_payment_method.html', context)

    except UserSubscription.DoesNotExist:
        messages.error(request, "No active subscription found.")
    except Exception:
        messages.error(request, "An unexpected error occurred.")

    return redirect('products:subscription_plans')


@login_required
def cancel_subscription(request):
    """View for canceling subscription."""
    if request.method == 'POST':
        try:
            subscription = UserSubscription.objects.get(
                user=request.user,
                is_active=True
            )

            stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                cancel_at_period_end=True
            )

            subscription.is_active = False
            subscription.save()

            msg = (
                'Your subscription has been cancelled. '
                'It will remain active until the end of the current '
                'billing period.'
            )
            messages.success(request, msg)
            return redirect('products:subscription_management')

        except stripe.error.StripeError as e:
            messages.error(request, f"Error cancelling subscription: {str(e)}")
        except UserSubscription.DoesNotExist:
            messages.error(request, "No active subscription found.")

    return render(request, 'product/cancel_subscription.html')
