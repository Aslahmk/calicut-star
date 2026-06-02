from .cart import Cart

def cart(request):
    try:
        return {'cart': Cart(request)}
    except AttributeError:
        return {'cart': None}