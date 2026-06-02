from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal
from django.utils import timezone
from restaurant.models import (
    Category, MenuItem, SpecialItem, ComboOffer, 
    Order, OrderItem, Customer, Payment, ContactMessage
)

class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Veggie Specialties",
            icon="bi-egg",
            order_index=1
        )

    def test_category_slug_auto_generation(self):
        """Verify that slug is automatically generated from name upon save."""
        self.assertEqual(self.category.slug, "veggie-specialties")

    def test_category_string_representation(self):
        """Verify the string representation returns the name."""
        self.assertEqual(str(self.category), "Veggie Specialties")


class MenuItemModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Meals",
            icon="bi-egg",
            order_index=2
        )
        self.menu_item = MenuItem.objects.create(
            name="Banana Leaf Meals",
            category=self.category,
            description="Pure vegetarian feast",
            price=15.00,
            is_available=True
        )

    def test_menu_item_string_representation(self):
        """Verify the string representation returns the name and category."""
        self.assertEqual(str(self.menu_item), "Banana Leaf Meals (Meals)")


class GeneralViewsTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Breakfast", slug="breakfast")
        self.item = MenuItem.objects.create(
            name="Idli Sambar",
            category=self.category,
            price=8.50,
            description="Steamed rice cakes",
            is_available=True
        )

    def test_home_page_status_code(self):
        """Verify that the home page renders successfully."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'restaurant/index.html')

    def test_menu_page_status_code(self):
        """Verify that the menu page renders successfully and contains category data."""
        response = self.client.get(reverse('menu'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'restaurant/menu.html')
        self.assertContains(response, "Idli Sambar")

    def test_contact_ajax_success(self):
        """Verify that AJAX contact submissions work with valid POST data."""
        post_data = {
            'name': 'Adil Riyadh',
            'phone': '+966501234567',
            'email': 'adil@example.com',
            'message': 'Looking for corporate catering details.'
        }
        response = self.client.post(
            reverse('contact_ajax'),
            data=post_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        
        # Verify message saved in DB
        self.assertEqual(ContactMessage.objects.count(), 1)
        msg = ContactMessage.objects.first()
        self.assertEqual(msg.name, 'Adil Riyadh')
        self.assertEqual(msg.phone, '+966501234567')


class CartViewsTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Meals", slug="meals")
        self.item = MenuItem.objects.create(
            name="Malabar Biriyani",
            category=self.category,
            price=18.00,
            is_available=True
        )

    def test_cart_add_ajax(self):
        """Test adding item to cart via AJAX."""
        post_data = {
            'item_id': self.item.id,
            'item_type': 'menu',
            'quantity': 2
        }
        response = self.client.post(
            reverse('cart_add'),
            data=post_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertTrue(json_data['success'])
        self.assertEqual(json_data['cart_len'], 2)
        
        # Verify session storage
        session = self.client.session
        self.assertIn('cart', session)
        self.assertIn(f"menu_{self.item.id}", session['cart'])
        self.assertEqual(session['cart'][f"menu_{self.item.id}"]['quantity'], 2)

    def test_cart_update_ajax(self):
        """Test updating cart quantity via AJAX."""
        # Pre-seed cart session
        session = self.client.session
        session['cart'] = {
            f"menu_{self.item.id}": {
                'item_id': str(self.item.id),
                'item_type': 'menu',
                'quantity': 2
            }
        }
        session.save()

        post_data = {
            'item_id': self.item.id,
            'item_type': 'menu',
            'quantity': 5
        }
        response = self.client.post(
            reverse('cart_update'),
            data=post_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertTrue(json_data['success'])
        self.assertEqual(json_data['cart_len'], 5)
        self.assertEqual(json_data['item_total'], 90.0) # 18 * 5
        self.assertEqual(json_data['cart_total'], 90.0)

    def test_cart_remove(self):
        """Test removing item from cart."""
        session = self.client.session
        session['cart'] = {
            f"menu_{self.item.id}": {
                'item_id': str(self.item.id),
                'item_type': 'menu',
                'quantity': 2
            }
        }
        session.save()

        post_data = {
            'item_id': self.item.id,
            'item_type': 'menu'
        }
        response = self.client.post(
            reverse('cart_remove'),
            data=post_data
        )
        self.assertRedirects(response, reverse('cart_detail'))
        session = self.client.session
        self.assertNotIn(f"menu_{self.item.id}", session['cart'])


class CheckoutAndTrackingTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Meals", slug="meals")
        self.item = MenuItem.objects.create(
            name="Kerala Meals",
            category=self.category,
            price=15.00,
            is_available=True
        )

    def test_checkout_view_redirect_when_empty(self):
        """Checkout should redirect to menu page if cart is empty."""
        response = self.client.get(reverse('checkout'))
        self.assertRedirects(response, reverse('menu'))

    def test_checkout_view_post_cash(self):
        """Test placing order with Cash payment option."""
        # Pre-seed cart
        session = self.client.session
        session['cart'] = {
            f"menu_{self.item.id}": {
                'item_id': str(self.item.id),
                'item_type': 'menu',
                'quantity': 2
            }
        }
        session.save()

        post_data = {
            'name': 'Hassan Riyadh',
            'phone': '+966507776666',
            'delivery_option': 'Dine-In',
            'address_or_table': 'Table 4',
            'notes': 'No spicy',
            'payment_method': 'Cash on Delivery'
        }
        response = self.client.post(
            reverse('checkout'),
            data=post_data
        )
        # Should redirect to success view
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertRedirects(response, reverse('order_success', args=[order.id]))
        
        self.assertEqual(order.customer_name, 'Hassan Riyadh')
        self.assertEqual(order.delivery_option, 'Dine-In')
        self.assertEqual(order.payment_method, 'Cash on Delivery')
        self.assertEqual(order.total_amount, Decimal('30.00')) # 15 * 2
        
        # Cart should be cleared
        session = self.client.session
        self.assertEqual(len(session.get('cart', {})), 0)

    def test_checkout_view_post_online_redirects(self):
        """Test that checkout redirects to Moyasar online view when Online selected."""
        session = self.client.session
        session['cart'] = {
            f"menu_{self.item.id}": {
                'item_id': str(self.item.id),
                'item_type': 'menu',
                'quantity': 1
            }
        }
        session.save()

        post_data = {
            'name': 'Hassan Riyadh',
            'phone': '+966507776666',
            'delivery_option': 'Delivery',
            'address_or_table': 'Olaya District, Riyadh',
            'payment_method': 'Online'
        }
        response = self.client.post(
            reverse('checkout'),
            data=post_data
        )
        order = Order.objects.first()
        self.assertRedirects(response, reverse('moyasar_checkout', args=[order.id]))

    def test_moyasar_verify_ajax_success(self):
        """Test successful simulation of Moyasar payment validation."""
        order = Order.objects.create(
            customer_name='Hassan Riyadh',
            phone='+966507776666',
            delivery_option='Delivery',
            address_or_table='Olaya District, Riyadh',
            total_amount=15.00,
            payment_method='Online',
            payment_status='Pending',
            status='Pending'
        )
        post_data = {
            'order_id': order.id,
            'card_number': '5888 4712 3456 7890', # Mock Saudi Mada card BIN
            'card_name': 'Hassan Riyadh',
            'cvv': '123'
        }
        response = self.client.post(
            reverse('moyasar_verify'),
            data=post_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertTrue(json_data['success'])
        
        order.refresh_from_db()
        self.assertEqual(order.payment_status, 'Paid')
        self.assertEqual(order.status, 'Confirmed')
        self.assertEqual(Payment.objects.count(), 1)
        self.assertEqual(Payment.objects.first().payment_gateway, 'Moyasar (Mada)')

    def test_order_tracking_lookup(self):
        """Verify that order tracking yields orders matching phone query."""
        customer = Customer.objects.create(name='Test Customer', phone='9665555555')
        order = Order.objects.create(
            customer=customer,
            customer_name='Test Customer',
            phone='9665555555',
            delivery_option='Takeaway',
            address_or_table='In 15 mins',
            total_amount=25.00,
            payment_status='Paid',
            status='Preparing'
        )
        response = self.client.get(reverse('order_tracking') + '?phone=9665555555')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "#CS-100" + str(order.id))
        self.assertContains(response, "In Kitchen")


class StaffDashboardTest(TestCase):
    def setUp(self):
        # Create staff user
        self.staff_user = User.objects.create_user(
            username='chef', password='chefpassword', is_staff=True
        )
        # Create normal user
        self.normal_user = User.objects.create_user(
            username='guest', password='guestpassword', is_staff=False
        )
        # Preseed orders
        self.order = Order.objects.create(
            customer_name='Loyal Customer',
            phone='+966500000000',
            delivery_option='Dine-In',
            address_or_table='Table 1',
            total_amount=50.00,
            payment_status='Paid',
            status='Pending'
        )

    def test_dashboard_restricted_to_staff(self):
        """Dashboard should deny access or redirect to login for non-staff."""
        # Not logged in
        response = self.client.get(reverse('staff_dashboard'))
        self.assertEqual(response.status_code, 302) # Redirect to login
        
        # Logged in as normal user
        self.client.login(username='guest', password='guestpassword')
        response = self.client.get(reverse('staff_dashboard'))
        self.assertEqual(response.status_code, 302) # Still redirect

    def test_dashboard_accessible_to_staff(self):
        """Staff user should access dashboard successfully and see order metrics."""
        self.client.login(username='chef', password='chefpassword')
        response = self.client.get(reverse('staff_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'restaurant/dashboard.html')
        self.assertContains(response, "Loyal Customer")
        self.assertContains(response, "50.00 SAR")

    def test_dashboard_update_order_status(self):
        """Staff user can update order status from dashboard."""
        self.client.login(username='chef', password='chefpassword')
        post_data = {
            'status': 'Preparing'
        }
        response = self.client.post(
            reverse('update_order_status', args=[self.order.id]),
            data=post_data
        )
        self.assertRedirects(response, reverse('staff_dashboard'))
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'Preparing')
