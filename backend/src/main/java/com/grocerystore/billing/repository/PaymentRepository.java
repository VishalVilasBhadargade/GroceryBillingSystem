package com.grocerystore.billing.repository;

import com.grocerystore.billing.entity.Payment;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.Optional;

/**
 * Payment Repository
 * Data access layer for Payment entity
 */
@Repository
public interface PaymentRepository extends JpaRepository<Payment, Integer> {

    @Query("SELECT p FROM Payment p WHERE p.bill.billId = :billId")
    Optional<Payment> findByBillId(@Param("billId") Integer billId);

    Optional<Payment> findByReferenceNumber(String referenceNumber);

    Page<Payment> findByPaymentMethod(Payment.PaymentMethod paymentMethod, Pageable pageable);

    Page<Payment> findByStatus(Payment.PaymentStatus status, Pageable pageable);

    @Query("SELECT p FROM Payment p WHERE p.createdAt BETWEEN :startDate AND :endDate " +
           "AND p.status = 'APPROVED'")
    Page<Payment> findApprovedPaymentsByDateRange(
            @Param("startDate") LocalDateTime startDate,
            @Param("endDate") LocalDateTime endDate,
            Pageable pageable);

    long countByStatus(Payment.PaymentStatus status);
}
