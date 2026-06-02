from .cart import Cart

def cart(request):
    """Context processor to make the Cart instance globally available in templates."""
    return {'cart': Cart(request)}
