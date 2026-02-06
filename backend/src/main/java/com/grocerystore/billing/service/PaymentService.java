package com.grocerystore.billing.service;

import com.grocerystore.billing.dto.PaymentDTO;
import com.grocerystore.billing.dto.ProcessPaymentDTO;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

/**
 * Payment Service Interface
 * Business logic for Payment operations
 */
public interface PaymentService {

    /**
     * Process a payment for a bill
     */
    PaymentDTO processPayment(ProcessPaymentDTO processPaymentDTO);

    /**
     * Get payment by ID
     */
    PaymentDTO getPaymentById(Integer paymentId);

    /**
     * Get payment by bill ID
     */
    PaymentDTO getPaymentByBillId(Integer billId);

    /**
     * Get payment by reference number
     */
    PaymentDTO getPaymentByReference(String referenceNumber);

    /**
     * Get all payments with pagination
     */
    Page<PaymentDTO> getAllPayments(Pageable pageable);

    /**
     * Get payments by payment method
     */
    Page<PaymentDTO> getPaymentsByMethod(String paymentMethod, Pageable pageable);

    /**
     * Get payments by status
     */
    Page<PaymentDTO> getPaymentsByStatus(String status, Pageable pageable);

    /**
     * Process refund
     */
    PaymentDTO refundPayment(Integer paymentId, String reason, Integer userId);

    /**
     * Validate payment amount
     */
    boolean validatePaymentAmount(Integer billId, java.math.BigDecimal amount);
}
