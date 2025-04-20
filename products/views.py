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

stripe.api_key = settings.STRIPE_SECRET_KEY

def products(request):
    """Display all products with search, filter, and sort functionality"""
    products = Product.objects.filter(is_available=True)
    categories = Category.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
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
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_slug,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
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
    """Handle subscription creation"""
    plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
    
    # Check if user already has an active subscription
    existing_subscription = UserSubscription.objects.filter(
        user=request.user,
        is_active=True
    ).first()
    
    if existing_subscription:
        messages.warning(request, 'You already have an active subscription.')
        return redirect('products:subscription_detail', plan_id=plan.id)
    
    try:
        # Create Stripe customer if not exists
        if not request.user.userprofile.stripe_customer_id:
            customer = stripe.Customer.create(
                email=request.user.email,
                name=f"{request.user.first_name} {request.user.last_name}"
            )
            request.user.userprofile.stripe_customer_id = customer.id
            request.user.userprofile.save()
        
        # Create Stripe subscription
        subscription = stripe.Subscription.create(
            customer=request.user.userprofile.stripe_customer_id,
            items=[{'price': plan.stripe_price_id}],
            payment_behavior='default_incomplete',
            expand=['latest_invoice.payment_intent'],
        )
        
        # Create UserSubscription record
        end_date = datetime.now() + timedelta(days=30)  # Default to 30 days
        if plan.plan_type == 'quarterly':
            end_date = datetime.now() + timedelta(days=90)
        elif plan.plan_type == 'annual':
            end_date = datetime.now() + timedelta(days=365)
        
        user_subscription = UserSubscription.objects.create(
            user=request.user,
            plan=plan,
            end_date=end_date,
            stripe_subscription_id=subscription.id,
            stripe_customer_id=request.user.userprofile.stripe_customer_id
        )
        
        messages.success(request, 'Subscription created successfully!')
        return redirect('products:subscription_success')
        
    except stripe.error.StripeError as e:
        messages.error(request, f'Error creating subscription: {str(e)}')
        return redirect('products:subscription_detail', plan_id=plan.id)
    except Exception as e:
        messages.error(request, f'An unexpected error occurred: {str(e)}')
        return redirect('products:subscription_detail', plan_id=plan.id)

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
    """Display subscription success page"""
    return render(request, 'product/subscription_success.html')