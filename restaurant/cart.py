from decimal import Decimal
from django.conf import settings
from .models import MenuItem, SpecialItem, ComboOffer

class Cart:
    def __init__(self, request):
        """Initialize the cart using Django sessions."""
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            # Save an empty cart in the session
            cart = self.session['cart'] = {}
        self.cart = cart

    def save(self):
        """Mark the session as modified to ensure it gets saved."""
        self.session.modified = True

    def add(self, item_id, item_type, quantity=1, override_quantity=False):
        """Add an item to the cart or update its quantity."""
        key = f"{item_type}_{item_id}"
        
        if key not in self.cart:
            self.cart[key] = {
                'item_id': str(item_id),
                'item_type': item_type,
                'quantity': 0
            }
            
        if override_quantity:
            self.cart[key]['quantity'] = quantity
        else:
            self.cart[key]['quantity'] += quantity
            
        self.save()

    def remove(self, item_id, item_type):
        """Remove an item from the cart."""
        key = f"{item_type}_{item_id}"
        if key in self.cart:
            del self.cart[key]
            self.save()

    def update(self, item_id, item_type, quantity):
        """Update the quantity of a specific item."""
        key = f"{item_type}_{item_id}"
        if key in self.cart:
            if quantity <= 0:
                self.remove(item_id, item_type)
            else:
                self.cart[key]['quantity'] = int(quantity)
                self.save()

    def __iter__(self):
        """Iterate over the items in the cart and query database models."""
        cart_data = self.cart.copy()
        
        for key, value in cart_data.items():
            item_id = value['item_id']
            item_type = value['item_type']
            quantity = value['quantity']
            
            item_obj = None
            price = Decimal('0.00')
            name = ""
            
            try:
                if item_type == 'menu':
                    item_obj = MenuItem.objects.get(id=item_id)
                    price = item_obj.price
                    name = item_obj.name
                elif item_type == 'special':
                    item_obj = SpecialItem.objects.get(id=item_id)
                    price = item_obj.price
                    name = item_obj.name
                elif item_type == 'combo':
                    item_obj = ComboOffer.objects.get(id=item_id)
                    price = item_obj.special_price
                    name = item_obj.title
            except (MenuItem.DoesNotExist, SpecialItem.DoesNotExist, ComboOffer.DoesNotExist):
                # Clean up deleted items from cart
                self.remove(item_id, item_type)
                continue
                
            total_price = price * quantity
            
            yield {
                'key': key,
                'item_id': item_id,
                'item_type': item_type,
                'quantity': quantity,
                'price': price,
                'total_price': total_price,
                'name': name,
                'item': item_obj
            }

    def __len__(self):
        """Count all items in the cart."""
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """Calculate the total price of all items in the cart."""
        total = Decimal('0.00')
        for item in self:
            total += item['total_price']
        return total

    def clear(self):
        """Remove the cart from session."""
        del self.session['cart']
        self.save()
