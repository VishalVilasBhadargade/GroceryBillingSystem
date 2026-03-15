package com.grocerystore.billing.service;

import com.grocerystore.billing.dto.ChangePasswordDTO;
import com.grocerystore.billing.dto.UpdateUserDTO;
import com.grocerystore.billing.dto.UserResponseDTO;

/**
 * User Service Interface
 */
public interface UserService {
    
    /**
     * Get user by ID
     */
    UserResponseDTO getUserById(Integer userId);
    
    /**
     * Update user profile
     */
    UserResponseDTO updateUser(Integer userId, UpdateUserDTO updateUserDTO);
    
    /**
     * Change user password
     */
    void changePassword(Integer userId, ChangePasswordDTO changePasswordDTO);
}
