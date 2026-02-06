package com.grocerystore.billing.service;

import com.grocerystore.billing.dto.LoginRequestDTO;
import com.grocerystore.billing.dto.LoginResponseDTO;

/**
 * Authentication Service Interface
 */
public interface AuthService {
    
    /**
     * Login user and return JWT token
     */
    LoginResponseDTO login(LoginRequestDTO loginRequestDTO);
    
    /**
     * Verify JWT token
     */
    boolean verifyToken(String token);
}
