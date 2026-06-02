# Calicut Star Restaurant Ordering and Management System Plan

Transform the existing website into a fully functional restaurant platform featuring shopping carts, checkout validation, Moyasar payment gateway integration (Saudi Arabia's native gateway supporting Mada cards), order tracking, invoice print generation, and an executive staff dashboard displaying sales analytics and statuses.

---

## User Review Required

> [!IMPORTANT]
> - **Session-Based Cart**: Cart data will persist in the client session using Django's session framework. This ensures anonymous visitors can easily build a cart without needing a mandatory account login first, boosting conversions.
> - **Saudi Payment Gateway (Moyasar)**: We will integrate Moyasar (supporting Mada, credit cards, Apple Pay) in test/simulation sandbox mode. Customers can pay online with Mada/Visa mockup cards or choose Cash/Card at Counter.
> - **Order Tracking**: Customers can enter their phone number on a dedicated page to view all current/past orders and track their delivery/preparation status in real-time.
> - **Restaurant Staff Dashboard**: A secure view (`/dashboard/`) restricted to staff will display key metrics (Daily/Weekly/Monthly sales, popular dishes, order statuses) and allow clicking to transition order states.
> - **Printable Invoice System**: Invoice generation will use clean CSS print styles allowing saving/printing directly as PDF from the browser.

---

## Proposed Changes

### 1. Backend Cart System (`restaurant/cart.py`)

#### [NEW] [cart.py](file:///e:/calicutstarweb/restaurant/cart.py)
Create a `Cart` class to manage session data:
- `add(item_id, item_type, quantity)`: Add a Menu Item or Combo Offer.
- `remove(item_id, item_type)`: Remove item.
- `update(item_id, item_type, quantity)`: Change quantity.
- `get_items()`: Iterate over items, fetching MenuItem or ComboOffer objects from DB.
- `get_total_price()`: Sum of all item prices multiplied by quantities.
- `clear()`: Empty cart.

### 2. Django Models (`restaurant/models.py`)

#### [MODIFY] [models.py](file:///e:/calicutstarweb/restaurant/models.py)
Expand schemas to support order tracking, payment processing, and dashboard analytics:
- `Order` (update fields):
  - `status`: choices ('Pending', 'Confirmed', 'Preparing', 'Ready', 'Out for Delivery', 'Delivered', 'Cancelled')
  - `payment_method`: choices ('Online', 'Cash on Delivery', 'Card at Counter')
  - `notes`: TextField (Kitchen notes)
- `Payment`:
  - `order`: ForeignKey to `Order`
  - `transaction_id`: CharField
  - `amount`: DecimalField
  - `payment_gateway`: CharField (e.g. 'Moyasar')
  - `status`: CharField ('Paid', 'Failed', 'Refunded')
  - `created_at`: DateTimeField

### 3. Views & Business Logic (`restaurant/views.py`)

#### [MODIFY] [views.py](file:///e:/calicutstarweb/restaurant/views.py)
Add order management, cart, checkout, payment, tracking, and dashboard logic:
- **Cart Views**:
  - `cart_add`: AJAX/POST to add items.
  - `cart_remove`: POST to remove.
  - `cart_update`: POST to update quantity.
  - `cart_detail`: Renders the cart review page.
- **Checkout View**:
  - `checkout_view`: Collects customer information. Validates address/table requirements.
  - If Cash/Counter: Saves order, clears cart, redirects to success receipt.
  - If Online: Renders Moyasar payment page.
- **Moyasar Payment Views**:
  - `moyasar_checkout`: Renders the credit card/Mada entry form.
  - `moyasar_verify`: Verifies the mock payment token and marks order as Paid.
- **Order Tracking View**:
  - `order_tracking_view`: Renders status verification. Queries orders by phone number.
- **Staff Dashboard View**:
  - `staff_dashboard`: Staff-only page displaying sales summary charts, status filter counters, top dishes, and status modifiers.
- **Invoice View**:
  - `invoice_view`: Clean printable invoice sheet showing details, prices, and payment methods.

### 4. Frontend & Navigation Templates (`templates/restaurant/`)

#### [NEW] [cart.html](file:///e:/calicutstarweb/templates/restaurant/cart.html)
- Interactive cart review page showing item list, prices, totals, quantity adjustments, and a checkout button.

#### [NEW] [checkout.html](file:///e:/calicutstarweb/templates/restaurant/checkout.html)
- Elegant checkout form with customer details, dine-in/delivery toggles, kitchen notes, and payment mode selector.

#### [NEW] [tracking.html](file:///e:/calicutstarweb/templates/restaurant/tracking.html)
- Form where users search by phone, listing active orders with color-coded status badges (e.g. "Preparing" in orange, "Delivered" in green).

#### [NEW] [dashboard.html](file:///e:/calicutstarweb/templates/restaurant/dashboard.html)
- Premium staff control center displaying analytics counters, list of orders grouped by status, sales summaries, and quick status action updates.

#### [NEW] [invoice.html](file:///e:/calicutstarweb/templates/restaurant/invoice.html)
- Clean, premium invoice slip with restaurant logo, date, and items list, formatted with printing layouts.

---

## Verification Plan

### Automated Tests
- Extend `tests.py` to:
  - Test Cart addition, updates, and removals in session storage.
  - Test Order state updates.
  - Test dashboard Sales aggregation logic.

### Manual Verification
1. Add items to cart from the Menu page. Verify cart badge counter updates.
2. Open Cart page, modify quantities, and confirm total updates.
3. Submit checkout:
   - Check **Cash** option: verifies redirect to Success and prints correct receipt.
   - Check **Moyasar Online**: completes mockup payment verification.
4. Input phone number on `/tracking/` to verify orders are listed with correct statuses.
5. Log in as staff, go to `/dashboard/`, change order statuses, and verify dashboard metrics update.
