package com.grocerystore.billing.controller;

import com.grocerystore.billing.dto.LoginRequestDTO;
import com.grocerystore.billing.dto.LoginResponseDTO;
import com.grocerystore.billing.response.ApiResponse;
import com.grocerystore.billing.service.AuthService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import jakarta.validation.Valid;

/**
 * Authentication Controller
 * REST endpoints for user authentication
 */
@RestController
@RequestMapping("/api/v1/auth")
@RequiredArgsConstructor
@Slf4j
@Validated
public class AuthController {

    private final AuthService authService;

    /**
     * User login
     */
    @PostMapping("/login")
    public ResponseEntity<ApiResponse<LoginResponseDTO>> login(
            @Valid @RequestBody LoginRequestDTO loginRequestDTO) {
        
        log.info("User login attempt: {}", loginRequestDTO.getUsername());
        LoginResponseDTO loginResponse = authService.login(loginRequestDTO);
        
        return ResponseEntity.status(HttpStatus.OK)
                .body(ApiResponse.success(loginResponse, "Login successful"));
    }

    /**
     * Verify token
     */
    @GetMapping("/verify")
    public ResponseEntity<ApiResponse<Boolean>> verifyToken(
            @RequestHeader("Authorization") String token) {
        
        log.info("Verifying token");
        boolean isValid = authService.verifyToken(token.replace("Bearer ", ""));
        
        return ResponseEntity.ok(ApiResponse.success(isValid, "Token verification complete"));
    }
}
