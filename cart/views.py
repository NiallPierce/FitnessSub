from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from products.models import Product
from .models import Cart, CartItem
from .forms import CartAddProductForm
from django.contrib import messages


def _cart_id(request):
    """Helper function to get or create cart_id."""
    if not request.session.exists(request.session.session_key):
        request.session.create()
    return request.session.session_key


@require_POST
def add_cart(request, product_id):
    """Add a product to the cart or update its quantity."""
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)

    if form.is_valid():
        cd = form.cleaned_data
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cart_id(request))
            cart.save()

        try:
            cart_item = CartItem.objects.get(product=product, cart=cart)
            if cd['override']:
                cart_item.quantity = cd['quantity']
            else:
                cart_item.quantity += cd['quantity']
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=cd['quantity'],
                cart=cart
            )
            cart_item.save()

        messages.success(
            request,
            f'{product.name} added to your cart!'
        )
    return redirect('cart:view_cart')


def remove_cart(request, product_id):
    """Decrease the quantity of a product in the cart."""
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    messages.success(
        request,
        f'{product.name} quantity updated!'
    )
    return redirect('cart:view_cart')


def remove_cart_item(request, product_id):
    """Remove a product completely from the cart."""
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    messages.success(
        request,
        f'{product.name} removed from your cart!'
    )
    return redirect('cart:view_cart')


def view_cart(request):
    """Display the contents of the cart."""
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        total = 0
        quantity = 0

        for cart_item in cart_items:
            total += (
                cart_item.product.price *
                cart_item.quantity
            )
            quantity += cart_item.quantity

        context = {
            'total': total,
            'quantity': quantity,
            'cart_items': cart_items,
        }
    except Cart.DoesNotExist:
        context = {
            'total': 0,
            'quantity': 0,
            'cart_items': None,
        }

    return render(request, 'cart/cart.html', context)
