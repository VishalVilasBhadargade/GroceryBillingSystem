package com.grocerystore.billing.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import java.time.LocalDateTime;
import java.util.List;

/**
 * Bill DTO
 * Used for API response
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class BillDTO {
    
    private Integer billId;
    
    private String billNumber;
    
    private Integer userId;
    
    private Integer customerId;
    
    @Positive(message = "Total amount must be positive")
    private Double totalAmount;
    
    private String billStatus;
    
    private List<BillItemDTO> items;
    
    private LocalDateTime createdAt;
    
    private LocalDateTime updatedAt;
}
