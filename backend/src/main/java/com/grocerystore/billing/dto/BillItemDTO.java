package com.grocerystore.billing.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;

/**
 * Bill Item DTO
 * Used for bill items in create bill request
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class BillItemDTO {
    
    private Integer billItemId;
    
    @NotNull(message = "Product ID is required")
    private Integer productId;
    
    private String productName;
    
    @NotNull(message = "Quantity is required")
    @Positive(message = "Quantity must be positive")
    private Integer quantity;
    
    private Double unitPrice;
    
    private Double lineTotal;
}
