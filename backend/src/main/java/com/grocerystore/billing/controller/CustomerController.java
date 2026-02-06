package com.grocerystore.billing.controller;

import com.grocerystore.billing.dto.CustomerDTO;
import com.grocerystore.billing.response.ApiResponse;
import com.grocerystore.billing.service.CustomerService;
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
 * Customer Controller
 * REST endpoints for customer management
 */
@RestController
@RequestMapping("/api/v1/customers")
@RequiredArgsConstructor
@Slf4j
@Validated
public class CustomerController {

    private final CustomerService customerService;

    /**
     * Create a new customer
     */
    @PostMapping
    @PreAuthorize("hasAnyRole('CASHIER', 'MANAGER', 'ADMIN')")
    public ResponseEntity<ApiResponse<CustomerDTO>> createCustomer(
            @Valid @RequestBody CustomerDTO customerDTO) {
        
        log.info("Creating new customer: {}", customerDTO.getName());
        CustomerDTO created = customerService.createCustomer(customerDTO);
        
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success(created, "Customer created successfully"));
    }

    /**
     * Get customer by ID
     */
    @GetMapping("/{customerId}")
    @PreAuthorize("hasAnyRole('CASHIER', 'MANAGER', 'ACCOUNTANT', 'ADMIN')")
    public ResponseEntity<ApiResponse<CustomerDTO>> getCustomerById(
            @PathVariable Integer customerId) {
        
        log.info("Fetching customer with ID: {}", customerId);
        CustomerDTO customer = customerService.getCustomerById(customerId);
        
        return ResponseEntity.ok(ApiResponse.success(customer, "Customer retrieved successfully"));
    }

    /**
     * Get all customers
     */
    @GetMapping
    @PreAuthorize("hasAnyRole('MANAGER', 'ACCOUNTANT', 'ADMIN')")
    public ResponseEntity<ApiResponse<Page<CustomerDTO>>> getAllCustomers(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        
        log.info("Fetching all customers - page: {}, size: {}", page, size);
        Pageable pageable = PageRequest.of(page, size);
        Page<CustomerDTO> customers = customerService.getAllCustomers(pageable);
        
        return ResponseEntity.ok(ApiResponse.success(customers, "Customers retrieved successfully"));
    }

    /**
     * Update customer
     */
    @PutMapping("/{customerId}")
    @PreAuthorize("hasAnyRole('MANAGER', 'ADMIN')")
    public ResponseEntity<ApiResponse<CustomerDTO>> updateCustomer(
            @PathVariable Integer customerId,
            @Valid @RequestBody CustomerDTO customerDTO) {
        
        log.info("Updating customer with ID: {}", customerId);
        CustomerDTO updated = customerService.updateCustomer(customerId, customerDTO);
        
        return ResponseEntity.ok(ApiResponse.success(updated, "Customer updated successfully"));
    }

    /**
     * Delete customer
     */
    @DeleteMapping("/{customerId}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<ApiResponse<Void>> deleteCustomer(
            @PathVariable Integer customerId) {
        
        log.info("Deleting customer with ID: {}", customerId);
        customerService.deleteCustomer(customerId);
        
        return ResponseEntity.ok(ApiResponse.success(null, "Customer deleted successfully"));
    }

    /**
     * Search customers
     */
    @GetMapping("/search")
    @PreAuthorize("hasAnyRole('CASHIER', 'MANAGER', 'ACCOUNTANT', 'ADMIN')")
    public ResponseEntity<ApiResponse<Page<CustomerDTO>>> searchCustomers(
            @RequestParam String searchTerm,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        
        log.info("Searching customers with term: {}", searchTerm);
        Pageable pageable = PageRequest.of(page, size);
        Page<CustomerDTO> results = customerService.searchCustomers(searchTerm, pageable);
        
        return ResponseEntity.ok(ApiResponse.success(results, "Customers retrieved successfully"));
    }

    /**
     * Add loyalty points
     */
    @PostMapping("/{customerId}/loyalty-points/add")
    @PreAuthorize("hasAnyRole('MANAGER', 'ADMIN')")
    public ResponseEntity<ApiResponse<CustomerDTO>> addLoyaltyPoints(
            @PathVariable Integer customerId,
            @RequestParam Integer points) {
        
        log.info("Adding {} loyalty points to customer: {}", points, customerId);
        customerService.addLoyaltyPoints(customerId, points);
        CustomerDTO updated = customerService.getCustomerById(customerId);
        
        return ResponseEntity.ok(ApiResponse.success(updated, "Loyalty points added successfully"));
    }

    /**
     * Redeem loyalty points
     */
    @PostMapping("/{customerId}/loyalty-points/redeem")
    @PreAuthorize("hasAnyRole('CASHIER', 'MANAGER', 'ADMIN')")
    public ResponseEntity<ApiResponse<CustomerDTO>> redeemLoyaltyPoints(
            @PathVariable Integer customerId,
            @RequestParam Integer points) {
        
        log.info("Redeeming {} loyalty points for customer: {}", points, customerId);
        // Add redeem method to service
        customerService.addLoyaltyPoints(customerId, -points); // Negative to redeem
        CustomerDTO updated = customerService.getCustomerById(customerId);
        
        return ResponseEntity.ok(ApiResponse.success(updated, "Loyalty points redeemed successfully"));
    }
}
