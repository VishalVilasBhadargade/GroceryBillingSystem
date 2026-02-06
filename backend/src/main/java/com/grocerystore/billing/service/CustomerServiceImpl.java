package com.grocerystore.billing.service;

import org.springframework.stereotype.Service;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.transaction.annotation.Transactional;
import org.modelmapper.ModelMapper;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import com.grocerystore.billing.dto.CustomerDTO;
import com.grocerystore.billing.service.CustomerService;
import com.grocerystore.billing.entity.Customer;
import com.grocerystore.billing.exception.DuplicateResourceException;
import com.grocerystore.billing.exception.ResourceNotFoundException;
import com.grocerystore.billing.repository.CustomerRepository;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Optional;

/**
 * Customer Service Implementation
 * Manages customer CRUD operations and loyalty program
 */
@Service
@RequiredArgsConstructor
@Slf4j
@Transactional
public class CustomerServiceImpl implements CustomerService {

    private final CustomerRepository customerRepository;
    private final ModelMapper modelMapper;

    @Override
    public CustomerDTO createCustomer(CustomerDTO customerDTO) {
        log.info("Creating new customer: {}", customerDTO.getName());
        // Check for duplicate phone
        if (customerRepository.existsByPhone(customerDTO.getPhone())) {
            throw new DuplicateResourceException("Phone number already exists: " + customerDTO.getPhone());
        }
        // Check for duplicate email if provided
        if (customerDTO.getEmail() != null && 
            customerRepository.existsByEmail(customerDTO.getEmail())) {
            throw new DuplicateResourceException("Email already exists: " + customerDTO.getEmail());
        }
        Customer customer = new Customer();
        customer.setName(customerDTO.getName());
        customer.setPhone(customerDTO.getPhone());
        customer.setEmail(customerDTO.getEmail());
        customer.setAddress(customerDTO.getAddress());
        customer.setCity(customerDTO.getCity());
        customer.setState(customerDTO.getState());
        customer.setZipCode(customerDTO.getZipCode());
        customer.setLoyaltyPoints(0);
        customer.setTotalSpent(BigDecimal.ZERO);
        customer.setCreatedAt(LocalDateTime.now());
        customer.setUpdatedAt(LocalDateTime.now());
        customer.setMemberSince(LocalDateTime.now());
        customer.setIsActive(true);
        Customer savedCustomer = customerRepository.save(customer);
        log.info("Customer created successfully with ID: {}", savedCustomer.getCustomerId());
        return modelMapper.map(savedCustomer, CustomerDTO.class);
    }
    @Override
    @Transactional(readOnly = true)
    public CustomerDTO getCustomerByPhone(String phone) {
        log.info("Fetching customer with phone: {}", phone);
        Customer customer = customerRepository.findByPhone(phone)
                .orElseThrow(() -> new ResourceNotFoundException("Customer not found with phone: " + phone));
        return modelMapper.map(customer, CustomerDTO.class);
    }

    @Override
    @Transactional(readOnly = true)
    public CustomerDTO getCustomerById(Integer customerId) {
        log.info("Fetching customer with ID: {}", customerId);
        Customer customer = customerRepository.findById(customerId)
                .orElseThrow(() -> new ResourceNotFoundException("Customer not found with ID: " + customerId));
        return modelMapper.map(customer, CustomerDTO.class);
    }

    @Override
    @Transactional(readOnly = true)
    public Page<CustomerDTO> getAllCustomers(Pageable pageable) {
        log.info("Fetching all customers with pagination");
        return customerRepository.findAll(pageable)
                .map(customer -> modelMapper.map(customer, CustomerDTO.class));
    }

    @Override
    public CustomerDTO updateCustomer(Integer customerId, CustomerDTO customerDTO) {
        log.info("Updating customer with ID: {}", customerId);
        Customer customer = customerRepository.findById(customerId)
                .orElseThrow(() -> new ResourceNotFoundException("Customer not found with ID: " + customerId));
        // Check phone uniqueness if phone is being updated
        if (!customer.getPhone().equals(customerDTO.getPhone()) &&
            customerRepository.existsByPhone(customerDTO.getPhone())) {
            throw new DuplicateResourceException("Phone number already exists: " + customerDTO.getPhone());
        }
        // Check email uniqueness if email is being updated
        if (customerDTO.getEmail() != null &&
            !customerDTO.getEmail().equals(customer.getEmail()) &&
            customerRepository.existsByEmail(customerDTO.getEmail())) {
            throw new DuplicateResourceException("Email already exists: " + customerDTO.getEmail());
        }
        customer.setName(customerDTO.getName());
        customer.setPhone(customerDTO.getPhone());
        customer.setEmail(customerDTO.getEmail());
        customer.setAddress(customerDTO.getAddress());
        customer.setCity(customerDTO.getCity());
        customer.setState(customerDTO.getState());
        customer.setZipCode(customerDTO.getZipCode());
        customer.setUpdatedAt(LocalDateTime.now());
        Customer updatedCustomer = customerRepository.save(customer);
        log.info("Customer updated successfully");
        return modelMapper.map(updatedCustomer, CustomerDTO.class);
    }

    @Override
    public void deleteCustomer(Integer customerId) {
        log.info("Deleting customer with ID: {}", customerId);
        Customer customer = customerRepository.findById(customerId)
                .orElseThrow(() -> new ResourceNotFoundException("Customer not found with ID: " + customerId));
        customerRepository.delete(customer);
        log.info("Customer deleted successfully");
    }

    @Override
    public Page<CustomerDTO> searchCustomers(String searchTerm, Pageable pageable) {
        log.info("Searching customers with term: {}", searchTerm);
        return customerRepository.searchCustomers(searchTerm, pageable)
                .map(customer -> modelMapper.map(customer, CustomerDTO.class));
    }

    @Override
    public void addLoyaltyPoints(Integer customerId, Integer points) {
        log.info("Adding {} loyalty points to customer: {}", points, customerId);
        Customer customer = customerRepository.findById(customerId)
                .orElseThrow(() -> new ResourceNotFoundException("Customer not found with ID: " + customerId));
        customer.setLoyaltyPoints(customer.getLoyaltyPoints() + points);
        customer.setUpdatedAt(LocalDateTime.now());
        customerRepository.save(customer);
        log.info("Loyalty points added successfully");
    }

    @Override
    public void updateTotalSpent(Integer customerId, BigDecimal amount) {
        log.info("Updating total spent for customer: {} with amount: {}", customerId, amount);
        Customer customer = customerRepository.findById(customerId)
                .orElseThrow(() -> new ResourceNotFoundException("Customer not found with ID: " + customerId));
        customer.setTotalSpent(customer.getTotalSpent().add(amount));
        customer.setUpdatedAt(LocalDateTime.now());
        customerRepository.save(customer);
        log.info("Total spent updated successfully");
    }

    @Override
    @Transactional(readOnly = true)
    public boolean existsByPhone(String phone) {
        return customerRepository.existsByPhone(phone);
    }

    @Override
    @Transactional(readOnly = true)
    public boolean existsByEmail(String email) {
        return customerRepository.existsByEmail(email);
    }

}
