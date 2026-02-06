package com.grocerystore.billing.controller;

import com.grocerystore.billing.dto.PaymentDTO;
import com.grocerystore.billing.dto.ProcessPaymentDTO;
import com.grocerystore.billing.response.ApiResponse;
import com.grocerystore.billing.service.PaymentService;
import com.grocerystore.billing.security.UserPrincipal;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import jakarta.validation.Valid;

/**
 * Payment Controller
 * REST endpoints for payment processing
 */
@RestController
@RequestMapping("/api/v1/payments")
@RequiredArgsConstructor
@Slf4j
@Validated
public class PaymentController {

    private final PaymentService paymentService;

    /**
     * Process a payment
     */
    @PostMapping("/process")
    @PreAuthorize("hasAnyRole('CASHIER', 'MANAGER', 'ADMIN')")
    public ResponseEntity<ApiResponse<PaymentDTO>> processPayment(
            @Valid @RequestBody ProcessPaymentDTO processPaymentDTO) {
        
        log.info("Processing payment for bill: {}", processPaymentDTO.getBillId());
        PaymentDTO payment = paymentService.processPayment(processPaymentDTO);
        
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success(payment, "Payment processed successfully"));
    }

    /**
     * Get payment by ID
     */
    @GetMapping("/{paymentId}")
    @PreAuthorize("hasAnyRole('MANAGER', 'ACCOUNTANT')")
    public ResponseEntity<ApiResponse<PaymentDTO>> getPaymentById(
            @PathVariable Integer paymentId) {
        
        log.info("Fetching payment with ID: {}", paymentId);
        PaymentDTO payment = paymentService.getPaymentById(paymentId);
        
        return ResponseEntity.ok(ApiResponse.success(payment, "Payment retrieved successfully"));
    }

    /**
     * Get payment by bill ID
     */
    @GetMapping("/bill/{billId}")
    @PreAuthorize("hasAnyRole('CASHIER', 'MANAGER')")
    public ResponseEntity<ApiResponse<PaymentDTO>> getPaymentByBillId(
            @PathVariable Integer billId) {
        
        log.info("Fetching payment for bill: {}", billId);
        PaymentDTO payment = paymentService.getPaymentByBillId(billId);
        
        return ResponseEntity.ok(ApiResponse.success(payment, "Payment retrieved successfully"));
    }

    /**
     * Get all payments
     */
    @GetMapping
    @PreAuthorize("hasAnyRole('MANAGER', 'ACCOUNTANT')")
    public ResponseEntity<ApiResponse<Page<PaymentDTO>>> getAllPayments(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        
        log.info("Fetching all payments - page: {}, size: {}", page, size);
        Pageable pageable = PageRequest.of(page, size);
        Page<PaymentDTO> payments = paymentService.getAllPayments(pageable);
        
        return ResponseEntity.ok(ApiResponse.success(payments, "Payments retrieved successfully"));
    }

    /**
     * Refund a payment
     */
    @PostMapping("/{paymentId}/refund")
    @PreAuthorize("hasAnyRole('MANAGER', 'ADMIN')")
    public ResponseEntity<ApiResponse<PaymentDTO>> refundPayment(
            @PathVariable Integer paymentId,
            @RequestParam String reason,
            @AuthenticationPrincipal UserPrincipal currentUser) {
        
        log.info("Refunding payment with ID: {}, reason: {}", paymentId, reason);
        PaymentDTO payment = paymentService.refundPayment(paymentId, reason, currentUser.getUserId());
        
        return ResponseEntity.ok(ApiResponse.success(payment, "Payment refunded successfully"));
    }
}
