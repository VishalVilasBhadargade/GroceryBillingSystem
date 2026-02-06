package com.grocerystore.billing.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import java.util.List;

/**
 * Create Bill DTO
 * Used for creating bills with items
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CreateBillDTO {
    
    private Integer customerId;
    
    @NotEmpty(message = "Bill must contain at least one item")
    @Valid
    private List<BillItemDTO> items;
}
