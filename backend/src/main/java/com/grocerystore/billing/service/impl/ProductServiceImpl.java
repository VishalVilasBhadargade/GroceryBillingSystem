package com.grocerystore.billing.service.impl;

import com.grocerystore.billing.dto.ProductDTO;
import com.grocerystore.billing.entity.Category;
import com.grocerystore.billing.entity.Product;
import com.grocerystore.billing.entity.Supplier;
import com.grocerystore.billing.exception.ResourceNotFoundException;
import com.grocerystore.billing.exception.DuplicateResourceException;
import com.grocerystore.billing.repository.ProductRepository;
import com.grocerystore.billing.repository.CategoryRepository;
import com.grocerystore.billing.repository.SupplierRepository;
import com.grocerystore.billing.service.ProductService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.modelmapper.ModelMapper;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Product Service Implementation
 * Handles all product-related business logic
 */
@Service
@Transactional
@RequiredArgsConstructor
@Slf4j
public class ProductServiceImpl implements ProductService {

    private final ProductRepository productRepository;
    private final CategoryRepository categoryRepository;
    private final SupplierRepository supplierRepository;
    private final ModelMapper modelMapper;

    @Override
    @Transactional(readOnly = true)
    public Page<ProductDTO> getAllProducts(Pageable pageable) {
        log.info("Fetching all products with pagination: {}", pageable);
        return productRepository.findByIsActiveTrue(pageable)
                .map(product -> modelMapper.map(product, ProductDTO.class));
    }

    @Override
    @Transactional(readOnly = true)
    public ProductDTO getProductById(Integer productId) {
        log.info("Fetching product with ID: {}", productId);
        Product product = productRepository.findById(productId)
                .orElseThrow(() -> new ResourceNotFoundException(
                        "Product not found with ID: " + productId));
        return modelMapper.map(product, ProductDTO.class);
    }

    @Override
    @Transactional(readOnly = true)
    public ProductDTO getProductByBarcode(String barcode) {
        log.info("Fetching product with barcode: {}", barcode);
        Product product = productRepository.findByBarcode(barcode)
                .orElseThrow(() -> new ResourceNotFoundException(
                        "Product not found with barcode: " + barcode));
        return modelMapper.map(product, ProductDTO.class);
    }

    @Override
    @Transactional(readOnly = true)
    public Page<ProductDTO> searchProducts(String searchTerm, Pageable pageable) {
        log.info("Searching products with term: {}", searchTerm);
        return productRepository.searchProducts(searchTerm, pageable)
                .map(product -> modelMapper.map(product, ProductDTO.class));
    }

    @Override
    @Transactional(readOnly = true)
    public Page<ProductDTO> getProductsByCategory(Integer categoryId, Pageable pageable) {
        log.info("Fetching products for category: {}", categoryId);
        return productRepository.findByCategoryIdAndIsActiveTrue(categoryId, pageable)
                .map(product -> modelMapper.map(product, ProductDTO.class));
    }

    @Override
    public ProductDTO createProduct(ProductDTO productDTO) {
        log.info("Creating new product: {}", productDTO.getName());
        
        // Validate unique fields
        if (productRepository.findBySku(productDTO.getSku()).isPresent()) {
            throw new DuplicateResourceException("SKU already exists: " + productDTO.getSku());
        }
        if (productRepository.findByBarcode(productDTO.getBarcode()).isPresent()) {
            throw new DuplicateResourceException("Barcode already exists: " + productDTO.getBarcode());
        }

        Product product = modelMapper.map(productDTO, Product.class);
        
        // Load related entities
        if (productDTO.getCategoryId() != null) {
            Category category = categoryRepository.findById(productDTO.getCategoryId())
                    .orElseThrow(() -> new ResourceNotFoundException("Category not found"));
            product.setCategory(category);
        }
        if (productDTO.getSupplierId() != null) {
            Supplier supplier = supplierRepository.findById(productDTO.getSupplierId())
                    .orElseThrow(() -> new ResourceNotFoundException("Supplier not found"));
            product.setSupplier(supplier);
        }
        
        Product savedProduct = productRepository.save(product);
        log.info("Product created successfully with ID: {}", savedProduct.getProductId());
        
        return modelMapper.map(savedProduct, ProductDTO.class);
    }

    @Override
    public ProductDTO updateProduct(Integer productId, ProductDTO productDTO) {
        log.info("Updating product with ID: {}", productId);
        
        Product product = productRepository.findById(productId)
                .orElseThrow(() -> new ResourceNotFoundException("Product not found with ID: " + productId));

        // Update fields
        product.setName(productDTO.getName());
        product.setDescription(productDTO.getDescription());
        product.setPrice(productDTO.getPrice() != null ? BigDecimal.valueOf(productDTO.getPrice()) : product.getPrice());
        product.setCostPrice(productDTO.getCostPrice());
        product.setQuantityOnHand(productDTO.getQuantityOnHand());
        product.setReorderLevel(productDTO.getReorderLevel());
        product.setIsActive(productDTO.getIsActive());

        Product updatedProduct = productRepository.save(product);
        log.info("Product updated successfully with ID: {}", productId);
        
        return modelMapper.map(updatedProduct, ProductDTO.class);
    }

    @Override
    public void deleteProduct(Integer productId) {
        log.info("Deleting product with ID: {}", productId);
        
        Product product = productRepository.findById(productId)
                .orElseThrow(() -> new ResourceNotFoundException("Product not found with ID: " + productId));
        
        product.setIsActive(false);
        productRepository.save(product);
        
        log.info("Product soft-deleted with ID: {}", productId);
    }

    @Override
    @Transactional(readOnly = true)
    public List<ProductDTO> getLowStockProducts() {
        log.info("Fetching low stock products");
        return productRepository.findByQuantityOnHandLessThanAndIsActiveTrue(0)
                .stream()
                .map(product -> modelMapper.map(product, ProductDTO.class))
                .collect(Collectors.toList());
    }

    @Override
    @Transactional(readOnly = true)
    public List<ProductDTO> getExpiredProducts() {
        log.info("Fetching expired products");
        return productRepository.findExpiredProducts()
                .stream()
                .map(product -> modelMapper.map(product, ProductDTO.class))
                .collect(Collectors.toList());
    }

    @Override
    public void updateProductQuantity(Integer productId, Integer newQuantity) {
        log.info("Updating quantity for product ID: {} to: {}", productId, newQuantity);
        
        Product product = productRepository.findById(productId)
                .orElseThrow(() -> new ResourceNotFoundException("Product not found"));
        
        product.setQuantityOnHand(newQuantity);
        productRepository.save(product);
    }

    @Override
    @Transactional(readOnly = true)
    public boolean existsByBarcode(String barcode) {
        return productRepository.findByBarcode(barcode).isPresent();
    }

    @Override
    @Transactional(readOnly = true)
    public boolean existsBySku(String sku) {
        return productRepository.findBySku(sku).isPresent();
    }
}
