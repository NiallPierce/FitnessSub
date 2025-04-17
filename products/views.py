from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Product, Category, Review
from .forms import ReviewForm
from cart.forms import CartAddProductForm

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
    return render(request, 'products/products.html', context)

def product_detail(request, category_slug, product_slug):
    """Display individual product details with reviews and related products"""
    product = get_object_or_404(
        Product,
        category__slug=category_slug,
        slug=product_slug,
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
            return redirect('login')
            
        review_form = ReviewForm(data=request.POST)
        if review_form.is_valid():
            new_review = review_form.save(commit=False)
            new_review.product = product
            new_review.user = request.user
            new_review.save()
            messages.success(request, 'Your review has been submitted.')
            return redirect('product_detail', category_slug=category_slug, product_slug=product_slug)
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
    return render(request, 'products/product_detail.html', context)

def category_list(request):
    """Display all categories"""
    categories = Category.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'products/category_list.html', context)

def category_detail(request, category_slug):
    """Display products in a specific category"""
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category, is_available=True)
    
    # Pagination
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'products/category_detail.html', context)