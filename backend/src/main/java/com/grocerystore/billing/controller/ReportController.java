package com.grocerystore.billing.controller;

import com.grocerystore.billing.response.ApiResponse;
import com.grocerystore.billing.service.ReportService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.Map;

/**
 * Report Controller
 * REST endpoints for reporting and analytics
 */
@RestController
@RequestMapping("/api/v1/reports")
@RequiredArgsConstructor
@Slf4j
@Validated
public class ReportController {

    private final ReportService reportService;

    /**
     * Get daily sales report
     */
    @GetMapping("/sales/daily")
    @PreAuthorize("hasAnyRole('MANAGER', 'ACCOUNTANT')")
    public ResponseEntity<ApiResponse<Map<String, Object>>> getDailySalesReport(
            @RequestParam LocalDate date) {
        
        log.info("Generating daily sales report for date: {}", date);
        Map<String, Object> report = reportService.getDailySalesReport(date);
        
        return ResponseEntity.ok(ApiResponse.success(report, "Daily sales report generated"));
    }

    /**
     * Get sales report for date range
     */
    @GetMapping("/sales/range")
    @PreAuthorize("hasAnyRole('MANAGER', 'ACCOUNTANT')")
    public ResponseEntity<ApiResponse<Map<String, Object>>> getSalesReportByDateRange(
            @RequestParam LocalDate startDate,
            @RequestParam LocalDate endDate) {
        
        log.info("Generating sales report from {} to {}", startDate, endDate);
        Map<String, Object> report = reportService.getSalesReportByDateRange(startDate, endDate);
        
        return ResponseEntity.ok(ApiResponse.success(report, "Sales report generated"));
    }

    /**
     * Get inventory report
     */
    @GetMapping("/inventory")
    @PreAuthorize("hasAnyRole('INVENTORY_MANAGER', 'MANAGER', 'ADMIN')")
    public ResponseEntity<ApiResponse<Map<String, Object>>> getInventoryReport() {
        
        log.info("Generating inventory report");
        Map<String, Object> report = reportService.getInventoryReport();
        
        return ResponseEntity.ok(ApiResponse.success(report, "Inventory report generated"));
    }

    /**
     * Get product sales report
     */
    @GetMapping("/products")
    @PreAuthorize("hasAnyRole('MANAGER', 'ACCOUNTANT')")
    public ResponseEntity<ApiResponse<Map<String, Object>>> getProductSalesReport(
            @RequestParam LocalDate startDate,
            @RequestParam LocalDate endDate) {
        
        log.info("Generating product sales report from {} to {}", startDate, endDate);
        Map<String, Object> report = reportService.getProductSalesReport(startDate, endDate);
        
        return ResponseEntity.ok(ApiResponse.success(report, "Product sales report generated"));
    }
}
