package com.grocerystore.billing.service;

import com.grocerystore.billing.dto.LoginRequestDTO;
import com.grocerystore.billing.dto.LoginResponseDTO;
import com.grocerystore.billing.entity.User;
import com.grocerystore.billing.exception.ResourceNotFoundException;
import com.grocerystore.billing.repository.UserRepository;
import com.grocerystore.billing.util.JwtTokenProvider;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * Authentication Service Implementation
 * Handles user login and token generation
 */
@Service
@RequiredArgsConstructor
@Slf4j
@Transactional
public class AuthServiceImpl implements AuthService {

    private final UserRepository userRepository;
    private final JwtTokenProvider tokenProvider;
    private final PasswordEncoder passwordEncoder;

    @Override
    public LoginResponseDTO login(LoginRequestDTO loginRequestDTO) {
        log.info("Processing login for user: {}", loginRequestDTO.getUsername());
        
        User user = userRepository.findByUsername(loginRequestDTO.getUsername())
                .orElseThrow(() -> new ResourceNotFoundException("User not found with username: " + loginRequestDTO.getUsername()));
        
        if (!passwordEncoder.matches(loginRequestDTO.getPassword(), user.getPasswordHash())) {
            throw new IllegalArgumentException("Invalid password");
        }
        
        String token = tokenProvider.generateToken(
            user.getUserId(),
            user.getUsername(),
            user.getRole().name()
        );
        
        log.info("Token generated successfully for user: {}", loginRequestDTO.getUsername());
        
        return LoginResponseDTO.builder()
                .token(token)
                .type("Bearer")
                .userId(user.getUserId())
                .username(user.getUsername())
                .role(user.getRole().name())
                .expiresIn(86400000L)
                .build();
    }

    @Override
    public boolean verifyToken(String token) {
        log.info("Verifying token");
        return tokenProvider.validateToken(token);
    }
}
