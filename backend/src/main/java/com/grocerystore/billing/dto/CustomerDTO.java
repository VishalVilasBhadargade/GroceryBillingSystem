package com.grocerystore.billing.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import jakarta.validation.constraints.*;
import java.time.LocalDateTime;

/**
 * Customer DTO
 * Used for API request/response
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CustomerDTO {
    
    private Integer customerId;
    
    @NotBlank(message = "Customer name is required")
    @Size(min = 2, max = 100, message = "Name must be between 2 and 100 characters")
    private String name;
    
    @NotBlank(message = "Phone is required")
    @Pattern(regexp = "^[0-9]{10}$", message = "Phone must be 10 digits")
    private String phone;
    
    @Email(message = "Email must be valid")
    private String email;
    
    private String address;
    
    private String city;
    
    private String state;
    
    @Pattern(regexp = "^[0-9]{5,6}$", message = "Zip code must be 5-6 digits")
    private String zipCode;
    
    private Integer loyaltyPoints;
    
    private Double totalSpent;
    
    private LocalDateTime createdAt;
    
    private LocalDateTime updatedAt;
}
