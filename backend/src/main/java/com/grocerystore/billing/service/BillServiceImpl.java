package com.grocerystore.billing.service;

import com.grocerystore.billing.dto.BillDTO;
import com.grocerystore.billing.dto.CreateBillDTO;
import com.grocerystore.billing.dto.BillItemDTO;
import com.grocerystore.billing.entity.*;
import com.grocerystore.billing.exception.ResourceNotFoundException;
import com.grocerystore.billing.exception.InsufficientInventoryException;
import com.grocerystore.billing.repository.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.modelmapper.ModelMapper;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Bill Service Implementation
 * Manages bill creation, retrieval, and void operations
 */
@Service
@RequiredArgsConstructor
@Slf4j
@Transactional
public class BillServiceImpl implements BillService {

    private final BillRepository billRepository;
    private final BillItemRepository billItemRepository;
    private final ProductRepository productRepository;
    private final CustomerRepository customerRepository;
    private final ModelMapper modelMapper;

    @Override
    public BillDTO createBill(CreateBillDTO createBillDTO, Integer userId) {
        log.info("Creating bill for user: {} with {} items", userId, createBillDTO.getItems().size());
        
        Bill bill = new Bill();
        bill.setCashier(new User()); // Will be set from context
        bill.setCustomer(customerRepository.findById(createBillDTO.getCustomerId()).orElse(null));
        bill.setStatus(Bill.BillStatus.COMPLETED);
        bill.setCreatedAt(LocalDateTime.now());
        bill.setUpdatedAt(LocalDateTime.now());
        bill.setBillNumber("BILL-" + System.currentTimeMillis());
        
        BigDecimal totalAmount = BigDecimal.ZERO;
        List<BillItem> billItems = new ArrayList<>();
        
        // Process each bill item
        for (BillItemDTO itemDTO : createBillDTO.getItems()) {
            Product product = productRepository.findById(itemDTO.getProductId())
                    .orElseThrow(() -> new ResourceNotFoundException("Product not found with ID: " + itemDTO.getProductId()));
            
            // Check inventory
            if (product.getQuantityOnHand() < itemDTO.getQuantity()) {
                throw new InsufficientInventoryException(
                    "Insufficient inventory for product: " + product.getName() + 
                    ". Available: " + product.getQuantityOnHand() + ", Requested: " + itemDTO.getQuantity()
                );
            }
            
            BillItem billItem = new BillItem();
            billItem.setProduct(product);
            billItem.setQuantity(itemDTO.getQuantity());
            billItem.setUnitPrice(product.getPrice());
            billItem.setLineTotal(product.getPrice().multiply(new BigDecimal(itemDTO.getQuantity())));
            billItem.setDiscountAmount(BigDecimal.ZERO);
            billItem.setFinalLineTotal(billItem.getLineTotal());
            billItem.setCreatedAt(LocalDateTime.now());
            
            // Deduct from inventory
            product.setQuantityOnHand(product.getQuantityOnHand() - itemDTO.getQuantity());
            productRepository.save(product);
            
            billItems.add(billItem);
            totalAmount = totalAmount.add(billItem.getLineTotal());
        }
        
        bill.setSubtotal(totalAmount);
        bill.setDiscountAmount(BigDecimal.ZERO);
        bill.setTaxAmount(BigDecimal.ZERO);
        bill.setTotalAmount(totalAmount);
        Bill savedBill = billRepository.save(bill);
        
        // Save bill items
        for (BillItem item : billItems) {
            item.setBill(savedBill);
        }
        billItemRepository.saveAll(billItems);
        
        log.info("Bill created successfully with ID: {}", savedBill.getBillId());
        return convertToDTO(savedBill);
    }

    @Override
    @Transactional(readOnly = true)
    public BillDTO getBillById(Integer billId) {
        log.info("Fetching bill with ID: {}", billId);
        
        Bill bill = billRepository.findById(billId)
                .orElseThrow(() -> new ResourceNotFoundException("Bill not found with ID: " + billId));
        
        return convertToDTO(bill);
    }

    @Override
    @Transactional(readOnly = true)
    public Page<BillDTO> getAllBills(Pageable pageable) {
        log.info("Fetching all bills with pagination");
        
        return billRepository.findAll(pageable)
                .map(this::convertToDTO);
    }

    @Override
    @Transactional(readOnly = true)
    public Page<BillDTO> getBillsByDateRange(LocalDateTime startDate, LocalDateTime endDate, Pageable pageable) {
        log.info("Fetching bills between {} and {}", startDate, endDate);
        
        return billRepository.findCompletedBillsByDateRange(startDate, endDate, pageable)
                .map(this::convertToDTO);
    }

    @Override
    public BillDTO voidBill(Integer billId, String reason, Integer userId) {
        log.info("Voiding bill with ID: {}, reason: {}", billId, reason);
        
        Bill bill = billRepository.findById(billId)
                .orElseThrow(() -> new ResourceNotFoundException("Bill not found with ID: " + billId));
        
        if (bill.getStatus() == Bill.BillStatus.VOIDED) {
            throw new IllegalStateException("Bill is already voided");
        }
        
        // Restore inventory
        List<BillItem> billItems = billItemRepository.findByBill_BillId(billId);
        for (BillItem item : billItems) {
            Product product = item.getProduct();
            product.setQuantityOnHand(product.getQuantityOnHand() + item.getQuantity());
            productRepository.save(product);
        }
        
        bill.setStatus(Bill.BillStatus.VOIDED);
        bill.setVoidReason(reason);
        bill.setUpdatedAt(LocalDateTime.now());
        
        Bill voidedBill = billRepository.save(bill);
        log.info("Bill voided successfully");
        
        return convertToDTO(voidedBill);
    }

    @Override
    @Transactional(readOnly = true)
    public Map<String, Object> getDailySalesSummary(LocalDate date) {
        log.info("Generating daily sales summary for date: {}", date);
        
        LocalDateTime startDateTime = date.atStartOfDay();
        LocalDateTime endDateTime = date.atTime(23, 59, 59);
        
        List<Bill> bills = billRepository.findByStatus(Bill.BillStatus.COMPLETED);
        // Filter by date range
        bills = bills.stream()
            .filter(b -> b.getCreatedAt().isAfter(startDateTime) && b.getCreatedAt().isBefore(endDateTime))
            .collect(Collectors.toList());
        
        Map<String, Object> summary = new HashMap<>();
        summary.put("date", date);
        summary.put("totalBills", bills.size());
        summary.put("totalRevenue", bills.stream()
                .map(Bill::getTotalAmount)
                .reduce(BigDecimal.ZERO, BigDecimal::add));
        summary.put("completedBills", bills.stream().filter(b -> b.getStatus() == Bill.BillStatus.COMPLETED).count());
        summary.put("voidedBills", bills.stream().filter(b -> b.getStatus() == Bill.BillStatus.VOIDED).count());
        
        if (!bills.isEmpty()) {
            BigDecimal average = bills.stream()
                .map(Bill::getTotalAmount)
                .reduce(BigDecimal.ZERO, BigDecimal::add)
                .divide(new BigDecimal(bills.size()), 2, java.math.RoundingMode.HALF_UP);
            summary.put("averageBillValue", average);
        } else {
            summary.put("averageBillValue", BigDecimal.ZERO);
        }
        
        log.info("Daily sales summary generated");
        return summary;
    }

    @Override
    @Transactional(readOnly = true)
    public String generateReceipt(Integer billId) {
        log.info("Generating receipt for bill: {}", billId);
        
        Bill bill = billRepository.findById(billId)
                .orElseThrow(() -> new ResourceNotFoundException("Bill not found with ID: " + billId));
        
        StringBuilder receipt = new StringBuilder();
        receipt.append("========== GROCERY STORE BILL ==========\n");
        receipt.append("Bill ID: ").append(bill.getBillId()).append("\n");
        receipt.append("Date: ").append(bill.getCreatedAt()).append("\n");
        receipt.append("========================================\n");
        
        List<BillItem> items = billItemRepository.findByBill_BillId(billId);
        for (BillItem item : items) {
            receipt.append(String.format("%-30s %10.2f x %5d = %10.2f\n",
                item.getProduct().getName(),
                item.getUnitPrice(),
                item.getQuantity(),
                item.getLineTotal()
            ));
        }
        
        receipt.append("========================================\n");
        receipt.append(String.format("Total Amount: Rs. %.2f\n", bill.getTotalAmount()));
        receipt.append("========================================\n");
        receipt.append("Thank you for shopping!\n");
        
        return receipt.toString();
    }

    @Override
    @Transactional(readOnly = true)
    public Page<BillDTO> getBillsByCustomer(Integer customerId, Pageable pageable) {
        log.info("Fetching bills for customer: {}", customerId);
        
        Customer customer = customerRepository.findById(customerId)
                .orElseThrow(() -> new ResourceNotFoundException("Customer not found with ID: " + customerId));
        
        return billRepository.findByCustomerId(customerId, pageable)
                .map(this::convertToDTO);
    }
    
    @Override
    @Transactional(readOnly = true)
    public Page<BillDTO> getBillsByCashier(Integer cashierId, Pageable pageable) {
        log.info("Fetching bills for cashier: {}", cashierId);
        return billRepository.findByCashierUserId(cashierId, pageable)
                .map(this::convertToDTO);
    }
    
    @Override
    @Transactional(readOnly = true)
    public BillDTO getBillByNumber(String billNumber) {
        log.info("Fetching bill by number: {}", billNumber);
        Bill bill = billRepository.findByBillNumber(billNumber)
                .orElseThrow(() -> new ResourceNotFoundException("Bill not found with number: " + billNumber));
        return convertToDTO(bill);
    }
    
    @Override
    @Transactional(readOnly = true)
    public Page<BillDTO> getBillsByStatus(String status, Pageable pageable) {
        log.info("Fetching bills with status: {}", status);
        return billRepository.findByStatus(Bill.BillStatus.valueOf(status), pageable)
                .map(this::convertToDTO);
    }

    /**
     * Convert Bill entity to BillDTO
     */
    private BillDTO convertToDTO(Bill bill) {
        List<BillItem> items = billItemRepository.findByBill_BillId(bill.getBillId());
        List<BillItemDTO> itemDTOs = items.stream()
                .map(item -> BillItemDTO.builder()
                        .billItemId(item.getItemId())
                        .productId(item.getProduct().getProductId())
                        .productName(item.getProduct().getName())
                        .quantity(item.getQuantity())
                        .unitPrice(item.getUnitPrice().doubleValue())
                        .lineTotal(item.getLineTotal().doubleValue())
                        .build())
                .collect(Collectors.toList());
        
        return BillDTO.builder()
                .billId(bill.getBillId())
                .userId(bill.getCashier().getUserId())
                .customerId(bill.getCustomer() != null ? bill.getCustomer().getCustomerId() : null)
                .totalAmount(bill.getTotalAmount().doubleValue())
                .billStatus(bill.getStatus().name())
                .items(itemDTOs)
                .createdAt(bill.getCreatedAt())
                .updatedAt(bill.getUpdatedAt())
                .build();
    }
}
