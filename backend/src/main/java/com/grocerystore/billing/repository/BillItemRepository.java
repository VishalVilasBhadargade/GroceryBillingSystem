package com.grocerystore.billing.repository;

import com.grocerystore.billing.entity.BillItem;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * Bill Item Repository
 * Data access for BillItem entities
 */
@Repository
public interface BillItemRepository extends JpaRepository<BillItem, Integer> {
    
    /**
     * Find all bill items by bill ID
     */
    List<BillItem> findByBill_BillId(Integer billId);
    
    /**
     * Find all bill items by product ID
     */
    List<BillItem> findByProduct_ProductId(Integer productId);
}
