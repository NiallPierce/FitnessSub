from .models import Cart, CartItem


def _cart_id(request):
    """ Helper function to get or create cart_id """
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def cart_contents(request):
    """
    Context processor to make cart contents available
    across all templates
    """
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        total = 0
        quantity = 0
        for cart_item in cart_items:
            total += (
                cart_item.product.price * cart_item.quantity
            )
            quantity += cart_item.quantity
    except Cart.DoesNotExist:
        cart_items = []
        total = 0
        quantity = 0

    context = {
        'cart_items': cart_items,
        'total': total,
        'quantity': quantity,
    }

    return context
