from django.shortcuts import render
from products.models import Product

# Create your views here.

def index(request):
    """ A view to return the index page """
    featured_products = Product.objects.filter(is_featured=True, is_available=True, image__isnull=False)[:6]
    # Debug info
    for product in featured_products:
        print(f"Product: {product.name}, Image: {product.image}")
    context = {
        'featured_products': featured_products,
    }
    return render(request, 'home/index.html', context)

def custom_404(request, exception):
    return render(request, '404.html', status=404)