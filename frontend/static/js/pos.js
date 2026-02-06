/* POS Interface JavaScript - simplified, defensive, and fully logged */

let billItems = [];

// Consistent INR formatting
const formatINR = (value) => '₹' + numberOrZero(value).toFixed(2);

// Utility
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function numberOrZero(value) {
    const num = parseFloat(value);
    return isNaN(num) ? 0 : num;
}

// Init
document.addEventListener('DOMContentLoaded', function initPOS() {
    if (typeof products === 'undefined' || !Array.isArray(products)) {
        console.error('Products data missing');
        alert('Product data not loaded. Refresh the page.');
        return;
    }

    console.log('POS loaded with', products.length, 'products');
    bindSearch();
    bindTotals();
    bindForm();
    renderItems();
});

// Search and add
function bindSearch() {
    const input = document.getElementById('product_search');
    const list = document.getElementById('autocomplete_list');
    if (!input || !list) return;

    input.addEventListener('input', () => {
        const q = input.value.toLowerCase().trim();
        if (!q) {
            list.style.display = 'none';
            return;
        }

        const matches = products.filter(p =>
            (p.product_name || '').toLowerCase().includes(q) ||
            (p.barcode || '').toLowerCase().includes(q) ||
            (p.sku || '').toLowerCase().includes(q)
        );

        if (matches.length === 0) {
            list.innerHTML = '<div class="autocomplete-item">No products found</div>';
            list.style.display = 'block';
            return;
        }

        list.innerHTML = matches.map(p => `
            <div class="autocomplete-item" data-id="${p.id}" data-name="${escapeHtml(p.product_name)}" data-price="${p.selling_price}" data-stock="${p.quantity_on_hand}">
                <strong>${escapeHtml(p.product_name)}</strong><br>
                <small>${formatINR(p.selling_price)} | Stock: ${p.quantity_on_hand}</small>
            </div>
        `).join('');

        list.querySelectorAll('.autocomplete-item').forEach(el => {
            el.addEventListener('click', () => {
                const id = parseInt(el.dataset.id, 10);
                const name = el.dataset.name;
                const price = numberOrZero(el.dataset.price);
                const stock = parseInt(el.dataset.stock, 10) || 0;
                addItem(id, name, price, stock);
                list.style.display = 'none';
                input.value = '';
            });
        });

        list.style.display = 'block';
    });

    document.addEventListener('click', (e) => {
        if (!list.contains(e.target) && e.target !== input) list.style.display = 'none';
    });
}

function addItem(id, name, price, stock) {
    const existing = billItems.find(i => i.productId === id);
    if (existing) {
        if (existing.quantity >= stock) {
            alert('Insufficient stock for this product');
            return;
        }
        existing.quantity += 1;
        existing.lineTotal = existing.quantity * existing.unitPrice;
    } else {
        billItems.push({
            productId: id,
            productName: name,
            unitPrice: price,
            quantity: 1,
            lineTotal: price,
            availableStock: stock
        });
    }
    renderItems();
    updateTotals();
}

// Render cart
function renderItems() {
    const container = document.getElementById('bill_items');
    if (!container) return;

    if (billItems.length === 0) {
        container.innerHTML = '<p class="text-muted mt-3">No items added yet</p>';
        return;
    }

    container.innerHTML = `
        <table class="table table-sm mt-3">
            <thead>
                <tr>
                    <th>Product</th>
                    <th>Price</th>
                    <th width="140">Qty</th>
                    <th>Total</th>
                    <th width="50"></th>
                </tr>
            </thead>
            <tbody>
                ${billItems.map((item, idx) => `
                    <tr>
                        <td><strong>${escapeHtml(item.productName)}</strong></td>
                        <td>
                            <div class="input-group input-group-sm">
                                <button type="button" class="btn btn-outline-secondary btn-sm" data-idx="${idx}" data-role="price-down">
                                    <i class="fas fa-minus"></i>
                                </button>
                                <input type="number" class="form-control form-control-sm text-center" step="0.01" value="${item.unitPrice.toFixed(2)}" data-idx="${idx}" data-role="price" style="max-width: 80px;">
                                <button type="button" class="btn btn-outline-secondary btn-sm" data-idx="${idx}" data-role="price-up">
                                    <i class="fas fa-plus"></i>
                                </button>
                            </div>
                        </td>
                        <td>
                            <div class="input-group input-group-sm">
                                <button type="button" class="btn btn-outline-secondary btn-sm" data-idx="${idx}" data-role="qty-down">
                                    <i class="fas fa-minus"></i>
                                </button>
                                <input type="number" class="form-control form-control-sm text-center" min="1" max="${item.availableStock}" value="${item.quantity}" data-idx="${idx}" data-role="qty" style="max-width: 60px;">
                                <button type="button" class="btn btn-outline-secondary btn-sm" data-idx="${idx}" data-role="qty-up">
                                    <i class="fas fa-plus"></i>
                                </button>
                            </div>
                        </td>
                        <td><strong>${formatINR(item.lineTotal)}</strong></td>
                        <td>
                            <button type="button" class="btn btn-sm btn-danger" data-idx="${idx}" data-role="remove" title="Remove">
                                <i class="fas fa-trash"></i>
                            </button>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;

    // Quantity change
    container.querySelectorAll('[data-role="qty"]').forEach(input => {
        input.addEventListener('change', () => {
            const idx = parseInt(input.dataset.idx, 10);
            const q = parseInt(input.value, 10) || 0;
            updateQty(idx, q);
        });
    });

    // Price change
    container.querySelectorAll('[data-role="price"]').forEach(input => {
        input.addEventListener('change', () => {
            const idx = parseInt(input.dataset.idx, 10);
            const p = numberOrZero(input.value);
            updatePrice(idx, p);
        });
    });

    // Quantity +/- buttons
    container.querySelectorAll('[data-role="qty-up"]').forEach(btn => {
        btn.addEventListener('click', () => {
            const idx = parseInt(btn.dataset.idx, 10);
            const item = billItems[idx];
            if (item && item.quantity < item.availableStock) {
                updateQty(idx, item.quantity + 1);
            }
        });
    });

    container.querySelectorAll('[data-role="qty-down"]').forEach(btn => {
        btn.addEventListener('click', () => {
            const idx = parseInt(btn.dataset.idx, 10);
            const item = billItems[idx];
            if (item && item.quantity > 1) {
                updateQty(idx, item.quantity - 1);
            }
        });
    });

    // Price +/- buttons
    container.querySelectorAll('[data-role="price-up"]').forEach(btn => {
        btn.addEventListener('click', () => {
            const idx = parseInt(btn.dataset.idx, 10);
            const item = billItems[idx];
            if (item) {
                updatePrice(idx, item.unitPrice + 10);
            }
        });
    });

    container.querySelectorAll('[data-role="price-down"]').forEach(btn => {
        btn.addEventListener('click', () => {
            const idx = parseInt(btn.dataset.idx, 10);
            const item = billItems[idx];
            if (item) {
                updatePrice(idx, Math.max(0, item.unitPrice - 10));
            }
        });
    });

    // Remove button
    container.querySelectorAll('[data-role="remove"]').forEach(btn => {
        btn.addEventListener('click', () => {
            const idx = parseInt(btn.dataset.idx, 10);
            removeItem(idx);
        });
    });
}

function updateQty(idx, qty) {
    if (isNaN(qty) || qty <= 0) {
        removeItem(idx);
        return;
    }
    const item = billItems[idx];
    if (!item) return;
    if (qty > item.availableStock) {
        alert('Quantity exceeds available stock (' + item.availableStock + ')');
        qty = item.availableStock;
    }
    item.quantity = qty;
    item.lineTotal = item.quantity * item.unitPrice;
    renderItems();
    updateTotals();
}

function updatePrice(idx, price) {
    const item = billItems[idx];
    if (!item) return;
    price = numberOrZero(price);
    if (price < 0) price = 0;
    item.unitPrice = parseFloat(price.toFixed(2));
    item.lineTotal = item.quantity * item.unitPrice;
    renderItems();
    updateTotals();
}

function removeItem(idx) {
    billItems.splice(idx, 1);
    renderItems();
    updateTotals();
}

function clearBill() {
    if (billItems.length && !confirm('Clear all items from the bill?')) return;
    billItems = [];
    renderItems();
    updateTotals();
}

// Totals
function bindTotals() {
    ['discount', 'tax', 'amount_paid', 'customer_name', 'customer_phone', 'customer_email'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.addEventListener('input', updateTotals);
    });
    updateTotals();
}

function updateTotals() {
    const discountEl = document.getElementById('discount');
    const taxEl = document.getElementById('tax');
    const amountPaidEl = document.getElementById('amount_paid');

    const subtotal = billItems.reduce((sum, i) => sum + i.lineTotal, 0);
    const discount = numberOrZero(discountEl ? discountEl.value : 0);
    const taxPct = numberOrZero(taxEl ? taxEl.value : 0);

    const subtotalAfterDiscount = subtotal - discount;
    const taxAmount = (subtotalAfterDiscount * taxPct) / 100;
    const total = subtotalAfterDiscount + taxAmount;
    
    // Get amount paid - if empty, assume full payment
    const amountPaidValue = amountPaidEl && amountPaidEl.value ? numberOrZero(amountPaidEl.value) : null;
    const amountPaid = amountPaidValue !== null ? amountPaidValue : total;
    const remainingAmount = Math.max(0, total - amountPaid);

    const setText = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.textContent = val;
    };

    setText('item_count', billItems.length);
    setText('subtotal', formatINR(subtotal));
    setText('tax_amount', formatINR(taxAmount));
    setText('total', formatINR(total));
    setText('remaining_amount', formatINR(remainingAmount));

    const billDataInput = document.getElementById('bill_data');
    if (billDataInput) {
        const billData = {
            items: billItems.map(i => ({
                product_id: i.productId,
                quantity: i.quantity
            })),
            customer_name: (document.getElementById('customer_name') && document.getElementById('customer_name').value) || 'Walk-in Customer',
            customer_phone: (document.getElementById('customer_phone') && document.getElementById('customer_phone').value) || '',
            customer_email: (document.getElementById('customer_email') && document.getElementById('customer_email').value) || '',
            discount: discount,
            tax_percent: taxPct,
            amount_paid: amountPaidValue
        };
        billDataInput.value = JSON.stringify(billData);
    }
}

// Adjust discount
function adjustDiscount(amount) {
    const input = document.getElementById('discount');
    if (!input) return;
    let value = numberOrZero(input.value);
    value = Math.max(0, value + amount);
    input.value = value.toFixed(2);
    updateTotals();
}

// Adjust tax
function adjustTax(amount) {
    const input = document.getElementById('tax');
    if (!input) return;
    let value = numberOrZero(input.value);
    value = Math.max(0, Math.min(100, value + amount));
    input.value = value.toFixed(2);
    updateTotals();
}

// Form submission guard
function bindForm() {
    const form = document.getElementById('bill_form');
    if (!form) return;
    form.addEventListener('submit', (e) => {
        if (billItems.length === 0) {
            e.preventDefault();
            alert('Please add items to the bill before completing the sale');
            return false;
        }
        const hidden = document.getElementById('bill_data');
        if (!hidden || !hidden.value) {
            e.preventDefault();
            alert('Bill data not ready. Please try again.');
            return false;
        }
        return true;
    });
}

console.log('POS JS ready');
