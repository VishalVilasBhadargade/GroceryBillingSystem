package com.grocerystore.billing.service;

import com.grocerystore.billing.dto.PaymentDTO;
import com.grocerystore.billing.dto.ProcessPaymentDTO;
import com.grocerystore.billing.entity.Bill;
import com.grocerystore.billing.entity.Payment;
import com.grocerystore.billing.entity.PaymentMethod;
import com.grocerystore.billing.entity.PaymentStatus;
import com.grocerystore.billing.exception.ResourceNotFoundException;
import com.grocerystore.billing.repository.BillRepository;
import com.grocerystore.billing.repository.PaymentRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.modelmapper.ModelMapper;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

/**
 * Payment Service Implementation
 * Manages payment processing and refunds
 */
@Service
@RequiredArgsConstructor
@Slf4j
@Transactional
public class PaymentServiceImpl implements PaymentService {

    private final PaymentRepository paymentRepository;
    private final BillRepository billRepository;
    private final ModelMapper modelMapper;

    @Override
    public PaymentDTO processPayment(ProcessPaymentDTO processPaymentDTO) {
        log.info("Processing payment for bill: {}", processPaymentDTO.getBillId());
        
        Bill bill = billRepository.findById(processPaymentDTO.getBillId())
                .orElseThrow(() -> new ResourceNotFoundException("Bill not found with ID: " + processPaymentDTO.getBillId()));
        
        // Validate payment amount
        java.math.BigDecimal paymentAmount = java.math.BigDecimal.valueOf(processPaymentDTO.getAmount());
        if (paymentAmount.compareTo(bill.getTotalAmount()) != 0) {
            throw new IllegalArgumentException("Payment amount does not match bill total");
        }
        
        Payment payment = new Payment();
        payment.setBill(bill);
        payment.setAmount(paymentAmount);
        payment.setPaymentMethod(Payment.PaymentMethod.valueOf(processPaymentDTO.getPaymentMethod()));
        payment.setStatus(Payment.PaymentStatus.APPROVED);
        payment.setReferenceNumber(generateTransactionId());
        
        Payment savedPayment = paymentRepository.save(payment);
        log.info("Payment processed successfully with transaction ID: {}", savedPayment.getReferenceNumber());
        
        return modelMapper.map(savedPayment, PaymentDTO.class);
    }

    @Override
    @Transactional(readOnly = true)
    public PaymentDTO getPaymentById(Integer paymentId) {
        log.info("Fetching payment with ID: {}", paymentId);
        
        Payment payment = paymentRepository.findById(paymentId)
                .orElseThrow(() -> new ResourceNotFoundException("Payment not found with ID: " + paymentId));
        
        return modelMapper.map(payment, PaymentDTO.class);
    }

    @Override
    @Transactional(readOnly = true)
    public PaymentDTO getPaymentByBillId(Integer billId) {
        log.info("Fetching payment for bill: {}", billId);
        
        Payment payment = paymentRepository.findByBillId(billId)
                .orElseThrow(() -> new ResourceNotFoundException("Payment not found for bill ID: " + billId));
        
        return modelMapper.map(payment, PaymentDTO.class);
    }

    @Override
    @Transactional(readOnly = true)
    public Page<PaymentDTO> getAllPayments(Pageable pageable) {
        log.info("Fetching all payments with pagination");
        
        return paymentRepository.findAll(pageable)
                .map(payment -> modelMapper.map(payment, PaymentDTO.class));
    }

    @Override
    public PaymentDTO refundPayment(Integer paymentId, String reason, Integer refundedBy) {
        log.info("Refunding payment with ID: {}, reason: {}", paymentId, reason);
        
        Payment payment = paymentRepository.findById(paymentId)
                .orElseThrow(() -> new ResourceNotFoundException("Payment not found with ID: " + paymentId));
        
        if (payment.getStatus() == Payment.PaymentStatus.DECLINED) {
            throw new IllegalStateException("Payment cannot be refunded");
        }
        
        payment.setStatus(Payment.PaymentStatus.DECLINED);
        
        Payment refundedPayment = paymentRepository.save(payment);
        log.info("Payment refunded successfully");
        
        return modelMapper.map(refundedPayment, PaymentDTO.class);
    }
    
    @Override
    @Transactional(readOnly = true)
    public Page<PaymentDTO> getPaymentsByStatus(String status, org.springframework.data.domain.Pageable pageable) {
        log.info("Fetching payments with status: {}", status);
        Payment.PaymentStatus paymentStatus = Payment.PaymentStatus.valueOf(status.toUpperCase());
        return paymentRepository.findByStatus(paymentStatus, pageable)
                .map(payment -> modelMapper.map(payment, PaymentDTO.class));
    }
    
    @Override
    @Transactional(readOnly = true)
    public boolean validatePaymentAmount(Integer billId, java.math.BigDecimal amount) {
        Bill bill = billRepository.findById(billId)
                .orElseThrow(() -> new ResourceNotFoundException("Bill not found"));
        return bill.getTotalAmount().compareTo(amount) == 0;
    }
    
    @Override
    @Transactional(readOnly = true)
    public PaymentDTO getPaymentByReference(String reference) {
        Payment payment = paymentRepository.findByReferenceNumber(reference)
                .orElseThrow(() -> new ResourceNotFoundException("Payment not found with reference: " + reference));
        return modelMapper.map(payment, PaymentDTO.class);
    }
    
    @Override
    @Transactional(readOnly = true)
    public Page<PaymentDTO> getPaymentsByMethod(String method, org.springframework.data.domain.Pageable pageable) {
        log.info("Fetching payments with method: {}", method);
        Payment.PaymentMethod paymentMethod = Payment.PaymentMethod.valueOf(method.toUpperCase());
        return paymentRepository.findByPaymentMethod(paymentMethod, pageable)
                .map(payment -> modelMapper.map(payment, PaymentDTO.class));
    }

    /**
     * Generate a unique transaction ID
     */
    private String generateTransactionId() {
        return "TXN_" + System.currentTimeMillis();
    }
}
