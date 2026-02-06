package com.grocerystore.billing.service;

import java.time.LocalDate;
import java.util.Map;

/**
 * Report Service Interface
 * Handles report generation and analytics
 */
public interface ReportService {
    
    /**
     * Get daily sales report for a specific date
     */
    Map<String, Object> getDailySalesReport(LocalDate date);
    
    /**
     * Get sales report for date range
     */
    Map<String, Object> getSalesReportByDateRange(LocalDate startDate, LocalDate endDate);
    
    /**
     * Get inventory report
     */
    Map<String, Object> getInventoryReport();
    
    /**
     * Get product sales report
     */
    Map<String, Object> getProductSalesReport(LocalDate startDate, LocalDate endDate);
}
