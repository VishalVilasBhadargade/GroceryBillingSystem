package com.grocerystore.billing.repository;

import com.grocerystore.billing.entity.Supplier;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface SupplierRepository extends JpaRepository<Supplier, Integer> {
    // Add custom query methods if needed
}
