package com.grocerystore.billing.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Login Response DTO
 * Used for login response with JWT token
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class LoginResponseDTO {
    
    private String token;
    
    private String type;
    
    private Integer userId;
    
    private String username;
    
    private String role;
    
    private Long expiresIn;
}
