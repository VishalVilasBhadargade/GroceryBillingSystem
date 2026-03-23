"""
Billing/Bill management views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db import transaction
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from urllib.parse import quote
from apps.core.decorators import login_required_custom, role_required
from apps.customers.models import Customer
from .models import Bill, BillItem, Payment
from apps.products.models import Product
import json
import logging

logger = logging.getLogger(__name__)


def _build_simple_pdf(lines):
    """Build a minimal PDF byte stream with plain text lines."""
    escaped_lines = []
    for line in lines:
        safe = str(line).replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
        escaped_lines.append(safe)

    y = 760
    commands = ["BT", "/F1 11 Tf", "40 800 Td"]
    for i, line in enumerate(escaped_lines):
        if i == 0:
            commands.append(f"({line}) Tj")
        else:
            commands.append(f"40 {y} Td ({line}) Tj")
        y -= 16

    commands.append("ET")
    content_stream = "\n".join(commands).encode('latin-1', errors='replace')

    objects = []
    objects.append(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    objects.append(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")
    objects.append(
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n"
    )
    objects.append(b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")
    objects.append(
        f"5 0 obj\n<< /Length {len(content_stream)} >>\nstream\n".encode('latin-1')
        + content_stream
        + b"\nendstream\nendobj\n"
    )

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objects:
        offsets.append(len(pdf))
        pdf.extend(obj)

    xref_start = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode('latin-1'))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode('latin-1'))

    pdf.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_start}\n%%EOF"
        ).encode('latin-1')
    )
    return bytes(pdf)


def _normalize_phone(phone):
    """Normalize phone numbers by removing spaces, dashes, and extra leading zeros"""
    if not phone:
        return None
    phone_str = str(phone).strip().replace(' ', '').replace('-', '').replace('+', '')
    # Remove leading 0 from Indian numbers
    if phone_str.startswith('0'):
        phone_str = phone_str[1:]
    return phone_str if phone_str else None


def _get_customer_for_bill(customer_phone, customer_email, customer_name):
    # Try matching by phone (with normalization)
    if customer_phone:
        customer_phone_norm = _normalize_phone(customer_phone)
        if customer_phone_norm:
            # Search across all customers with normalized phone comparison
            for customer in Customer.objects.all():
                if _normalize_phone(customer.phone) == customer_phone_norm:
                    return customer

    # Try matching by email
    if customer_email:
        customer = Customer.objects.filter(email__iexact=customer_email).first()
        if customer:
            return customer

    # Try matching by name
    if customer_name:
        return Customer.objects.filter(customer_name__iexact=customer_name).first()

    return None


def _apply_customer_loyalty(customer, amount_paid):
    if not customer:
        return

    amount = Decimal(str(amount_paid or 0))
    if amount <= 0:
        return

    customer.total_spent = (customer.total_spent or Decimal('0')) + amount
    customer.loyalty_points = int(customer.total_spent // Decimal('100'))
    customer.save(update_fields=['total_spent', 'loyalty_points', 'updated_at'])


def _build_whatsapp_receipt_url(bill):
    """Build a WhatsApp deep link with bill summary and product list text."""
    phone = _normalize_phone(bill.customer_phone)
    if not phone:
        return None

    # Keep only digits and normalize to India country code format for wa.me
    phone_digits = ''.join(ch for ch in phone if ch.isdigit())
    if len(phone_digits) == 10:
        phone_digits = f"91{phone_digits}"

    customer_name = bill.customer_name or 'Customer'
    item_lines = []
    for item in bill.items.all():
        item_lines.append(f"- {item.product_name} x {item.quantity} = रु. {item.total_price:.2f}")

    product_list_text = "\n".join(item_lines) if item_lines else "- वस्तू उपलब्ध नाहीत"

    bill_created_at_local = timezone.localtime(bill.created_at)

    message = (
        f"नमस्कार {customer_name},\n"
        f"श्री साईकृपा किराणा कडून आपली बिल पावती:\n"
        f"बिल क्रमांक: {bill.id}\n"
        f"दिनांक: {bill_created_at_local.strftime('%d/%m/%Y %H:%M')}\n"
        f"वस्तूंची यादी:\n{product_list_text}\n"
        f"एकूण रक्कम: रु. {bill.total:.2f}\n"
        f"भरलेली रक्कम: रु. {bill.amount_paid:.2f}\n"
        f"बाकी रक्कम: रु. {bill.remaining_amount:.2f}\n"
        f"\n"
        f"मदतीसाठी WhatsApp: +91 9673311365"
    )
    return f"https://wa.me/{phone_digits}?text={quote(message)}"


@login_required_custom
@role_required('CASHIER', 'MANAGER', 'ADMIN')
def create_bill(request):
    """Create new bill - POS interface"""
    if request.method == 'POST':
        try:
            bill_data = json.loads(request.POST.get('bill_data', '{}'))
            items = bill_data.get('items') or []

            if not items:
                messages.error(request, 'No items in the bill')
                return redirect('billing:create')

            discount = float(bill_data.get('discount') or 0)
            tax_percent = float(bill_data.get('tax_percent') or 0)

            with transaction.atomic():
                subtotal = 0
                line_items = []

                for item in items:
                    product_id = item.get('product_id')
                    quantity = int(item.get('quantity') or 0)

                    if not product_id or quantity <= 0:
                        raise ValueError('Invalid product or quantity in bill items')

                    product = get_object_or_404(Product, pk=product_id)

                    if quantity > product.quantity_on_hand:
                        messages.error(request, f'Insufficient stock for {product.product_name}. Available: {product.quantity_on_hand}')
                        raise ValueError('Insufficient stock')

                    unit_price = float(product.selling_price)
                    line_total = unit_price * quantity
                    subtotal += line_total

                    line_items.append({
                        'product_name': product.product_name,
                        'quantity': quantity,
                        'unit_price': unit_price,
                        'total_price': line_total,
                        'product': product,
                    })

                subtotal_after_discount = max(subtotal - discount, 0)
                tax_amount = (subtotal_after_discount * tax_percent) / 100
                total = subtotal_after_discount + tax_amount

                # Handle partial payment
                amount_paid_value = bill_data.get('amount_paid')
                if amount_paid_value is None or amount_paid_value == '':
                    # If no amount specified, assume full payment
                    amount_paid = total
                else:
                    amount_paid = float(amount_paid_value)
                    # Validate amount_paid
                    if amount_paid < 0:
                        amount_paid = 0
                    elif amount_paid > total:
                        amount_paid = total
                
                remaining_amount = max(0, total - amount_paid)
                
                # Determine status based on payment
                if remaining_amount == 0:
                    status = 'PAID'
                elif amount_paid > 0:
                    status = 'PARTIAL'
                else:
                    status = 'PENDING'

                bill = Bill.objects.create(
                    user=request.user,
                    customer_name=bill_data.get('customer_name', 'Walk-in Customer'),
                    customer_phone=bill_data.get('customer_phone', ''),
                    customer_email=bill_data.get('customer_email', ''),
                    subtotal=subtotal,
                    tax=tax_amount,
                    discount=discount,
                    total=total,
                    amount_paid=amount_paid,
                    remaining_amount=remaining_amount,
                    status=status
                )

                for line in line_items:
                    BillItem.objects.create(
                        bill=bill,
                        product_name=line['product_name'],
                        quantity=line['quantity'],
                        unit_price=line['unit_price'],
                        total_price=line['total_price']
                    )
                    # Deduct stock
                    line['product'].quantity_on_hand -= line['quantity']
                    line['product'].save()

                customer = _get_customer_for_bill(
                    bill.customer_phone,
                    bill.customer_email,
                    bill.customer_name
                )
                _apply_customer_loyalty(customer, amount_paid)

            messages.success(request, f'Bill #{bill.id} created successfully')
            return redirect('billing:detail', bill_id=bill.id)
        except json.JSONDecodeError as e:
            messages.error(request, f'Invalid bill data: {str(e)}')
        except Exception as e:
            logger.exception("Failed to create bill")
            if 'Insufficient stock' not in str(e):
                messages.error(request, f'Failed to create bill: {str(e)}')
            return redirect('billing:create')
    
    # Get products for autocomplete
    products = Product.objects.all()[:100]
    products_list = []
    for product in products:
        products_list.append({
            'id': product.id,
            'product_name': product.product_name,
            'sku': product.sku,
            'barcode': product.barcode if hasattr(product, 'barcode') else product.sku,
            'selling_price': float(product.selling_price),
            'quantity_on_hand': product.quantity_on_hand,
        })
    
    context = {
        'products': json.dumps(products_list),
    }
    
    return render(request, 'billing/create.html', context)


@login_required_custom
def test_pos(request):
    """Test page for POS JavaScript"""
    # Get products for testing
    products = Product.objects.all()[:100]
    products_list = []
    for product in products:
        products_list.append({
            'id': product.id,
            'product_name': product.product_name,
            'sku': product.sku,
            'barcode': product.barcode if hasattr(product, 'barcode') else product.sku,
            'selling_price': float(product.selling_price),
            'quantity_on_hand': product.quantity_on_hand,
        })
    
    context = {
        'products': json.dumps(products_list),
    }
    
    return render(request, 'billing/test_pos.html', context)


@login_required_custom
def bill_list(request):
    """List bills"""
    bills = Bill.objects.all()
    
    # Pagination
    paginator = Paginator(bills, 10)
    page = request.GET.get('page', 1)
    bills_page = paginator.get_page(page)
    
    context = {
        'bills': bills_page,
        'current_page': page,
        'total_pages': paginator.num_pages,
    }
    
    return render(request, 'billing/list.html', context)


@login_required_custom
def bill_detail(request, bill_id):
    """View bill details"""
    bill = get_object_or_404(Bill, pk=bill_id)
    context = {
        'bill': bill,
        'whatsapp_receipt_url': _build_whatsapp_receipt_url(bill),
    }
    return render(request, 'billing/detail.html', context)


@login_required_custom
def print_receipt(request, bill_id):
    """Print bill receipt in thermal printer format"""
    bill = get_object_or_404(Bill, pk=bill_id)
    context = {
        'bill': bill,
        'whatsapp_receipt_url': _build_whatsapp_receipt_url(bill),
    }
    return render(request, 'billing/receipt.html', context)


@login_required_custom
def print_receipt_pdf(request, bill_id):
    """Return printable PDF receipt for a bill."""
    bill = get_object_or_404(Bill, pk=bill_id)

    bill_created_at_local = timezone.localtime(bill.created_at)

    lines = [
        "Shri Saikripa Kirana - Receipt",
        f"Bill #: {bill.id}",
        f"Date: {bill_created_at_local.strftime('%d/%m/%Y %H:%M')}",
        f"Customer: {bill.customer_name or 'Walk-in Customer'}",
        "----------------------------------------",
    ]

    for item in bill.items.all():
        lines.append(f"{item.product_name} x {item.quantity} = Rs. {item.total_price:.2f}")

    lines.extend([
        "----------------------------------------",
        f"Subtotal: Rs. {bill.subtotal:.2f}",
        f"Discount: Rs. {bill.discount:.2f}",
        f"Tax: Rs. {bill.tax:.2f}",
        f"Total: Rs. {bill.total:.2f}",
        f"Paid: Rs. {bill.amount_paid:.2f}",
        f"Balance: Rs. {bill.remaining_amount:.2f}",
        f"Status: {bill.status}",
        "----------------------------------------",
        "WhatsApp Support: +91 9673311365",
    ])

    pdf_bytes = _build_simple_pdf(lines)
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="bill_{bill.id}_receipt.pdf"'
    return response


@login_required_custom
@role_required('MANAGER', 'ADMIN')
def void_bill(request, bill_id):
    """Void a bill"""
    bill = get_object_or_404(Bill, pk=bill_id)
    bill.status = 'VOID'
    bill.save()
    messages.success(request, f'Bill #{bill_id} voided successfully')
    return redirect('billing:detail', bill_id=bill_id)


@login_required_custom
@role_required('MANAGER', 'ADMIN')
def edit_bill(request, bill_id):
    """Edit bill - modify time, discount, tax, and item prices"""
    bill = get_object_or_404(Bill, pk=bill_id)
    
    if request.method == 'POST':
        try:
            # Update bill details
            bill.customer_name = request.POST.get('customer_name', bill.customer_name).strip()
            bill.customer_phone = request.POST.get('customer_phone', bill.customer_phone).strip()
            bill.customer_email = request.POST.get('customer_email', bill.customer_email).strip()
            
            # Update time
            created_at_str = request.POST.get('created_at', '').strip()
            if created_at_str:
                from datetime import datetime
                try:
                    bill.created_at = datetime.fromisoformat(created_at_str)
                except ValueError:
                    pass
            
            # Update discount and tax
            try:
                bill.discount = float(request.POST.get('discount', 0) or 0)
            except (ValueError, TypeError):
                bill.discount = 0
                
            try:
                tax_percent = float(request.POST.get('tax_percent', 0) or 0)
            except (ValueError, TypeError):
                tax_percent = 0
            
            # Update item prices - recalculate subtotal from items
            subtotal = 0
            for item in bill.items.all():
                item_id = item.id
                try:
                    quantity_val = request.POST.get(f'quantity_{item_id}', '')
                    unit_price_val = request.POST.get(f'unit_price_{item_id}', '')
                    
                    if quantity_val:
                        item.quantity = int(quantity_val)
                    if unit_price_val:
                        item.unit_price = float(unit_price_val)
                    
                    item.total_price = float(item.quantity) * float(item.unit_price)
                    item.save()
                    
                    subtotal += item.total_price
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error updating item {item_id}: {str(e)}")
                    continue
            
            # Recalculate totals
            bill.subtotal = subtotal
            subtotal_after_discount = max(subtotal - bill.discount, 0)
            bill.tax = (subtotal_after_discount * tax_percent) / 100
            bill.total = subtotal_after_discount + bill.tax
            
            # Update remaining amount based on new total
            bill.remaining_amount = max(bill.total - bill.amount_paid, 0)
            
            # Update status based on remaining amount
            if bill.remaining_amount == 0:
                bill.status = 'PAID'
            elif bill.amount_paid > 0:
                bill.status = 'PARTIAL'
            else:
                bill.status = 'PENDING'
            
            bill.save()
            
            messages.success(request, f'Bill #{bill_id} updated successfully')
            return redirect('billing:detail', bill_id=bill_id)
        except Exception as e:
            logger.exception("Failed to edit bill")
            messages.error(request, f'Failed to edit bill: {str(e)}')
            return redirect('billing:edit', bill_id=bill_id)
    
    context = {'bill': bill}
    return render(request, 'billing/edit.html', context)


@login_required_custom
@role_required('CASHIER', 'MANAGER', 'ACCOUNTANT', 'ADMIN')
def record_payment(request, bill_id):
    """Record payment for a bill"""
    bill = get_object_or_404(Bill, pk=bill_id)
    
    if request.method == 'POST':
        try:
            # Get current remaining amount
            current_remaining = Decimal(str(bill.remaining_amount or 0)).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )

            if current_remaining <= 0:
                messages.info(request, 'This bill is already fully paid')
                return redirect('billing:detail', bill_id=bill_id)

            is_direct_full_payment = request.POST.get('direct_pay_full') == '1'

            if is_direct_full_payment:
                # One-click full settlement for pending/partial bills.
                amount_paid_now = current_remaining
            else:
                # Use Decimal for precise financial calculations
                amount_paid_now = Decimal(str(request.POST.get('amount_paid', 0)))

                if amount_paid_now <= 0:
                    messages.error(request, 'Payment amount must be greater than 0')
                    return redirect('billing:detail', bill_id=bill_id)

                # Round to 2 decimal places
                amount_paid_now = amount_paid_now.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            # If payment is close to or equals remaining amount, pay exactly the remaining
            if abs(amount_paid_now - current_remaining) < Decimal('0.01'):
                amount_paid_now = current_remaining
            
            # Check if payment exceeds remaining amount
            if amount_paid_now > current_remaining:
                messages.error(request, f'Payment amount (₹{amount_paid_now:.2f}) exceeds remaining amount (₹{current_remaining:.2f})')
                return redirect('billing:detail', bill_id=bill_id)
            
            # Create payment transaction record
            payment_method = request.POST.get('payment_method', 'CASH')
            reference_number = request.POST.get('reference_number', '').strip()
            notes = request.POST.get('notes', '').strip()
            
            Payment.objects.create(
                bill=bill,
                amount=amount_paid_now,
                payment_method=payment_method,
                reference_number=reference_number if reference_number else None,
                notes=notes if notes else None,
                recorded_by=request.user
            )
            
            # Update bill payment information using Decimal arithmetic
            bill.amount_paid = Decimal(str(bill.amount_paid)) + amount_paid_now
            # Cap to total to prevent tiny over/under differences
            if bill.amount_paid > bill.total:
                bill.amount_paid = bill.total
            
            # The save() method will automatically recalculate remaining_amount and status
            bill.save()

            customer = _get_customer_for_bill(
                bill.customer_phone,
                bill.customer_email,
                bill.customer_name
            )
            _apply_customer_loyalty(customer, amount_paid_now)
            
            messages.success(request, f'Payment of ₹{amount_paid_now:.2f} recorded successfully')
            return redirect('billing:detail', bill_id=bill_id)
        except (ValueError, TypeError, InvalidOperation) as e:
            messages.error(request, f'Invalid payment amount: {str(e)}')
            return redirect('billing:detail', bill_id=bill_id)
    
    return redirect('billing:detail', bill_id=bill_id)


@login_required_custom
@role_required('MANAGER', 'ADMIN')
def delete_bill(request, bill_id):
    """Delete a bill"""
    bill = get_object_or_404(Bill, pk=bill_id)
    bill_id_display = bill.id
    bill.delete()
    messages.success(request, f'Bill #{bill_id_display} deleted successfully')
    return redirect('billing:list')
