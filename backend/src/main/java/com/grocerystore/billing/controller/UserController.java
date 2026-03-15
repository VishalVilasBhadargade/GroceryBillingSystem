package com.grocerystore.billing.controller;

import com.grocerystore.billing.dto.ChangePasswordDTO;
import com.grocerystore.billing.dto.UpdateUserDTO;
import com.grocerystore.billing.dto.UserResponseDTO;
import com.grocerystore.billing.response.ApiResponse;
import com.grocerystore.billing.service.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

/**
 * User Controller
 * REST endpoints for user management
 */
@RestController
@RequestMapping("/api/v1/users")
@RequiredArgsConstructor
@Slf4j
@Validated
@CrossOrigin(origins = "*")
public class UserController {

    private final UserService userService;

    /**
     * Get user by ID
     */
    @GetMapping("/{userId}")
    public ResponseEntity<ApiResponse<UserResponseDTO>> getUserById(@PathVariable Integer userId) {
        log.info("Getting user by ID: {}", userId);
        UserResponseDTO user = userService.getUserById(userId);
        return ResponseEntity.ok(ApiResponse.success(user, "User retrieved successfully"));
    }

    /**
     * Update user profile
     */
    @PutMapping("/{userId}")
    public ResponseEntity<ApiResponse<UserResponseDTO>> updateUser(
            @PathVariable Integer userId,
            @Valid @RequestBody UpdateUserDTO updateUserDTO) {
        log.info("Updating user: {}", userId);
        UserResponseDTO updatedUser = userService.updateUser(userId, updateUserDTO);
        return ResponseEntity.ok(ApiResponse.success(updatedUser, "User updated successfully"));
    }

    /**
     * Change user password
     */
    @PutMapping("/{userId}/change-password")
    public ResponseEntity<ApiResponse<Void>> changePassword(
            @PathVariable Integer userId,
            @Valid @RequestBody ChangePasswordDTO changePasswordDTO) {
        log.info("Changing password for user: {}", userId);
        userService.changePassword(userId, changePasswordDTO);
        return ResponseEntity.ok(ApiResponse.success(null, "Password changed successfully"));
    }
}
