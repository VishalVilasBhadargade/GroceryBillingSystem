package com.grocerystore.billing.service;

import com.grocerystore.billing.dto.ChangePasswordDTO;
import com.grocerystore.billing.dto.UpdateUserDTO;
import com.grocerystore.billing.dto.UserResponseDTO;
import com.grocerystore.billing.entity.User;
import com.grocerystore.billing.exception.ResourceNotFoundException;
import com.grocerystore.billing.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * User Service Implementation
 * Handles user management operations
 */
@Service
@RequiredArgsConstructor
@Slf4j
@Transactional
public class UserServiceImpl implements UserService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    @Override
    @Transactional(readOnly = true)
    public UserResponseDTO getUserById(Integer userId) {
        log.info("Fetching user with ID: {}", userId);
        
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new ResourceNotFoundException("User not found with ID: " + userId));
        
        return convertToDTO(user);
    }

    @Override
    public UserResponseDTO updateUser(Integer userId, UpdateUserDTO updateUserDTO) {
        log.info("Updating user with ID: {}", userId);
        
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new ResourceNotFoundException("User not found with ID: " + userId));
        
        // Update fields
        if (updateUserDTO.getFirstName() != null) {
            user.setFirstName(updateUserDTO.getFirstName());
        }
        if (updateUserDTO.getLastName() != null) {
            user.setLastName(updateUserDTO.getLastName());
        }
        if (updateUserDTO.getEmail() != null) {
            // Check if email is already taken by another user
            if (userRepository.findByEmail(updateUserDTO.getEmail())
                    .filter(u -> !u.getUserId().equals(userId))
                    .isPresent()) {
                throw new IllegalArgumentException("Email already in use");
            }
            user.setEmail(updateUserDTO.getEmail());
        }
        
        User savedUser = userRepository.save(user);
        log.info("User updated successfully: {}", userId);
        
        return convertToDTO(savedUser);
    }

    @Override
    public void changePassword(Integer userId, ChangePasswordDTO changePasswordDTO) {
        log.info("Changing password for user: {}", userId);
        
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new ResourceNotFoundException("User not found with ID: " + userId));
        
        // Verify current password
        if (!passwordEncoder.matches(changePasswordDTO.getCurrentPassword(), user.getPasswordHash())) {
            throw new IllegalArgumentException("Current password is incorrect");
        }
        
        // Update to new password
        user.setPasswordHash(passwordEncoder.encode(changePasswordDTO.getNewPassword()));
        userRepository.save(user);
        
        log.info("Password changed successfully for user: {}", userId);
    }

    private UserResponseDTO convertToDTO(User user) {
        return UserResponseDTO.builder()
                .userId(user.getUserId())
                .username(user.getUsername())
                .email(user.getEmail())
                .firstName(user.getFirstName())
                .lastName(user.getLastName())
                .role(user.getRole().name())
                .isActive(user.getIsActive())
                .createdAt(user.getCreatedAt())
                .updatedAt(user.getUpdatedAt())
                .build();
    }
}
