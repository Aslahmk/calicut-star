document.addEventListener('DOMContentLoaded', () => {

    /* ==========================================================================
       1. Sticky Navigation & Scroll Events
       ========================================================================== */
    const navbar = document.querySelector('.custom-navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    /* ==========================================================================
       2. Scroll Animations (IntersectionObserver)
       ========================================================================== */
    const animElements = document.querySelectorAll('[data-fade-in]');
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('appear');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        
        animElements.forEach(el => observer.observe(el));
    } else {
        // Fallback for older browsers
        animElements.forEach(el => el.classList.add('appear'));
    }

    /* ==========================================================================
       3. Lightbox Gallery Controller
       ========================================================================== */
    const galleryItems = document.querySelectorAll('.gallery-item-card');
    const lightbox = document.getElementById('lightbox-modal');
    
    if (galleryItems.length > 0 && lightbox) {
        const lightboxImg = lightbox.querySelector('.lightbox-img');
        const lightboxCaption = lightbox.querySelector('.lightbox-caption');
        const closeBtn = lightbox.querySelector('.lightbox-close');
        const prevBtn = lightbox.querySelector('.lightbox-prev');
        const nextBtn = lightbox.querySelector('.lightbox-next');
        
        let currentIndex = 0;
        let activeGallery = [];

        // Build list of active items based on current filters
        function updateActiveGallery() {
            activeGallery = [];
            galleryItems.forEach(item => {
                if (item.style.display !== 'none') {
                    activeGallery.push({
                        src: item.getAttribute('data-image-src'),
                        title: item.getAttribute('data-title'),
                        caption: item.getAttribute('data-caption')
                    });
                }
            });
        }

        function showImage(index) {
            if (activeGallery.length === 0) return;
            // Bound checks
            if (index >= activeGallery.length) index = 0;
            if (index < 0) index = activeGallery.length - 1;
            
            currentIndex = index;
            const imgData = activeGallery[currentIndex];
            
            lightboxImg.src = imgData.src;
            lightboxCaption.innerHTML = `<strong>${imgData.title}</strong>${imgData.caption ? ' - ' + imgData.caption : ''}`;
        }

        // Open Lightbox
        galleryItems.forEach((card) => {
            card.addEventListener('click', () => {
                updateActiveGallery();
                const currentSrc = card.getAttribute('data-image-src');
                const foundIndex = activeGallery.findIndex(item => item.src === currentSrc);
                
                lightbox.style.display = 'flex';
                document.body.style.overflow = 'hidden'; // Stop scroll
                
                showImage(foundIndex !== -1 ? foundIndex : 0);
            });
        });

        // Close functions
        const closeLightbox = () => {
            lightbox.style.display = 'none';
            document.body.style.overflow = 'auto'; // Re-enable scroll
        };

        closeBtn.addEventListener('click', closeLightbox);
        lightbox.addEventListener('click', (e) => {
            if (e.target === lightbox || e.target.classList.contains('lightbox-content-wrapper')) {
                closeLightbox();
            }
        });

        // Prev / Next actions
        prevBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            showImage(currentIndex - 1);
        });
        nextBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            showImage(currentIndex + 1);
        });

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (lightbox.style.display === 'flex') {
                if (e.key === 'Escape') closeLightbox();
                if (e.key === 'ArrowRight') showImage(currentIndex + 1);
                if (e.key === 'ArrowLeft') showImage(currentIndex - 1);
            }
        });
    }

    /* ==========================================================================
       4. Gallery Filtering Logic
       ========================================================================== */
    const filterButtons = document.querySelectorAll('.gallery-filter-btn');
    if (filterButtons.length > 0) {
        filterButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                // Set active class
                filterButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                const filterValue = btn.getAttribute('data-filter');
                
                galleryItems.forEach(item => {
                    const itemCategory = item.getAttribute('data-category');
                    if (filterValue === 'all' || itemCategory === filterValue) {
                        item.style.display = 'block';
                    } else {
                        item.style.display = 'none';
                    }
                });
            });
        });
    }

    /* ==========================================================================
       5. Menu Page Search and Filters
       ========================================================================== */
    const menuSearchInput = document.getElementById('menu-search-input');
    const menuFilterButtons = document.querySelectorAll('.menu-filter-btn');
    const menuItemCards = document.querySelectorAll('.menu-item-col');

    if (menuSearchInput || menuFilterButtons.length > 0) {
        let activeCategoryFilter = 'all';
        let searchQuery = '';

        const filterMenu = () => {
            menuItemCards.forEach(col => {
                const card = col.querySelector('.food-card');
                const title = card.querySelector('.food-card-title').textContent.toLowerCase();
                const desc = card.querySelector('.food-card-text').textContent.toLowerCase();
                const category = card.getAttribute('data-category');

                const matchesCategory = (activeCategoryFilter === 'all' || category === activeCategoryFilter);
                const matchesSearch = (title.includes(searchQuery) || desc.includes(searchQuery));

                if (matchesCategory && matchesSearch) {
                    col.style.display = 'block';
                } else {
                    col.style.display = 'none';
                }
            });

            // Handle empty search / filter results helper
            const visibleItems = Array.from(menuItemCards).filter(col => col.style.display !== 'none');
            const noResultsMsg = document.getElementById('menu-no-results');
            if (noResultsMsg) {
                if (visibleItems.length === 0) {
                    noResultsMsg.classList.remove('d-none');
                } else {
                    noResultsMsg.classList.add('d-none');
                }
            }
        };

        if (menuSearchInput) {
            menuSearchInput.addEventListener('input', (e) => {
                searchQuery = e.target.value.toLowerCase().trim();
                filterMenu();
            });
        }

        if (menuFilterButtons.length > 0) {
            menuFilterButtons.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    menuFilterButtons.forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');

                    activeCategoryFilter = btn.getAttribute('data-filter');
                    filterMenu();
                });
            });
        }
    }

    /* ==========================================================================
       6. Contact Form AJAX Submission
       ========================================================================== */
    const contactForm = document.getElementById('contact-form');
    const formFeedback = document.getElementById('form-feedback');

    if (contactForm && formFeedback) {
        contactForm.addEventListener('submit', (e) => {
            e.preventDefault();

            // Setup form data
            const formData = new FormData(contactForm);
            const submitBtn = contactForm.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerHTML;
            
            // Set loading state
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Sending...';
            
            // Hide previous feedback
            formFeedback.classList.add('d-none');
            formFeedback.className = 'alert mt-3 d-none';

            // Send AJAX POST
            fetch(contactForm.getAttribute('action'), {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                return response.json().then(data => {
                    if (!response.ok) {
                        throw new Error(data.message || 'Something went wrong');
                    }
                    return data;
                });
            })
            .then(data => {
                // Success
                formFeedback.classList.remove('d-none');
                formFeedback.classList.add('alert-success');
                formFeedback.innerHTML = `<i class="bi bi-check-circle-fill me-2"></i> ${data.message}`;
                contactForm.reset();
            })
            .catch(error => {
                // Error
                formFeedback.classList.remove('d-none');
                formFeedback.classList.add('alert-danger');
                formFeedback.innerHTML = `<i class="bi bi-exclamation-triangle-fill me-2"></i> ${error.message}`;
            })
            .finally(() => {
                // Reset button state
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
            });
        });
    }

    /* ==========================================================================
       7. Checkout Modal & Razorpay Controller
       ========================================================================== */
    const checkoutModalEl = document.getElementById('checkoutModal');
    if (checkoutModalEl) {
        const checkoutModal = new bootstrap.Modal(checkoutModalEl);
        
        // Modal inputs
        const modalItemName = document.getElementById('modal-item-name');
        const modalItemPrice = document.getElementById('modal-item-price');
        const modalItemQuantity = document.getElementById('modal-item-quantity');
        const modalItemId = document.getElementById('modal-item-id');
        const modalItemType = document.getElementById('modal-item-type');
        const modalItemRawPrice = document.getElementById('modal-item-raw-price');
        
        const qtyMinusBtn = document.getElementById('qty-minus');
        const qtyPlusBtn = document.getElementById('qty-plus');
        
        const deliveryRadios = document.querySelectorAll('input[name="delivery_option"]');
        const locationLabel = document.getElementById('location-label');
        const locationInput = document.getElementById('checkout-location');
        
        const payOnlineBtn = document.getElementById('pay-online-btn');
        const orderWhatsappBtn = document.getElementById('order-whatsapp-btn');
        const checkoutFeedback = document.getElementById('checkout-feedback');
        const checkoutForm = document.getElementById('checkout-form');

        let currentQty = 1;
        let unitPrice = 0.00;

        // Update Total Price display
        function updateTotalPrice() {
            const total = (unitPrice * currentQty).toFixed(2);
            modalItemPrice.textContent = `${total} SAR`;
        }

        // Delegate trigger events on buttons (handles dynamic elements)
        document.body.addEventListener('click', (e) => {
            const triggerBtn = e.target.closest('.trigger-checkout');
            if (triggerBtn) {
                const itemId = triggerBtn.getAttribute('data-item-id');
                const itemName = triggerBtn.getAttribute('data-item-name');
                const itemPrice = parseFloat(triggerBtn.getAttribute('data-item-price'));
                const itemType = triggerBtn.getAttribute('data-item-type');

                modalItemName.textContent = itemName;
                modalItemId.value = itemId;
                modalItemType.value = itemType;
                modalItemRawPrice.value = itemPrice;
                
                unitPrice = itemPrice;
                currentQty = 1;
                modalItemQuantity.value = currentQty;
                
                updateTotalPrice();
                checkoutFeedback.className = 'alert mt-3 d-none'; // Clear feedback
            }
        });

        // Quantity handlers
        qtyMinusBtn.addEventListener('click', () => {
            if (currentQty > 1) {
                currentQty--;
                modalItemQuantity.value = currentQty;
                updateTotalPrice();
            }
        });

        qtyPlusBtn.addEventListener('click', () => {
            currentQty++;
            modalItemQuantity.value = currentQty;
            updateTotalPrice();
        });

        // Service Type Toggle changes label and placeholder
        deliveryRadios.forEach(radio => {
            radio.addEventListener('change', () => {
                const serviceType = radio.value;
                if (serviceType === 'Dine-In') {
                    locationLabel.innerHTML = 'Table Number <span class="text-danger">*</span>';
                    locationInput.placeholder = 'e.g. Table 5';
                    locationInput.required = true;
                } else if (serviceType === 'Takeaway') {
                    locationLabel.innerHTML = 'Pickup Note (Optional)';
                    locationInput.placeholder = 'e.g. In 15 minutes';
                    locationInput.required = false;
                } else if (serviceType === 'Delivery') {
                    locationLabel.innerHTML = 'Delivery Address <span class="text-danger">*</span>';
                    locationInput.placeholder = 'Enter building name, street, neighborhood';
                    locationInput.required = true;
                }
            });
        });

        // Validation helper
        function validateForm() {
            const name = document.getElementById('checkout-name').value.trim();
            const phone = document.getElementById('checkout-phone').value.trim();
            const option = document.querySelector('input[name="delivery_option"]:checked').value;
            const location = locationInput.value.trim();

            if (!name || !phone) {
                showFeedback('Please fill out Name and Phone fields.', 'danger');
                return false;
            }
            if ((option === 'Dine-In' || option === 'Delivery') && !location) {
                showFeedback(option === 'Dine-In' ? 'Table number is required.' : 'Delivery address is required.', 'danger');
                return false;
            }
            return { name, phone, option, location };
        }

        function showFeedback(msg, type) {
            checkoutFeedback.className = `alert mt-3 alert-${type}`;
            checkoutFeedback.innerHTML = msg;
            checkoutFeedback.classList.remove('d-none');
        }

        // ACTION 1: PAY ONLINE (RAZORPAY)
        payOnlineBtn.addEventListener('click', () => {
            const validation = validateForm();
            if (!validation) return;

            // Set loading state
            payOnlineBtn.disabled = true;
            const originalText = payOnlineBtn.innerHTML;
            payOnlineBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
            checkoutFeedback.className = 'alert mt-3 d-none';

            // Post to create-order
            const formData = new FormData(checkoutForm);
            formData.append('name', validation.name);
            formData.append('phone', validation.phone);
            formData.append('delivery_option', validation.option);
            formData.append('address_or_table', validation.location);
            formData.append('quantity', currentQty);
            formData.append('payment_method', 'Razorpay');

            fetch(checkoutForm.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(res => {
                return res.json().then(data => {
                    if (!res.ok) throw new Error(data.message || 'Payment initiation failed.');
                    return data;
                });
            })
            .then(data => {
                // Check if sandbox simulation is active
                if (data.is_sandbox) {
                    const confirmPayment = confirm(`[Sandbox Mode]\nSimulate a successful online card payment of ${(data.amount / 100).toFixed(2)} SAR for ${data.item_name}?`);
                    if (confirmPayment) {
                        const mockPaymentId = `pay_mock_${Date.now()}`;
                        const mockSignature = `sig_mock_${Math.random().toString(36).substr(2, 9)}`;
                        verifyPayment(mockPaymentId, data.razorpay_order_id, mockSignature, data.order_id);
                    } else {
                        payOnlineBtn.disabled = false;
                        payOnlineBtn.innerHTML = originalText;
                        showFeedback('Sandbox payment simulation cancelled by user.', 'warning');
                    }
                    return;
                }

                // Launch Razorpay
                const options = {
                    "key": data.key_id,
                    "amount": data.amount,
                    "currency": data.currency,
                    "name": "Calicut Star",
                    "description": `Order of ${data.item_name}`,
                    "order_id": data.razorpay_order_id,
                    "handler": function (response) {
                        // Success Handler - verify signature
                        verifyPayment(response.razorpay_payment_id, response.razorpay_order_id, response.razorpay_signature, data.order_id);
                    },
                    "prefill": {
                        "name": data.customer_name,
                        "contact": data.phone
                    },
                    "theme": {
                        "color": "#0B5D3B" // Brand Green
                    },
                    "modal": {
                        "ondismiss": function() {
                            payOnlineBtn.disabled = false;
                            payOnlineBtn.innerHTML = originalText;
                            showFeedback('Payment window closed. Order is still pending.', 'warning');
                        }
                    }
                };
                const rzp = new Razorpay(options);
                rzp.open();
            })
            .catch(err => {
                showFeedback(err.message, 'danger');
                payOnlineBtn.disabled = false;
                payOnlineBtn.innerHTML = originalText;
            });
        });

        // Verify signature helper
        function verifyPayment(paymentId, orderId, signature, localOrderId) {
            showFeedback('Verifying payment, please wait...', 'info');
            
            const verifyData = new FormData();
            verifyData.append('razorpay_payment_id', paymentId);
            verifyData.append('razorpay_order_id', orderId);
            verifyData.append('razorpay_signature', signature);
            verifyData.append('local_order_id', localOrderId);

            // Get CSRF Token
            const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
            
            fetch('/checkout/verify/', {
                method: 'POST',
                body: verifyData,
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    // Redirect to success screen
                    window.location.href = `/order/success/${localOrderId}/`;
                } else {
                    showFeedback(data.message, 'danger');
                    resetPayButton();
                }
            })
            .catch(err => {
                showFeedback('Payment verification connection error.', 'danger');
                resetPayButton();
            });
        }

        function resetPayButton() {
            payOnlineBtn.disabled = false;
            payOnlineBtn.innerHTML = '<i class="bi bi-credit-card-2-front-fill me-2"></i>Pay Online (Razorpay)';
        }

        // ACTION 2: ORDER & PAY CASH VIA WHATSAPP
        orderWhatsappBtn.addEventListener('click', () => {
            const validation = validateForm();
            if (!validation) return;

            orderWhatsappBtn.disabled = true;
            const originalText = orderWhatsappBtn.innerHTML;
            orderWhatsappBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...';

            const formData = new FormData(checkoutForm);
            formData.append('name', validation.name);
            formData.append('phone', validation.phone);
            formData.append('delivery_option', validation.option);
            formData.append('address_or_table', validation.location);
            formData.append('quantity', currentQty);
            formData.append('payment_method', 'WhatsApp');

            fetch(checkoutForm.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(res => {
                return res.json().then(data => {
                    if (!res.ok) throw new Error(data.message || 'Failed to register order.');
                    return data;
                });
            })
            .then(data => {
                // Success: close modal, open WhatsApp
                checkoutModal.hide();
                checkoutForm.reset();
                orderWhatsappBtn.disabled = false;
                orderWhatsappBtn.innerHTML = originalText;
                
                // Formulate WhatsApp message text
                const restaurantPhone = "966509653846";
                const messageText = `Hello Calicut Star! I would like to place an order (Cash payment/COD).

*Order Details*:
- ${data.quantity}x ${data.item_name} (${data.total_amount} SAR)

*Order Reference*: #CS-100${data.order_id}
*Customer Name*: ${data.customer_name}
*Phone*: ${data.phone}
*Service Type*: ${data.delivery_option}
*Table/Address*: ${data.address_or_table}

Please confirm and prepare my order!`;

                const whatsappUrl = `https://wa.me/${restaurantPhone}?text=${encodeURIComponent(messageText)}`;
                window.open(whatsappUrl, '_blank');
            })
            .catch(err => {
                showFeedback(err.message, 'danger');
                orderWhatsappBtn.disabled = false;
                orderWhatsappBtn.innerHTML = originalText;
            });
        });
    }

    /* ==========================================================================
       8. AJAX Shopping Cart Handlers & Toast System
       ========================================================================== */
    function showToast(message, type = 'success') {
        let container = document.getElementById('toast-container-custom');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container-custom';
            container.style.position = 'fixed';
            container.style.top = '100px';
            container.style.right = '20px';
            container.style.zIndex = '9999';
            container.style.display = 'flex';
            container.style.flexDirection = 'column';
            container.style.gap = '10px';
            container.style.maxWidth = '350px';
            document.body.appendChild(container);
        }
        
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} shadow-lg border-0 fade show d-flex align-items-center justify-content-between`;
        toast.role = 'alert';
        toast.style.margin = '0';
        toast.style.borderRadius = '8px';
        toast.style.padding = '15px 20px';
        toast.style.minWidth = '280px';
        toast.style.backgroundColor = type === 'success' ? '#0B5D3B' : '#DC3545';
        toast.style.color = '#FFFFFF';
        toast.style.borderLeft = type === 'success' ? '5px solid #D4A017' : '5px solid #FFEBEB';
        
        toast.innerHTML = `
            <div style="font-size: 0.9rem; font-weight: 500; text-align: left;">${message}</div>
            <button type="button" class="btn-close btn-close-white ms-3" style="font-size: 0.75rem; flex-shrink: 0;" aria-label="Close"></button>
        `;
        
        toast.querySelector('.btn-close').addEventListener('click', () => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        });
        
        container.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    }

    // Handle Add to Cart button clicks
    document.body.addEventListener('click', (e) => {
        const addBtn = e.target.closest('.add-to-cart-btn');
        if (addBtn) {
            e.preventDefault();
            const itemId = addBtn.getAttribute('data-item-id');
            const itemName = addBtn.getAttribute('data-item-name');
            const itemType = addBtn.getAttribute('data-item-type');
            
            addBtn.disabled = true;
            const originalHtml = addBtn.innerHTML;
            addBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Adding...';
            
            const formData = new FormData();
            formData.append('item_id', itemId);
            formData.append('item_type', itemType);
            formData.append('quantity', 1);
            
            const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
            const csrfToken = csrfInput ? csrfInput.value : '';
            
            fetch('/cart/add/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(res => res.json())
            .then(data => {
                addBtn.disabled = false;
                addBtn.innerHTML = originalHtml;
                
                if (data.success) {
                    const badge = document.getElementById('cart-badge');
                    if (badge) {
                        badge.textContent = data.cart_len;
                        badge.style.display = data.cart_len > 0 ? 'inline-block' : 'none';
                    }
                    showToast(`Added <strong>${itemName}</strong> to cart! <a href="/cart/" class="text-warning text-decoration-underline ms-2" style="font-weight: 700;">View Cart</a>`, 'success');
                } else {
                    showToast(data.message || 'Failed to add item to cart.', 'danger');
                }
            })
            .catch(err => {
                addBtn.disabled = false;
                addBtn.innerHTML = originalHtml;
                showToast('Connection error occurred.', 'danger');
            });
        }
    });
});
