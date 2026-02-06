package com.grocerystore.billing.service;

import com.grocerystore.billing.dto.CustomerDTO;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

/**
 * Customer Service Interface
 * Business logic for Customer operations
 */
public interface CustomerService {

    /**
     * Get all customers with pagination
     */
    Page<CustomerDTO> getAllCustomers(Pageable pageable);

    /**
     * Get customer by ID
     */
    CustomerDTO getCustomerById(Integer customerId);

    /**
     * Get customer by phone
     */
    CustomerDTO getCustomerByPhone(String phone);

    /**
     * Search customers by term
     */
    Page<CustomerDTO> searchCustomers(String searchTerm, Pageable pageable);

    /**
     * Create new customer
     */
    CustomerDTO createCustomer(CustomerDTO customerDTO);

    /**
     * Update customer
     */
    CustomerDTO updateCustomer(Integer customerId, CustomerDTO customerDTO);

    /**
     * Delete customer (soft delete)
     */
    void deleteCustomer(Integer customerId);

    /**
     * Add loyalty points to customer
     */
    void addLoyaltyPoints(Integer customerId, Integer points);

    /**
     * Update customer total spent
     */
    void updateTotalSpent(Integer customerId, java.math.BigDecimal amount);

    /**
     * Check if phone exists
     */
    boolean existsByPhone(String phone);

    /**
     * Check if email exists
     */
    boolean existsByEmail(String email);
}
