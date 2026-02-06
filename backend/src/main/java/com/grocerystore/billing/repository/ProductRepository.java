package com.grocerystore.billing.repository;

import com.grocerystore.billing.entity.Product;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.List;

/**
 * Product Repository
 * Data access layer for Product entity
 */
@Repository
public interface ProductRepository extends JpaRepository<Product, Integer> {

    Optional<Product> findByBarcode(String barcode);

    Optional<Product> findBySku(String sku);

    Page<Product> findByIsActiveTrue(Pageable pageable);

    @Query("SELECT p FROM Product p WHERE p.category.categoryId = :categoryId AND p.isActive = true")
    Page<Product> findByCategoryIdAndIsActiveTrue(@Param("categoryId") Integer categoryId, Pageable pageable);

    @Query("SELECT p FROM Product p WHERE p.isActive = true AND " +
           "(LOWER(p.name) LIKE LOWER(CONCAT('%', :searchTerm, '%')) OR " +
           "LOWER(p.description) LIKE LOWER(CONCAT('%', :searchTerm, '%')))")
    Page<Product> searchProducts(@Param("searchTerm") String searchTerm, Pageable pageable);

    List<Product> findByQuantityOnHandLessThanAndIsActiveTrue(Integer reorderLevel);

    @Query("SELECT p FROM Product p WHERE p.expiryDate IS NOT NULL " +
           "AND p.expiryDate <= CURRENT_DATE AND p.isActive = true")
    List<Product> findExpiredProducts();

    @Query("SELECT p FROM Product p WHERE p.supplier.supplierId = :supplierId")
    Page<Product> findBySupplierId(@Param("supplierId") Integer supplierId, Pageable pageable);

    long countByIsActiveTrue();

    long countByQuantityOnHandLessThan(Integer level);
}
