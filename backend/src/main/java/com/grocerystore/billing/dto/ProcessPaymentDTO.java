package com.grocerystore.billing.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;

/**
 * Process Payment DTO
 * Used for processing payments
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ProcessPaymentDTO {
    
    @NotNull(message = "Bill ID is required")
    private Integer billId;
    
    @NotNull(message = "Amount is required")
    @Positive(message = "Amount must be positive")
    private Double amount;
    
    @NotNull(message = "Payment method is required")
    private String paymentMethod;
    
    private String referenceNumber;
}
