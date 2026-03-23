/* POS Interface JavaScript - simplified, defensive, and fully logged */

let billItems = [];
let autocompleteSelectedIndex = -1;
let autocompleteItems = [];

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
    console.log('Initializing keyboard shortcuts...');
    
    bindSearch();
    bindTotals();
    bindForm();
    bindKeyboardShortcuts();
    renderItems();
    
    // Show keyboard shortcuts hint
    showKeyboardHints();
    
    console.log('✅ POS fully initialized with keyboard support');
    console.log('💡 Available shortcuts: F1 (Help), F2 (Search), F4 (Clear), F9 (Complete)');
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
            autocompleteSelectedIndex = -1;
            return;
        }

        const matches = products.filter(p =>
            (p.product_name || '').toLowerCase().includes(q) ||
            (p.barcode || '').toLowerCase().includes(q) ||
            (p.sku || '').toLowerCase().includes(q)
        );

        autocompleteItems = matches;
        autocompleteSelectedIndex = -1;

        if (matches.length === 0) {
            list.innerHTML = '<div class="autocomplete-item">No products found</div>';
            list.style.display = 'block';
            return;
        }

        renderAutocompleteList(matches, list);
        list.style.display = 'block';
    });

    // Keyboard navigation for autocomplete
    input.addEventListener('keydown', (e) => {
        const list = document.getElementById('autocomplete_list');
        if (!list || list.style.display === 'none') {
            // If autocomplete is not showing and Enter is pressed, try barcode exact match
            if (e.key === 'Enter') {
                e.preventDefault();
                const barcode = input.value.trim();
                const exactMatch = products.find(p => 
                    (p.barcode || '').toLowerCase() === barcode.toLowerCase() ||
                    (p.sku || '').toLowerCase() === barcode.toLowerCase()
                );
                if (exactMatch) {
                    addItem(exactMatch.id, exactMatch.product_name, exactMatch.selling_price, exactMatch.quantity_on_hand);
                    input.value = '';
                    list.style.display = 'none';
                }
            }
            return;
        }

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            autocompleteSelectedIndex = Math.min(autocompleteSelectedIndex + 1, autocompleteItems.length - 1);
            highlightAutocompleteItem();
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            autocompleteSelectedIndex = Math.max(autocompleteSelectedIndex - 1, -1);
            highlightAutocompleteItem();
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (autocompleteSelectedIndex >= 0 && autocompleteSelectedIndex < autocompleteItems.length) {
                const p = autocompleteItems[autocompleteSelectedIndex];
                addItem(p.id, p.product_name, p.selling_price, p.quantity_on_hand);
            } else if (autocompleteItems.length > 0) {
                // Select first item if none selected
                const p = autocompleteItems[0];
                addItem(p.id, p.product_name, p.selling_price, p.quantity_on_hand);
            }
            list.style.display = 'none';
            input.value = '';
            autocompleteSelectedIndex = -1;
        } else if (e.key === 'Escape') {
            e.preventDefault();
            list.style.display = 'none';
            autocompleteSelectedIndex = -1;
        }
    });

    document.addEventListener('click', (e) => {
        if (!list.contains(e.target) && e.target !== input) {
            list.style.display = 'none';
            autocompleteSelectedIndex = -1;
        }
    });
}

function renderAutocompleteList(matches, listEl) {
    listEl.innerHTML = matches.map((p, idx) => `
        <div class="autocomplete-item ${idx === autocompleteSelectedIndex ? 'selected' : ''}" data-id="${p.id}" data-name="${escapeHtml(p.product_name)}" data-price="${p.selling_price}" data-stock="${p.quantity_on_hand}" data-idx="${idx}">
            <strong>${escapeHtml(p.product_name)}</strong><br>
            <small>${formatINR(p.selling_price)} | Stock: ${p.quantity_on_hand}</small>
        </div>
    `).join('');

    listEl.querySelectorAll('.autocomplete-item').forEach(el => {
        el.addEventListener('click', () => {
            const id = parseInt(el.dataset.id, 10);
            const name = el.dataset.name;
            const price = numberOrZero(el.dataset.price);
            const stock = parseInt(el.dataset.stock, 10) || 0;
            addItem(id, name, price, stock);
            listEl.style.display = 'none';
            document.getElementById('product_search').value = '';
            autocompleteSelectedIndex = -1;
        });
        
        el.addEventListener('mouseenter', () => {
            autocompleteSelectedIndex = parseInt(el.dataset.idx, 10);
            highlightAutocompleteItem();
        });
    });
}

function highlightAutocompleteItem() {
    const listEl = document.getElementById('autocomplete_list');
    if (!listEl) return;
    
    const items = listEl.querySelectorAll('.autocomplete-item');
    items.forEach((item, idx) => {
        if (idx === autocompleteSelectedIndex) {
            item.classList.add('selected');
            item.scrollIntoView({ block: 'nearest' });
        } else {
            item.classList.remove('selected');
        }
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

    // Allow keyboard shortcuts in input fields
    const allInputs = container.querySelectorAll('[data-role="qty"], [data-role="price"]');
    allInputs.forEach(input => {
        input.addEventListener('keydown', (e) => {
            // Allow F-keys and Ctrl shortcuts even in input fields
            if (e.key.startsWith('F') || (e.ctrlKey && !e.shiftKey && !e.altKey)) {
                // Let these events bubble up to trigger keyboard shortcuts
                // Don't prevent default for these keys
                console.log('Shortcut in input field:', e.key);
            }
        });
    });

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

// Keyboard shortcuts  
function bindKeyboardShortcuts() {
    console.log('Keyboard shortcuts initialized');
    
    // Use capture phase to intercept keyboard events BEFORE input field handlers
    // This ensures shortcuts work even when typing in quantity/price fields
    document.addEventListener('keydown', handleGlobalKeyboardShortcut, true);
    
    console.log('Keyboard shortcuts ready. Press F1 for help.');
}

function handleGlobalKeyboardShortcut(e) {
    // Get active element
    const activeEl = document.activeElement;
    const isInputField = activeEl.tagName === 'INPUT' || activeEl.tagName === 'TEXTAREA';
    
    // Debug logging for F-keys and Ctrl shortcuts
    if (e.key.startsWith('F') || e.ctrlKey) {
        console.log('Shortcut:', e.key, 'Ctrl:', e.ctrlKey, 'Active elem:', activeEl.id || activeEl.className);
    }
    
    // F9 - Complete Sale (works everywhere, even in input fields)
    if (e.key === 'F9') {
        e.preventDefault();
        e.stopPropagation();
        console.log('✅ F9 pressed - Complete Sale');
        const form = document.getElementById('bill_form');
        if (form && billItems.length > 0) {
            form.submit();
        } else {
            alert('Add items to complete the sale');
        }
        return;
    }
    
    // F4 - Clear Bill (works everywhere, even in input fields)
    if (e.key === 'F4') {
        e.preventDefault();
        e.stopPropagation();
        console.log('✅ F4 pressed - Clear Bill');
        clearBill();
        return;
    }
    
    // F2 - Focus on Product Search (works everywhere, even in input fields)
    if (e.key === 'F2') {
        e.preventDefault();
        e.stopPropagation();
        console.log('✅ F2 pressed - Focus Search');
        const searchInput = document.getElementById('product_search');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
        return;
    }
    
    // Ctrl+D - Focus on Discount (works everywhere)
    if (e.ctrlKey && e.key === 'd') {
        e.preventDefault();
        e.stopPropagation();
        console.log('✅ Ctrl+D pressed - Focus Discount');
        const discountInput = document.getElementById('discount');
        if (discountInput) {
            discountInput.focus();
            discountInput.select();
        }
        return;
    }
    
    // Ctrl+T - Focus on Tax (works everywhere)
    if (e.ctrlKey && e.key === 't') {
        e.preventDefault();
        e.stopPropagation();
        console.log('✅ Ctrl+T pressed - Focus Tax');
        const taxInput = document.getElementById('tax');
        if (taxInput) {
            taxInput.focus();
            taxInput.select();
        }
        return;
    }
    
    // Ctrl+P - Focus on Amount Paid (may be blocked by browser)
    if (e.ctrlKey && e.key === 'p') {
        e.preventDefault();
        e.stopPropagation();
        console.log('✅ Ctrl+P pressed - Focus Amount Paid');
        const paidInput = document.getElementById('amount_paid');
        if (paidInput) {
            paidInput.focus();
            paidInput.select();
        }
        return;
    }
    
    // Ctrl+N - Focus on Customer Name (may be blocked by browser)
    if (e.ctrlKey && e.key === 'n') {
        e.preventDefault();
        e.stopPropagation();
        console.log('✅ Ctrl+N pressed - Focus Customer Name');
        const nameInput = document.getElementById('customer_name');
        if (nameInput) {
            nameInput.focus();
            nameInput.select();
        }
        return;
    }
    
    // Ctrl+S - Submit (Complete Sale) (may be blocked by browser)
    if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        e.stopPropagation();
        console.log('✅ Ctrl+S pressed - Submit Bill');
        const form = document.getElementById('bill_form');
        if (form && billItems.length > 0) {
            form.submit();
        }
        return;
    }
    
    // ESC - Clear search or blur current field
    if (e.key === 'Escape') {
        const searchInput = document.getElementById('product_search');
        const autocompleteList = document.getElementById('autocomplete_list');
        
        if (autocompleteList && autocompleteList.style.display !== 'none') {
            e.preventDefault();
            e.stopPropagation();
            autocompleteList.style.display = 'none';
            console.log('✅ ESC pressed - Closed autocomplete');
        } else if (activeEl === searchInput) {
            e.preventDefault();
            searchInput.value = '';
            searchInput.blur();
            console.log('✅ ESC pressed - Cleared search');
        } else if (isInputField) {
            e.preventDefault();
            activeEl.blur();
            console.log('✅ ESC pressed - Blurred field');
        }
        return;
    }
    
    // F1 - Show keyboard shortcuts (works everywhere)
    if (e.key === 'F1') {
        e.preventDefault();
        e.stopPropagation();
        console.log('✅ F1 pressed - Show Help');
        showKeyboardHelp();
        return;
    }
}

function showKeyboardHints() {
    // Add a small hint badge on first load
    if (!localStorage.getItem('pos_keyboard_hints_shown')) {
        setTimeout(() => {
            const hint = document.createElement('div');
            hint.id = 'keyboard-hint';
            hint.className = 'alert alert-info alert-dismissible fade show position-fixed';
            hint.style.cssText = 'bottom: 20px; right: 20px; z-index: 9999; max-width: 400px;';
            hint.innerHTML = `
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                <strong><i class="fas fa-keyboard"></i> Keyboard Shortcuts Enabled!</strong><br>
                <small>
                    Press <kbd>F1</kbd> to see all shortcuts<br>
                    Press <kbd>F2</kbd> to search products<br>
                    Press <kbd>F9</kbd> or <kbd>Ctrl+S</kbd> to complete sale
                </small>
            `;
            document.body.appendChild(hint);
            localStorage.setItem('pos_keyboard_hints_shown', 'true');
            
            // Auto-dismiss after 8 seconds
            setTimeout(() => {
                hint.classList.remove('show');
                setTimeout(() => hint.remove(), 500);
            }, 8000);
        }, 1000);
    }
}

function showKeyboardHelp() {
    const helpModal = document.createElement('div');
    helpModal.className = 'modal fade';
    helpModal.id = 'keyboardHelpModal';
    helpModal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header bg-primary text-white">
                    <h5 class="modal-title"><i class="fas fa-keyboard"></i> Keyboard Shortcuts</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h6 class="text-primary"><i class="fas fa-search"></i> Product Search</h6>
                            <table class="table table-sm">
                                <tr>
                                    <td><kbd>F2</kbd></td>
                                    <td>Focus on product search</td>
                                </tr>
                                <tr>
                                    <td><kbd>Tab</kbd> / <kbd>Shift</kbd> + <kbd>Tab</kbd></td>
                                    <td>Navigate search results</td>
                                </tr>
                                <tr>
                                    <td><kbd>Enter</kbd></td>
                                    <td>Select highlighted product</td>
                                </tr>
                                <tr>
                                    <td><kbd>Esc</kbd></td>
                                    <td>Close search results</td>
                                </tr>
                            </table>
                            
                            <h6 class="text-primary mt-3"><i class="fas fa-shopping-cart"></i> Cart Actions</h6>
                            <table class="table table-sm">
                                <tr>
                                    <td><kbd>F4</kbd></td>
                                    <td>Clear all items</td>
                                </tr>
                            </table>
                        </div>
                        
                        <div class="col-md-6">
                            <h6 class="text-primary"><i class="fas fa-dollar-sign"></i> Quick Fields</h6>
                            <table class="table table-sm">
                                <tr>
                                    <td><kbd>Ctrl</kbd> + <kbd>D</kbd></td>
                                    <td>Focus on Discount</td>
                                </tr>
                                <tr>
                                    <td><kbd>Ctrl</kbd> + <kbd>T</kbd></td>
                                    <td>Focus on Tax</td>
                                </tr>
                                <tr>
                                    <td><kbd>Ctrl</kbd> + <kbd>P</kbd></td>
                                    <td>Focus on Amount Paid</td>
                                </tr>
                                <tr>
                                    <td><kbd>Ctrl</kbd> + <kbd>N</kbd></td>
                                    <td>Focus on Customer Name</td>
                                </tr>
                            </table>
                            
                            <h6 class="text-primary mt-3"><i class="fas fa-check-circle"></i> Complete Sale</h6>
                            <table class="table table-sm">
                                <tr>
                                    <td><kbd>F9</kbd></td>
                                    <td>Complete sale</td>
                                </tr>
                                <tr>
                                    <td><kbd>Ctrl</kbd> + <kbd>S</kbd></td>
                                    <td>Complete sale</td>
                                </tr>
                            </table>
                            
                            <h6 class="text-primary mt-3"><i class="fas fa-question-circle"></i> Help</h6>
                            <table class="table table-sm">
                                <tr>
                                    <td><kbd>F1</kbd></td>
                                    <td>Show this help</td>
                                </tr>
                            </table>
                        </div>
                    </div>
                    
                    <div class="alert alert-success mt-3">
                        <i class="fas fa-lightbulb"></i> <strong>Pro Tip:</strong> You can use barcode scanner in the product search field. Just scan and press Enter!
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(helpModal);
    const modal = new bootstrap.Modal(helpModal);
    modal.show();
    
    helpModal.addEventListener('hidden.bs.modal', () => {
        helpModal.remove();
    });
}

console.log('POS JS ready');
console.log('✅ Keyboard shortcuts enabled - Press F1 for help');
