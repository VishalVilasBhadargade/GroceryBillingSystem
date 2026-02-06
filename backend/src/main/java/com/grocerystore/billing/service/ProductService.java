package com.grocerystore.billing.service;

import com.grocerystore.billing.dto.ProductDTO;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.util.List;

/**
 * Product Service Interface
 * Business logic for Product operations
 */
public interface ProductService {

    /**
     * Get all products with pagination
     */
    Page<ProductDTO> getAllProducts(Pageable pageable);

    /**
     * Get product by ID
     */
    ProductDTO getProductById(Integer productId);

    /**
     * Get product by barcode
     */
    ProductDTO getProductByBarcode(String barcode);

    /**
     * Search products by term
     */
    Page<ProductDTO> searchProducts(String searchTerm, Pageable pageable);

    /**
     * Get products by category
     */
    Page<ProductDTO> getProductsByCategory(Integer categoryId, Pageable pageable);

    /**
     * Create new product
     */
    ProductDTO createProduct(ProductDTO productDTO);

    /**
     * Update product
     */
    ProductDTO updateProduct(Integer productId, ProductDTO productDTO);

    /**
     * Delete product
     */
    void deleteProduct(Integer productId);

    /**
     * Get low stock products
     */
    List<ProductDTO> getLowStockProducts();

    /**
     * Get expired products
     */
    List<ProductDTO> getExpiredProducts();

    /**
     * Update product quantity
     */
    void updateProductQuantity(Integer productId, Integer newQuantity);

    /**
     * Check if product exists by barcode
     */
    boolean existsByBarcode(String barcode);

    /**
     * Check if product exists by SKU
     */
    boolean existsBySku(String sku);
}
