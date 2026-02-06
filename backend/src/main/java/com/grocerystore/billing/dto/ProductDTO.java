package com.grocerystore.billing.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.math.BigDecimal;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ProductDTO {
    private Integer productId;
    private Long id; // Legacy field
    private String sku;
    private String barcode;
    private String name;
    private String description;
    private Double price;
    private BigDecimal costPrice;
    private Integer quantity;
    private Integer quantityOnHand;
    private Integer reorderLevel;
    private Integer categoryId;
    private Integer supplierId;
    private Boolean isActive;
}
