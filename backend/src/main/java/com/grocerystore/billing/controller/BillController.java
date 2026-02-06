package com.grocerystore.billing.controller;

import com.grocerystore.billing.dto.BillDTO;
import com.grocerystore.billing.dto.CreateBillDTO;
import com.grocerystore.billing.response.ApiResponse;
import com.grocerystore.billing.service.BillService;
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
 * Bill Controller
 * REST endpoints for billing/transaction operations
 */
@RestController
@RequestMapping("/api/v1/bills")
@RequiredArgsConstructor
@Slf4j
@Validated
public class BillController {

    private final BillService billService;

    /**
     * Create a new bill (checkout)
     */
    @PostMapping
    @PreAuthorize("hasAnyRole('CASHIER', 'MANAGER', 'ADMIN')")
    public ResponseEntity<ApiResponse<BillDTO>> createBill(
            @Valid @RequestBody CreateBillDTO createBillDTO,
            @AuthenticationPrincipal UserPrincipal currentUser) {
        
        log.info("Creating bill for cashier: {}", currentUser.getUserId());
        BillDTO bill = billService.createBill(createBillDTO, currentUser.getUserId());
        
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success(bill, "Bill created successfully"));
    }

    /**
     * Get bill by ID
     */
    @GetMapping("/{billId}")
    @PreAuthorize("hasAnyRole('CASHIER', 'MANAGER', 'ACCOUNTANT')")
    public ResponseEntity<ApiResponse<BillDTO>> getBillById(
            @PathVariable Integer billId) {
        
        log.info("Fetching bill with ID: {}", billId);
        BillDTO bill = billService.getBillById(billId);
        
        return ResponseEntity.ok(ApiResponse.success(bill, "Bill retrieved successfully"));
    }

    /**
     * Get all bills
     */
    @GetMapping
    @PreAuthorize("hasAnyRole('MANAGER', 'ACCOUNTANT')")
    public ResponseEntity<ApiResponse<Page<BillDTO>>> getAllBills(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        
        log.info("Fetching all bills - page: {}, size: {}", page, size);
        Pageable pageable = PageRequest.of(page, size);
        Page<BillDTO> bills = billService.getAllBills(pageable);
        
        return ResponseEntity.ok(ApiResponse.success(bills, "Bills retrieved successfully"));
    }

    /**
     * Void a bill (requires manager approval)
     */
    @PostMapping("/{billId}/void")
    @PreAuthorize("hasAnyRole('MANAGER', 'ADMIN')")
    public ResponseEntity<ApiResponse<BillDTO>> voidBill(
            @PathVariable Integer billId,
            @RequestParam String reason,
            @AuthenticationPrincipal UserPrincipal currentUser) {
        
        log.info("Voiding bill with ID: {}, reason: {}", billId, reason);
        BillDTO bill = billService.voidBill(billId, reason, currentUser.getUserId());
        
        return ResponseEntity.ok(ApiResponse.success(bill, "Bill voided successfully"));
    }

    /**
     * Get receipt for bill
     */
    @GetMapping("/{billId}/receipt")
    @PreAuthorize("hasAnyRole('CASHIER', 'MANAGER')")
    public ResponseEntity<ApiResponse<String>> getReceipt(
            @PathVariable Integer billId) {
        
        log.info("Generating receipt for bill: {}", billId);
        String receipt = billService.generateReceipt(billId);
        
        return ResponseEntity.ok(ApiResponse.success(receipt, "Receipt generated successfully"));
    }

    /**
     * Get daily sales summary
     */
    @GetMapping("/reports/daily-sales")
    @PreAuthorize("hasAnyRole('MANAGER', 'ACCOUNTANT')")
    public ResponseEntity<ApiResponse<java.util.Map<String, Object>>> getDailySalesSummary(
            @RequestParam(required = false) String date) {
        
        java.time.LocalDate reportDate = date != null ? 
                java.time.LocalDate.parse(date) : java.time.LocalDate.now();
        
        log.info("Generating daily sales summary for: {}", reportDate);
        var summary = billService.getDailySalesSummary(reportDate);
        
        return ResponseEntity.ok(ApiResponse.success(summary, "Daily sales summary retrieved"));
    }
}
