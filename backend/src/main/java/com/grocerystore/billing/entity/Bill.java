package com.grocerystore.billing.entity;

import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * Bill Entity
 * Represents transactions/bills
 */
@Entity
@Table(name = "bills", indexes = {
    @Index(name = "idx_bills_number", columnList = "bill_number"),
    @Index(name = "idx_bills_date", columnList = "bill_date"),
    @Index(name = "idx_bills_cashier_id", columnList = "cashier_id"),
    @Index(name = "idx_bills_customer_id", columnList = "customer_id"),
    @Index(name = "idx_bills_status", columnList = "status")
})
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Bill {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer billId;

    @Column(nullable = false, unique = true, length = 50)
    private String billNumber;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "cashier_id", nullable = false)
    private User cashier;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "customer_id")
    private Customer customer;

    @Column(nullable = false)
    private LocalDateTime billDate;

    @Column(nullable = false, precision = 12, scale = 2)
    private BigDecimal subtotal;

    @Column(nullable = false, precision = 12, scale = 2)
    private BigDecimal discountAmount;

    @Column(nullable = false, precision = 12, scale = 2)
    private BigDecimal taxAmount;

    @Column(nullable = false, precision = 12, scale = 2)
    private BigDecimal totalAmount;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private BillStatus status;

    @Column(length = 255)
    private String voidReason;

    @Column(name = "void_date")
    private LocalDateTime voidDate;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "void_by_user_id")
    private User voidByUser;

    @Column(columnDefinition = "TEXT")
    private String notes;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(nullable = false)
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
        billDate = LocalDateTime.now();
        status = BillStatus.COMPLETED;
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    /**
     * Bill Status Enum
     */
    public enum BillStatus {
        COMPLETED,
        VOIDED,
        REFUNDED
    }
}
