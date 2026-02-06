package com.grocerystore.billing.entity;

import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * Payment Entity
 * Represents payment transactions
 */
@Entity
@Table(name = "payments", indexes = {
    @Index(name = "idx_bill_id", columnList = "bill_id"),
    @Index(name = "idx_customer_id", columnList = "customer_id"),
    @Index(name = "idx_payment_method", columnList = "payment_method"),
    @Index(name = "idx_status", columnList = "status"),
    @Index(name = "idx_reference_number", columnList = "reference_number")
})
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Payment {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer paymentId;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "bill_id", nullable = false, unique = true)
    private Bill bill;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "customer_id")
    private Customer customer;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private PaymentMethod paymentMethod;

    @Column(nullable = false, precision = 12, scale = 2)
    private BigDecimal amount;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private PaymentStatus status;

    @Column(length = 100)
    private String referenceNumber;

    @Column(length = 4)
    private String cardLastFour;

    @Column(length = 20)
    private String cardBrand;

    @Column(columnDefinition = "TEXT")
    private String gatewayResponse;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "processed_at")
    private LocalDateTime processedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        status = PaymentStatus.PENDING;
    }

    /**
     * Payment Method Enum
     */
    public enum PaymentMethod {
        CASH,
        CREDIT_CARD,
        DEBIT_CARD,
        DIGITAL_WALLET,
        CHECK
    }

    /**
     * Payment Status Enum
     */
    public enum PaymentStatus {
        PENDING,
        APPROVED,
        DECLINED,
        FAILED
    }
}
