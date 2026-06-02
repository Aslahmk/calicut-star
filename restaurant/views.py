import time
from datetime import timedelta
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings
from django.db.models import Sum, Count
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required

from .models import (
    Category, MenuItem, SpecialItem, ComboOffer, 
    GalleryItem, Review, ContactMessage, Order, 
    OrderItem, Customer, Payment
)
from .cart import Cart

# ==============================================================================
# 1. Homepage & General Showcase
# ==============================================================================
def home_view(request):
    specials_list = SpecialItem.objects.filter(is_available=True)
    
    specials = {
        'Fish Specials': [],
        'Mutton Specials': [],
        'Beef Specials': [],
        'Chicken Specials': []
    }
    for item in specials_list:
        if item.category_group in specials:
            specials[item.category_group].append(item)

    combos = ComboOffer.objects.filter(is_available=True)
    gallery = GalleryItem.objects.all()
    reviews = Review.objects.filter(is_approved=True)[:6]
    
    # Non-JS fallback for contact form
    if request.method == 'POST' and not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email', '')
        message = request.POST.get('message')
        
        if name and phone and message:
            ContactMessage.objects.create(name=name, phone=phone, email=email, message=message)
            messages.success(request, "Your message has been sent successfully! We will get back to you shortly.")
        else:
            messages.error(request, "Please fill in all required fields.")
        return redirect('home')

    context = {
        'specials': specials,
        'combos': combos,
        'gallery': gallery,
        'reviews': reviews,
    }
    return render(request, 'restaurant/index.html', context)


@require_POST
def contact_ajax(request):
    """Asynchronous contact form submission."""
    name = request.POST.get('name')
    phone = request.POST.get('phone')
    email = request.POST.get('email', '')
    message = request.POST.get('message')
    
    if not name or not phone or not message:
        return JsonResponse({
            'success': False,
            'message': 'Please fill out all required fields (Name, Phone, and Message).'
        }, status=400)
    
    try:
        ContactMessage.objects.create(name=name, phone=phone, email=email, message=message)
        return JsonResponse({
            'success': True,
            'message': 'Thank you! Your message has been sent. We will contact you soon.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while sending your message. Please try again later.'
        }, status=500)


def menu_view(request):
    categories = Category.objects.all().order_by('order_index', 'name')
    menu_items = MenuItem.objects.filter(is_available=True).order_by('category__order_index', 'order_index', 'name')
    
    context = {
        'categories': categories,
        'menu_items': menu_items,
    }
    return render(request, 'restaurant/menu.html', context)


# ==============================================================================
# 2. Cart System Logic
# ==============================================================================
@require_POST
def cart_add(request):
    """AJAX handler to add items to the session-based cart."""
    cart = Cart(request)
    item_id = request.POST.get('item_id')
    item_type = request.POST.get('item_type') # 'menu' or 'combo' or 'special'
    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        quantity = 1
        
    if not item_id or not item_type:
        return JsonResponse({'success': False, 'message': 'Invalid parameters.'}, status=400)
        
    cart.add(item_id=item_id, item_type=item_type, quantity=quantity)
    return JsonResponse({
        'success': True,
        'message': 'Item added to cart successfully!',
        'cart_len': len(cart)
    })


@require_POST
def cart_update(request):
    """AJAX handler to update item quantities in the cart."""
    cart = Cart(request)
    item_id = request.POST.get('item_id')
    item_type = request.POST.get('item_type')
    try:
        quantity = int(request.POST.get('quantity'))
    except (ValueError, TypeError):
        return JsonResponse({'success': False, 'message': 'Invalid quantity.'}, status=400)
        
    if not item_id or not item_type:
        return JsonResponse({'success': False, 'message': 'Invalid parameters.'}, status=400)
        
    cart.update(item_id=item_id, item_type=item_type, quantity=quantity)
    
    # Calculate new item price total
    item_total = Decimal('0.00')
    try:
        if item_type == 'menu':
            item_total = MenuItem.objects.get(id=item_id).price * quantity
        elif item_type == 'special':
            item_total = SpecialItem.objects.get(id=item_id).price * quantity
        elif item_type == 'combo':
            item_total = ComboOffer.objects.get(id=item_id).special_price * quantity
    except Exception:
        pass
        
    return JsonResponse({
        'success': True,
        'item_total': float(item_total),
        'cart_total': float(cart.get_total_price()),
        'cart_len': len(cart)
    })


@require_POST
def cart_remove(request):
    """Standard POST handler to remove an item from the cart."""
    cart = Cart(request)
    item_id = request.POST.get('item_id')
    item_type = request.POST.get('item_type')
    if item_id and item_type:
        cart.remove(item_id=item_id, item_type=item_type)
        messages.success(request, "Item removed from cart.")
    return redirect('cart_detail')


def cart_detail(request):
    """Renders the cart review screen."""
    cart = Cart(request)
    context = {
        'cart': cart
    }
    return render(request, 'restaurant/cart.html', context)


# ==============================================================================
# 3. Checkout, Payments & WhatsApp Confirmation
# ==============================================================================
def checkout_view(request):
    """Manages order form collection and gateways routing."""
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, "Your cart is empty. Please add some delicious food items first!")
        return redirect('menu')
        
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        delivery_option = request.POST.get('delivery_option', 'Dine-In')
        address_or_table = request.POST.get('address_or_table', '')
        notes = request.POST.get('notes', '')
        payment_method = request.POST.get('payment_method', 'Cash on Delivery')
        
        if not name or not phone or not address_or_table:
            messages.error(request, "Please fill in all required customer details.")
            return render(request, 'restaurant/checkout.html', {'cart': cart})
            
        # 1. CRM Lookup/Registration
        customer, created = Customer.objects.get_or_create(phone=phone)
        customer.name = name
        if delivery_option == 'Delivery':
            customer.address = address_or_table
        customer.save()
        
        # 2. Register Order
        order = Order.objects.create(
            customer=customer,
            customer_name=name,
            phone=phone,
            delivery_option=delivery_option,
            address_or_table=address_or_table,
            total_amount=cart.get_total_price(),
            payment_method=payment_method,
            notes=notes,
            status='Pending',
            payment_status='Pending'
        )
        
        # 3. Register Order Items
        for item in cart:
            OrderItem.objects.create(
                order=order,
                item_name=item['name'],
                price=item['price'],
                quantity=item['quantity']
            )
            
        # 4. Route based on Payment Method
        if payment_method == 'Online':
            # Save order reference in session to check success later
            request.session['last_order_id'] = order.id
            return redirect('moyasar_checkout', order_id=order.id)
        else:
            # Cash on Delivery / Counter: Complete immediately
            cart.clear()
            messages.success(request, f"Order #CS-100{order.id} placed successfully!")
            return redirect('order_success', order_id=order.id)
            
    context = {
        'cart': cart
    }
    return render(request, 'restaurant/checkout.html', context)


def moyasar_checkout_view(request, order_id):
    """Renders the credit card/Mada entry simulation form."""
    order = get_object_or_404(Order, id=order_id)
    if order.payment_status == 'Paid':
        return redirect('order_success', order_id=order.id)
        
    context = {
        'order': order,
        'client_ip': request.META.get('REMOTE_ADDR', '127.0.0.1')
    }
    return render(request, 'restaurant/moyasar_checkout.html', context)


@require_POST
def moyasar_verify_ajax(request):
    """Simulates Moyasar payment authorization. Matches Saudi Mada cards."""
    order_id = request.POST.get('order_id')
    card_number = request.POST.get('card_number', '').replace(' ', '')
    card_name = request.POST.get('card_name', 'Mada Cardholder')
    cvv = request.POST.get('cvv', '')
    
    if not order_id or len(card_number) < 15 or len(cvv) < 3:
        return JsonResponse({'success': False, 'message': 'Invalid card payment details.'}, status=400)
        
    order = get_object_or_404(Order, id=order_id)
    
    # Simulation logic
    # In Saudi, card numbers starting with certain prefixes represent Mada cards (e.g. 588847, 440533, etc.)
    is_mada = card_number.startswith('588847') or card_number.startswith('589') or card_number.startswith('440533')
    
    # Simulate payment success
    transaction_id = f"txn_moyasar_{int(time.time())}"
    
    # Create Payment entry
    Payment.objects.create(
        order=order,
        transaction_id=transaction_id,
        amount=order.total_amount,
        payment_gateway='Moyasar (Mada)' if is_mada else 'Moyasar (Credit Card)',
        status='Paid'
    )
    
    # Update Order
    order.payment_status = 'Paid'
    order.status = 'Confirmed'
    order.save()
    
    # Clear cart from session
    cart = Cart(request)
    cart.clear()
    
    return JsonResponse({
        'success': True,
        'message': 'Payment authorized and captured successfully via Mada!' if is_mada else 'Payment authorized and captured successfully via Credit Card!',
        'transaction_id': transaction_id,
        'order_id': order.id
    })


def order_success_view(request, order_id):
    """Displays receipt confirmation summary."""
    order = get_object_or_404(Order, id=order_id)
    items_list = order.items.all()
    
    # Summary string for sharing
    items_summary = "\n".join([f"- {item.quantity}x {item.item_name}" for item in items_list])
    
    context = {
        'order': order,
        'items_list': items_list,
        'items_summary': items_summary
    }
    return render(request, 'restaurant/order_success.html', context)


# ==============================================================================
# 4. Order Tracking System
# ==============================================================================
def order_tracking_view(request):
    """Enables users to search historical/active orders by phone number."""
    phone = request.GET.get('phone', '').strip()
    orders = []
    
    if phone:
        orders = Order.objects.filter(phone__icontains=phone).order_by('-created_at')
        
    context = {
        'phone': phone,
        'orders': orders
    }
    return render(request, 'restaurant/tracking.html', context)


# ==============================================================================
# 5. Restaurant Staff Dashboard & Invoice Generation
# ==============================================================================
@staff_member_required
def staff_dashboard(request):
    """Executive panel displaying sales aggregation charts and status togglers."""
    today = timezone.localdate()
    start_of_today = timezone.make_aware(timezone.datetime(today.year, today.month, today.day, 0, 0, 0))
    
    # Metrics computations (for Paid or Delivered orders)
    completed_orders = Order.objects.filter(payment_status='Paid') | Order.objects.filter(status='Delivered')
    
    # Sales Aggregations
    sales_today = completed_orders.filter(created_at__gte=start_of_today).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    
    one_week_ago = start_of_today - timedelta(days=7)
    sales_weekly = completed_orders.filter(created_at__gte=one_week_ago).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    
    one_month_ago = start_of_today - timedelta(days=30)
    sales_monthly = completed_orders.filter(created_at__gte=one_month_ago).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    
    # Order counts by status
    orders_by_status = Order.objects.values('status').annotate(count=Count('id'))
    status_counts = {
        'Pending': 0, 'Confirmed': 0, 'Preparing': 0, 
        'Ready': 0, 'Out for Delivery': 0, 'Delivered': 0, 'Cancelled': 0
    }
    for item in orders_by_status:
        if item['status'] in status_counts:
            status_counts[item['status']] = item['count']
            
    # Alias with underscore for Django template dictionary lookup
    status_counts['Out_for_Delivery'] = status_counts.get('Out for Delivery', 0)
            
    # Popular Dishes (Top 5)
    popular_dishes = OrderItem.objects.values('item_name').annotate(
        total_qty=Sum('quantity'),
        total_sales=Sum('price')
    ).order_by('-total_qty')[:5]
    
    # Active orders listed in dashboard (non-delivered, non-cancelled)
    active_orders = Order.objects.exclude(status__in=['Delivered', 'Cancelled']).order_by('-created_at')
    
    # Selected Filter
    filter_status = request.GET.get('status_filter')
    if filter_status and filter_status in status_counts:
        dashboard_orders = Order.objects.filter(status=filter_status).order_by('-created_at')
    else:
        dashboard_orders = active_orders

    context = {
        'sales_today': sales_today,
        'sales_weekly': sales_weekly,
        'sales_monthly': sales_monthly,
        'status_counts': status_counts,
        'popular_dishes': popular_dishes,
        'dashboard_orders': dashboard_orders,
        'selected_filter': filter_status or 'Active'
    }
    return render(request, 'restaurant/dashboard.html', context)


@staff_member_required
@require_POST
def update_order_status(request, order_id):
    """Changes the state of an order in the dashboard."""
    new_status = request.POST.get('status')
    order = get_object_or_404(Order, id=order_id)
    
    if new_status in dict(Order.ORDER_STATUSES):
        order.status = new_status
        # Auto-mark payment if delivered or paid
        if new_status == 'Delivered' and order.payment_method != 'Online':
            order.payment_status = 'Paid'
        order.save()
        messages.success(request, f"Order #CS-100{order.id} status updated to {new_status}.")
    else:
        messages.error(request, "Invalid status choice.")
        
    return redirect('staff_dashboard')


def invoice_view(request, order_id):
    """Generates a print-friendly invoice slip."""
    order = get_object_or_404(Order, id=order_id)
    items_list = order.items.all()
    
    context = {
        'order': order,
        'items_list': items_list
    }
    return render(request, 'restaurant/invoice.html', context)
