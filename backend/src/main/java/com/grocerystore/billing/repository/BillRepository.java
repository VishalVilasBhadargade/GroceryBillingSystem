package com.grocerystore.billing.repository;

import com.grocerystore.billing.entity.Bill;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

/**
 * Bill Repository
 * Data access layer for Bill entity
 */
@Repository
public interface BillRepository extends JpaRepository<Bill, Integer> {

    Optional<Bill> findByBillNumber(String billNumber);

    @Query("SELECT b FROM Bill b WHERE b.billDate BETWEEN :startDate AND :endDate " +
           "AND b.status = 'COMPLETED'")
    Page<Bill> findCompletedBillsByDateRange(
            @Param("startDate") LocalDateTime startDate,
            @Param("endDate") LocalDateTime endDate,
            Pageable pageable);

    @Query("SELECT b FROM Bill b WHERE b.customer.customerId = :customerId")
    Page<Bill> findByCustomerId(@Param("customerId") Integer customerId, Pageable pageable);

    Page<Bill> findByCashierUserId(Integer cashierId, Pageable pageable);

    Page<Bill> findByStatus(Bill.BillStatus status, Pageable pageable);

    @Query("SELECT COUNT(b) FROM Bill b WHERE b.billDate BETWEEN :startDate AND :endDate " +
           "AND b.status = 'COMPLETED'")
    long countCompletedBillsInRange(
            @Param("startDate") LocalDateTime startDate,
            @Param("endDate") LocalDateTime endDate);

    @Query("SELECT SUM(b.totalAmount) FROM Bill b WHERE b.billDate BETWEEN :startDate AND :endDate " +
           "AND b.status = 'COMPLETED'")
    Double sumTotalAmountInRange(
            @Param("startDate") LocalDateTime startDate,
            @Param("endDate") LocalDateTime endDate);

    List<Bill> findByStatus(Bill.BillStatus status);
}
