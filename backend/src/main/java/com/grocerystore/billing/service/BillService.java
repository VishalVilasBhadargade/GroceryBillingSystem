package com.grocerystore.billing.service;

import com.grocerystore.billing.dto.BillDTO;
import com.grocerystore.billing.dto.CreateBillDTO;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Bill Service Interface
 * Business logic for Bill/Transaction operations
 */
public interface BillService {

    /**
     * Create a new bill (checkout)
     */
    BillDTO createBill(CreateBillDTO createBillDTO, Integer cashierId);

    /**
     * Get bill by ID
     */
    BillDTO getBillById(Integer billId);

    /**
     * Get bill by bill number
     */
    BillDTO getBillByNumber(String billNumber);

    /**
     * Get all bills with pagination
     */
    Page<BillDTO> getAllBills(Pageable pageable);

    /**
     * Get bills for a date range
     */
    Page<BillDTO> getBillsByDateRange(LocalDateTime startDate, LocalDateTime endDate, Pageable pageable);

    /**
     * Get bills by customer
     */
    Page<BillDTO> getBillsByCustomer(Integer customerId, Pageable pageable);

    /**
     * Get bills by cashier
     */
    Page<BillDTO> getBillsByCashier(Integer cashierId, Pageable pageable);

    /**
     * Get bills by status
     */
    Page<BillDTO> getBillsByStatus(String status, Pageable pageable);

    /**
     * Void a bill
     */
    BillDTO voidBill(Integer billId, String reason, Integer userId);

    /**
     * Generate receipt for bill
     */
    String generateReceipt(Integer billId);

    /**
     * Get daily sales summary
     */
    java.util.Map<String, Object> getDailySalesSummary(java.time.LocalDate date);
}
