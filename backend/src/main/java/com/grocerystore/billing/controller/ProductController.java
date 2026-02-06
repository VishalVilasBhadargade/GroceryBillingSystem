package com.grocerystore.billing.controller;

import com.grocerystore.billing.dto.ProductDTO;
import com.grocerystore.billing.response.ApiResponse;
import com.grocerystore.billing.service.ProductService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;

/**
 * Product Controller
 * REST endpoints for product management
 */
@RestController
@RequestMapping("/api/v1/products")
@RequiredArgsConstructor
@Slf4j
@Validated
public class ProductController {

    private final ProductService productService;

    /**
     * Get all products
     */
    @GetMapping
    @PreAuthorize("hasAnyRole('ADMIN', 'MANAGER', 'CASHIER')")
    public ResponseEntity<ApiResponse<Page<ProductDTO>>> getAllProducts(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        
        log.info("Fetching products - page: {}, size: {}", page, size);
        Pageable pageable = PageRequest.of(page, size);
        Page<ProductDTO> products = productService.getAllProducts(pageable);
        
        return ResponseEntity.ok(ApiResponse.success(products, "Products retrieved successfully"));
    }

    /**
     * Get product by ID
     */
    @GetMapping("/{productId}")
    @PreAuthorize("hasAnyRole('ADMIN', 'MANAGER', 'CASHIER')")
    public ResponseEntity<ApiResponse<ProductDTO>> getProductById(
            @PathVariable Integer productId) {
        
        log.info("Fetching product with ID: {}", productId);
        ProductDTO product = productService.getProductById(productId);
        
        return ResponseEntity.ok(ApiResponse.success(product, "Product retrieved successfully"));
    }

    /**
     * Get product by barcode (POS scanning)
     */
    @GetMapping("/barcode/{barcode}")
    @PreAuthorize("hasAnyRole('ADMIN', 'MANAGER', 'CASHIER')")
    public ResponseEntity<ApiResponse<ProductDTO>> getProductByBarcode(
            @PathVariable @NotBlank String barcode) {
        
        log.info("Fetching product with barcode: {}", barcode);
        ProductDTO product = productService.getProductByBarcode(barcode);
        
        return ResponseEntity.ok(ApiResponse.success(product, "Product retrieved successfully"));
    }

    /**
     * Search products
     */
    @GetMapping("/search")
    @PreAuthorize("hasAnyRole('ADMIN', 'MANAGER', 'CASHIER')")
    public ResponseEntity<ApiResponse<Page<ProductDTO>>> searchProducts(
            @RequestParam @NotBlank String searchTerm,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        
        log.info("Searching products with term: {}", searchTerm);
        Pageable pageable = PageRequest.of(page, size);
        Page<ProductDTO> products = productService.searchProducts(searchTerm, pageable);
        
        return ResponseEntity.ok(ApiResponse.success(products, "Search completed successfully"));
    }

    /**
     * Create product
     */
    @PostMapping
    @PreAuthorize("hasAnyRole('ADMIN', 'MANAGER')")
    public ResponseEntity<ApiResponse<ProductDTO>> createProduct(
            @Valid @RequestBody ProductDTO productDTO) {
        
        log.info("Creating product: {}", productDTO.getName());
        ProductDTO createdProduct = productService.createProduct(productDTO);
        
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success(createdProduct, "Product created successfully"));
    }

    /**
     * Update product
     */
    @PutMapping("/{productId}")
    @PreAuthorize("hasAnyRole('ADMIN', 'MANAGER')")
    public ResponseEntity<ApiResponse<ProductDTO>> updateProduct(
            @PathVariable Integer productId,
            @Valid @RequestBody ProductDTO productDTO) {
        
        log.info("Updating product with ID: {}", productId);
        ProductDTO updatedProduct = productService.updateProduct(productId, productDTO);
        
        return ResponseEntity.ok(ApiResponse.success(updatedProduct, "Product updated successfully"));
    }

    /**
     * Delete product
     */
    @DeleteMapping("/{productId}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<ApiResponse<Void>> deleteProduct(
            @PathVariable Integer productId) {
        
        log.info("Deleting product with ID: {}", productId);
        productService.deleteProduct(productId);
        
        return ResponseEntity.noContent().build();
    }

    /**
     * Get low stock products
     */
    @GetMapping("/alerts/low-stock")
    @PreAuthorize("hasAnyRole('ADMIN', 'MANAGER', 'INVENTORY_MANAGER')")
    public ResponseEntity<ApiResponse<java.util.List<ProductDTO>>> getLowStockProducts() {
        
        log.info("Fetching low stock products");
        var lowStockProducts = productService.getLowStockProducts();
        
        return ResponseEntity.ok(ApiResponse.success(lowStockProducts, "Low stock products retrieved"));
    }
}
