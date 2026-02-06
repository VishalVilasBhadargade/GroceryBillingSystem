package com.grocerystore.billing.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import jakarta.validation.constraints.Positive;
import java.time.LocalDateTime;

/**
 * Payment DTO
 * Used for API response
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PaymentDTO {
    
    private Integer paymentId;
    
    private Integer billId;
    
    @Positive(message = "Amount must be positive")
    private Double amount;
    
    private String paymentMethod;
    
    private String paymentStatus;
    
    private String transactionId;
    
    private LocalDateTime createdAt;
    
    private LocalDateTime updatedAt;
}
