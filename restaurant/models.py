from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon = models.CharField(
        max_length=50, 
        blank=True, 
        help_text="Bootstrap icon class name, e.g., 'bi-cup-hot', 'bi-egg-fried'"
    )
    order_index = models.PositiveIntegerField(default=0, help_text="Used for ordering categories in navigation and menus.")

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['order_index', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    name = models.CharField(max_length=150)
    category = models.ForeignKey(Category, related_name='items', on_delete=models.CASCADE)
    description = models.TextField(blank=True, help_text="Brief description of ingredients or preparation.")
    price = models.DecimalField(max_digits=6, decimal_places=2, help_text="Price in SAR (Saudi Riyal).")
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True)
    is_available = models.BooleanField(default=True, verbose_name="Available")
    is_vegetarian = models.BooleanField(default=False, verbose_name="Vegetarian")
    is_spicy = models.BooleanField(default=False, verbose_name="Spicy")
    order_index = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Menu Item"
        verbose_name_plural = "Menu Items"
        ordering = ['category', 'order_index', 'name']

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class SpecialItem(models.Model):
    CATEGORY_GROUPS = [
        ('Fish Specials', 'Fish Specials'),
        ('Mutton Specials', 'Mutton Specials'),
        ('Beef Specials', 'Beef Specials'),
        ('Chicken Specials', 'Chicken Specials'),
    ]

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, help_text="Price in SAR.")
    image = models.ImageField(upload_to='specials/', blank=True, null=True)
    is_available = models.BooleanField(default=True, verbose_name="Available")
    category_group = models.CharField(max_length=30, choices=CATEGORY_GROUPS)
    order_index = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Today's Special Item"
        verbose_name_plural = "Today's Special Items"
        ordering = ['category_group', 'order_index', 'name']

    def __str__(self):
        return f"{self.name} - {self.category_group}"


class ComboOffer(models.Model):
    title = models.CharField(max_length=150, help_text="e.g. Porotta + Beef Curry + Tea")
    description = models.TextField(help_text="Details about what is included in the offer.")
    original_price = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, help_text="Optional original price in SAR to show savings.")
    special_price = models.DecimalField(max_digits=6, decimal_places=2, help_text="Offer price in SAR.")
    image = models.ImageField(upload_to='combos/', blank=True, null=True)
    is_available = models.BooleanField(default=True, verbose_name="Available")

    class Meta:
        verbose_name = "Combo Offer"
        verbose_name_plural = "Combo Offers"

    def __str__(self):
        return self.title


class GalleryItem(models.Model):
    GALLERY_CATEGORIES = [
        ('Interior', 'Restaurant Interior'),
        ('Food', 'Food Photography'),
        ('Dining', 'Customer Dining Experience'),
        ('Signature', 'Signature Kerala Dishes'),
    ]

    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='gallery/')
    category = models.CharField(max_length=20, choices=GALLERY_CATEGORIES)
    caption = models.CharField(max_length=200, blank=True, help_text="Optional short caption.")

    class Meta:
        verbose_name = "Gallery Item"
        verbose_name_plural = "Gallery Items"

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"


class Review(models.Model):
    customer_name = models.CharField(max_length=100)
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    review_text = models.TextField()
    is_approved = models.BooleanField(default=True, help_text="Approve this review to display it on the website.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Customer Review"
        verbose_name_plural = "Customer Reviews"
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.customer_name} - {self.rating} Stars"


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.name} on {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def __str__(self):
        return f"{self.name} ({self.phone})"


class Order(models.Model):
    DELIVERY_OPTIONS = [
        ('Dine-In', 'Dine-In'),
        ('Takeaway', 'Takeaway'),
        ('Delivery', 'Delivery'),
    ]
    PAYMENT_STATUSES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
    ]
    ORDER_STATUSES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Preparing', 'Preparing'),
        ('Ready', 'Ready'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]
    PAYMENT_METHODS = [
        ('Online', 'Online Payment'),
        ('Cash on Delivery', 'Cash on Delivery'),
        ('Card at Counter', 'Card at Counter'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True, related_name='orders')
    customer_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    delivery_option = models.CharField(max_length=20, choices=DELIVERY_OPTIONS, default='Dine-In')
    address_or_table = models.CharField(
        max_length=255, 
        help_text="Table number for Dine-In, or address for Delivery."
    )
    total_amount = models.DecimalField(max_digits=8, decimal_places=2, help_text="Total in SAR.")
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHODS, default='Cash on Delivery')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUSES, default='Pending')
    status = models.CharField(max_length=30, choices=ORDER_STATUSES, default='Pending')
    notes = models.TextField(blank=True, null=True, help_text="Kitchen notes or customer remarks.")
    
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=200, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name} ({self.status})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    item_name = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def __str__(self):
        return f"{self.quantity}x {self.item_name}"


class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    payment_gateway = models.CharField(max_length=50, default='Moyasar')
    status = models.CharField(max_length=20, default='Paid')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Payment Transaction"
        verbose_name_plural = "Payment Transactions"

    def __str__(self):
        return f"Payment for Order #{self.order.id} - {self.transaction_id} ({self.status})"

