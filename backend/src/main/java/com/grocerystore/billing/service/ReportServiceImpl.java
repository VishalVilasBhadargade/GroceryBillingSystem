package com.grocerystore.billing.service;

import com.grocerystore.billing.repository.BillRepository;
import com.grocerystore.billing.repository.ProductRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.HashMap;
import java.util.Map;

/**
 * Report Service Implementation
 * Generates various reports and analytics
 */
@Service
@RequiredArgsConstructor
@Slf4j
@Transactional(readOnly = true)
public class ReportServiceImpl implements ReportService {

    private final BillRepository billRepository;
    private final ProductRepository productRepository;
    private final BillService billService;

    @Override
    public Map<String, Object> getDailySalesReport(LocalDate date) {
        log.info("Generating daily sales report for date: {}", date);
        return billService.getDailySalesSummary(date);
    }

    @Override
    public Map<String, Object> getSalesReportByDateRange(LocalDate startDate, LocalDate endDate) {
        log.info("Generating sales report from {} to {}", startDate, endDate);
        
        Map<String, Object> report = new HashMap<>();
        report.put("startDate", startDate);
        report.put("endDate", endDate);
        report.put("totalBills", billRepository.countCompletedBillsInRange(
            startDate.atStartOfDay(),
            endDate.atTime(23, 59, 59)
        ));
        report.put("totalRevenue", billRepository.sumTotalAmountInRange(
            startDate.atStartOfDay(),
            endDate.atTime(23, 59, 59)
        ));
        
        return report;
    }

    @Override
    public Map<String, Object> getInventoryReport() {
        log.info("Generating inventory report");
        
        Map<String, Object> report = new HashMap<>();
        report.put("totalProducts", productRepository.countByIsActiveTrue());
        report.put("lowStockProducts", productRepository.countByQuantityOnHandLessThan(10));
        report.put("outOfStockProducts", productRepository.countByQuantityOnHandLessThan(1));
        
        return report;
    }

    @Override
    public Map<String, Object> getProductSalesReport(LocalDate startDate, LocalDate endDate) {
        log.info("Generating product sales report from {} to {}", startDate, endDate);
        
        Map<String, Object> report = new HashMap<>();
        report.put("startDate", startDate);
        report.put("endDate", endDate);
        report.put("totalProductsSold", billRepository.countCompletedBillsInRange(
            startDate.atStartOfDay(),
            endDate.atTime(23, 59, 59)
        ));
        
        return report;
    }
}
