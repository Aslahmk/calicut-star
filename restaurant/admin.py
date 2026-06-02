from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Category, MenuItem, SpecialItem, ComboOffer, GalleryItem, Review, ContactMessage, Order, OrderItem, Customer, Payment

# Admin customization titles
admin.site.site_header = "Calicut Star Administration"
admin.site.site_title = "Calicut Star Admin Portal"
admin.site.index_title = "Welcome to Calicut Star Management Console"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon', 'order_index')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    ordering = ('order_index', 'name')


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available', 'is_vegetarian', 'is_spicy', 'image_preview', 'order_index')
    list_filter = ('category', 'is_available', 'is_vegetarian', 'is_spicy')
    search_fields = ('name', 'description')
    ordering = ('category', 'order_index', 'name')
    list_editable = ('price', 'is_available', 'order_index')

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />')
        return "No Image"
    image_preview.short_description = "Preview"


@admin.register(SpecialItem)
class SpecialItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_group', 'price', 'is_available', 'image_preview', 'order_index')
    list_filter = ('category_group', 'is_available')
    search_fields = ('name', 'description')
    ordering = ('category_group', 'order_index', 'name')
    list_editable = ('price', 'is_available', 'order_index')

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />')
        return "No Image"
    image_preview.short_description = "Preview"


@admin.register(ComboOffer)
class ComboOfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'original_price', 'special_price', 'is_available', 'image_preview')
    list_filter = ('is_available',)
    search_fields = ('title', 'description')
    list_editable = ('special_price', 'is_available')

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />')
        return "No Image"
    image_preview.short_description = "Preview"


@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'caption', 'image_preview')
    list_filter = ('category',)
    search_fields = ('title', 'caption')

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="80" style="border-radius: 4px;" />')
        return "No Image"
    image_preview.short_description = "Preview"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'rating', 'review_text_short', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved', 'created_at')
    search_fields = ('customer_name', 'review_text')
    list_editable = ('is_approved',)
    readonly_fields = ('created_at',)

    def review_text_short(self, obj):
        return obj.review_text[:60] + "..." if len(obj.review_text) > 60 else obj.review_text
    review_text_short.short_description = "Review Text"


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'phone', 'email', 'message')
    readonly_fields = ('name', 'phone', 'email', 'message', 'created_at')
    list_editable = ('is_read',)
    ordering = ('-created_at',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('item_name', 'price', 'quantity')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'phone', 'delivery_option', 'address_or_table', 'total_amount', 'status', 'payment_method', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_method', 'payment_status', 'delivery_option', 'created_at')
    search_fields = ('customer_name', 'phone', 'address_or_table', 'razorpay_order_id')
    readonly_fields = ('customer_name', 'phone', 'delivery_option', 'address_or_table', 'total_amount', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature', 'created_at')
    list_editable = ('status', 'payment_status')
    inlines = [OrderItemInline]
    ordering = ('-created_at',)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'created_at')
    search_fields = ('name', 'phone', 'email')
    readonly_fields = ('created_at',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'order', 'amount', 'payment_gateway', 'status', 'created_at')
    list_filter = ('payment_gateway', 'status', 'created_at')
    search_fields = ('transaction_id', 'order__id', 'order__customer_name')
    readonly_fields = ('transaction_id', 'order', 'amount', 'payment_gateway', 'status', 'created_at')


