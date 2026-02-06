package com.grocerystore.billing.repository;

import com.grocerystore.billing.entity.Customer;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.Optional;

/**
 * Customer Repository
 * Data access layer for Customer entity
 */
@Repository
public interface CustomerRepository extends JpaRepository<Customer, Integer> {

    Optional<Customer> findByPhone(String phone);

    Optional<Customer> findByEmail(String email);

    boolean existsByPhone(String phone);

    boolean existsByEmail(String email);

    Page<Customer> findByIsActiveTrue(Pageable pageable);

    @Query("SELECT c FROM Customer c WHERE c.isActive = true AND " +
           "(LOWER(c.firstName) LIKE LOWER(CONCAT('%', :searchTerm, '%')) OR " +
           "LOWER(c.lastName) LIKE LOWER(CONCAT('%', :searchTerm, '%')) OR " +
           "LOWER(c.phone) LIKE LOWER(CONCAT('%', :searchTerm, '%')))")
    Page<Customer> searchCustomers(@Param("searchTerm") String searchTerm, Pageable pageable);

    long countByIsActiveTrue();
}
