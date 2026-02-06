# Login & Authentication Flow - Grocery Billing Software

## 🔐 Overview

This document explains the complete authentication system including:
- Login UI and user interaction
- Backend JWT token generation
- Django session management
- Token verification and usage
- Security measures

---

## 📊 Authentication Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER LOGIN FLOW                          │
└─────────────────────────────────────────────────────────────────┘

1. USER ENTERS CREDENTIALS
   └─> Username & Password in Login Form

2. FRONTEND VALIDATION
   └─> Client-side validation (non-empty fields)
   └─> Send POST request to Django backend

3. DJANGO PROCESSES LOGIN
   ├─> Receive username & password
   ├─> Call API Client to authenticate with Java backend
   └─> Receive JWT token from Java backend

4. JAVA BACKEND AUTHENTICATES
   ├─> Verify username & password against database
   ├─> Check user exists and account is active
   ├─> Validate password using BCrypt
   └─> Generate JWT token with user details

5. RETURN TOKEN TO DJANGO
   ├─> Java returns: { token: "eyJhbGciOiJIUzI1NiIs...", user: {...} }
   └─> Include expiration time (24 hours)

6. DJANGO STORES TOKEN IN SESSION
   ├─> Save token in Django session: request.session['token']
   ├─> Save user info in session: request.session['user']
   └─> Create session cookie in browser

7. REDIRECT TO DASHBOARD
   ├─> User session established
   └─> All subsequent requests include token

8. AUTHENTICATED API CALLS
   ├─> Every API request includes: Authorization: Bearer {token}
   ├─> API Client validates token
   └─> Return response or 401 Unauthorized
```

---

## 🎨 Part 1: Login UI (HTML/CSS)

### Login Page Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Grocery Billing System - Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary-color: #2c3e50;
            --success-color: #27ae60;
            --danger-color: #e74c3c;
            --info-color: #3498db;
        }

        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        .login-container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
            width: 100%;
            max-width: 450px;
        }

        .login-header {
            background: linear-gradient(135deg, var(--primary-color) 0%, #34495e 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }

        .login-header i {
            font-size: 48px;
            margin-bottom: 15px;
            display: block;
        }

        .login-header h1 {
            font-size: 28px;
            font-weight: 700;
            margin: 10px 0 5px;
        }

        .login-header p {
            font-size: 14px;
            opacity: 0.9;
            margin: 0;
        }

        .login-body {
            padding: 40px 30px;
        }

        .form-group {
            margin-bottom: 25px;
        }

        .form-group label {
            display: block;
            font-weight: 600;
            color: var(--primary-color);
            margin-bottom: 8px;
            font-size: 14px;
        }

        .form-group input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #ecf0f1;
            border-radius: 8px;
            font-size: 14px;
            transition: all 0.3s ease;
        }

        .form-group input:focus {
            outline: none;
            border-color: var(--info-color);
            box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
        }

        .form-group input::placeholder {
            color: #95a5a6;
        }

        .form-group .input-group-text {
            background: white;
            border: 2px solid #ecf0f1;
            color: #7f8c8d;
        }

        .remember-forgot {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 13px;
            margin-bottom: 25px;
        }

        .remember-forgot a {
            color: var(--info-color);
            text-decoration: none;
            font-weight: 600;
        }

        .remember-forgot a:hover {
            text-decoration: underline;
        }

        .login-btn {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, var(--success-color) 0%, #229954 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 15px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }

        .login-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(39, 174, 96, 0.3);
        }

        .login-btn:active {
            transform: translateY(0);
        }

        .login-btn:disabled {
            background: #bdc3c7;
            cursor: not-allowed;
            transform: none;
        }

        .login-btn.loading::after {
            content: '';
            width: 16px;
            height: 16px;
            border: 3px solid #ffffff;
            border-radius: 50%;
            border-top-color: transparent;
            animation: spin 0.8s linear infinite;
            margin-left: 8px;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .alert {
            margin-bottom: 20px;
            border: none;
            border-radius: 8px;
            padding: 12px 15px;
            font-size: 13px;
        }

        .alert-danger {
            background: #fadbd8;
            color: #c0392b;
        }

        .alert-success {
            background: #d5f4e6;
            color: #27ae60;
        }

        .login-footer {
            text-align: center;
            padding: 20px 30px;
            background: #f8f9fa;
            border-top: 1px solid #ecf0f1;
            font-size: 13px;
            color: #7f8c8d;
        }

        .login-footer strong {
            display: block;
            margin-bottom: 8px;
            color: var(--primary-color);
        }

        .demo-creds {
            background: #e8f8f5;
            border-left: 4px solid var(--success-color);
            padding: 12px;
            border-radius: 4px;
            font-size: 12px;
        }

        .demo-creds strong {
            color: var(--success-color);
            display: block;
            margin-bottom: 5px;
        }

        .demo-creds code {
            background: white;
            padding: 3px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            color: var(--primary-color);
        }

        @media (max-width: 480px) {
            .login-container {
                margin: 20px;
            }

            .login-header {
                padding: 30px 20px;
            }

            .login-header h1 {
                font-size: 24px;
            }

            .login-body {
                padding: 30px 20px;
            }
        }
    </style>
</head>
<body>
    <div class="login-container">
        <!-- Header -->
        <div class="login-header">
            <i class="fas fa-lock"></i>
            <h1>Grocery Billing</h1>
            <p>Point of Sale System</p>
        </div>

        <!-- Login Form -->
        <div class="login-body">
            <form id="loginForm" onsubmit="handleLogin(event)">
                <!-- Error Message -->
                <div id="errorMessage" class="alert alert-danger" style="display: none;"></div>

                <!-- Success Message -->
                <div id="successMessage" class="alert alert-success" style="display: none;"></div>

                <!-- Username -->
                <div class="form-group">
                    <label for="username">
                        <i class="fas fa-user"></i> Username
                    </label>
                    <input 
                        type="text" 
                        id="username" 
                        name="username" 
                        placeholder="Enter your username" 
                        required
                        autocomplete="off"
                    >
                </div>

                <!-- Password -->
                <div class="form-group">
                    <label for="password">
                        <i class="fas fa-key"></i> Password
                    </label>
                    <input 
                        type="password" 
                        id="password" 
                        name="password" 
                        placeholder="Enter your password" 
                        required
                        autocomplete="off"
                    >
                </div>

                <!-- Remember & Forgot Password -->
                <div class="remember-forgot">
                    <label style="margin: 0; font-weight: 500;">
                        <input type="checkbox" id="rememberMe" style="margin-right: 5px;">
                        Remember me
                    </label>
                    <a href="#forgot-password">Forgot password?</a>
                </div>

                <!-- Login Button -->
                <button type="submit" class="login-btn" id="loginBtn">
                    <i class="fas fa-sign-in-alt"></i>
                    Sign In
                </button>
            </form>
        </div>

        <!-- Footer with Demo Credentials -->
        <div class="login-footer">
            <strong>Demo Credentials</strong>
            <div class="demo-creds">
                <strong>Admin User:</strong>
                Username: <code>admin</code> | Password: <code>admin123</code>
                <br><br>
                <strong>Cashier User:</strong>
                Username: <code>cashier1</code> | Password: <code>cashier123</code>
                <br><br>
                <strong>Inventory Manager:</strong>
                Username: <code>manager1</code> | Password: <code>manager123</code>
            </div>
        </div>
    </div>

    <script>
        /**
         * Handle login form submission
         * This is CLIENT-SIDE validation only
         * Actual authentication happens on backend
         */
        async function handleLogin(event) {
            event.preventDefault();
            
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value;
            const loginBtn = document.getElementById('loginBtn');
            const errorDiv = document.getElementById('errorMessage');
            const successDiv = document.getElementById('successMessage');

            // Clear previous messages
            errorDiv.style.display = 'none';
            successDiv.style.display = 'none';

            // Client-side validation
            if (!username) {
                showError('Please enter username');
                return;
            }

            if (!password) {
                showError('Please enter password');
                return;
            }

            if (password.length < 4) {
                showError('Password must be at least 4 characters');
                return;
            }

            // Show loading state
            loginBtn.disabled = true;
            loginBtn.classList.add('loading');
            loginBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Signing in...';

            try {
                // Send login request to Django backend
                // Django will forward this to Java backend and get JWT token
                const response = await fetch('/auth/login/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        username: username,
                        password: password,
                        rememberMe: document.getElementById('rememberMe').checked
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    // Login successful
                    successDiv.innerHTML = '✓ Login successful! Redirecting...';
                    successDiv.style.display = 'block';

                    // Redirect to dashboard after 1 second
                    setTimeout(() => {
                        window.location.href = '/dashboard/';
                    }, 1000);
                } else {
                    // Login failed
                    showError(data.message || 'Invalid username or password');
                }
            } catch (error) {
                console.error('Login error:', error);
                showError('Network error. Please try again.');
            } finally {
                // Reset button state
                loginBtn.disabled = false;
                loginBtn.classList.remove('loading');
                loginBtn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Sign In';
            }
        }

        /**
         * Display error message
         */
        function showError(message) {
            const errorDiv = document.getElementById('errorMessage');
            errorDiv.innerHTML = '✗ ' + message;
            errorDiv.style.display = 'block';
        }

        /**
         * Get CSRF token from cookie
         */
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let cookie of cookies) {
                    cookie = cookie.trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        // Auto-fill demo credentials for testing (optional)
        function loadDemoCredentials(role = 'admin') {
            const credentials = {
                admin: { username: 'admin', password: 'admin123' },
                cashier: { username: 'cashier1', password: 'cashier123' },
                manager: { username: 'manager1', password: 'manager123' }
            };

            const creds = credentials[role];
            if (creds) {
                document.getElementById('username').value = creds.username;
                document.getElementById('password').value = creds.password;
            }
        }
    </script>
</body>
</html>
```

---

## 🔒 Part 2: Java Spring Boot Backend Authentication

### JwtTokenProvider - Generate & Validate JWT Tokens

```java
package com.grocerystore.billing.security;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.nio.charset.StandardCharsets;
import java.security.Key;
import java.util.Date;

/**
 * JWT Token Provider
 * Handles token generation and validation
 */
@Component
public class JwtTokenProvider {

    // Secret key for signing tokens (load from environment variable)
    @Value("${app.jwt.secret:your-secret-key-min-32-chars-long-for-security}")
    private String jwtSecret;

    // Token expiration time (24 hours)
    @Value("${app.jwt.expiration:86400000}")
    private long jwtExpirationMs;

    /**
     * Generate JWT token for authenticated user
     * 
     * @param username User's username
     * @param userId User's ID
     * @param role User's role
     * @return JWT token string
     */
    public String generateToken(String username, Long userId, String role) {
        Date now = new Date();
        Date expiryDate = new Date(now.getTime() + jwtExpirationMs); // 24 hours from now

        Key key = Keys.hmacShaKeyFor(jwtSecret.getBytes(StandardCharsets.UTF_8));

        // Create JWT token with claims (payload)
        return Jwts.builder()
                .setSubject(username)                              // Subject: username
                .claim("userId", userId)                           // Custom claim: user ID
                .claim("role", role)                               // Custom claim: user role
                .setIssuedAt(now)                                  // Issue time
                .setExpiration(expiryDate)                         // Expiration time
                .signWith(key, SignatureAlgorithm.HS256)          // Sign with secret key
                .compact();                                        // Return compact form
    }

    /**
     * Validate JWT token
     * 
     * @param token JWT token to validate
     * @return true if valid, false otherwise
     */
    public boolean validateToken(String token) {
        try {
            Key key = Keys.hmacShaKeyFor(jwtSecret.getBytes(StandardCharsets.UTF_8));
            Jwts.parserBuilder()
                    .setSigningKey(key)
                    .build()
                    .parseClaimsJws(token);
            return true;
        } catch (Exception e) {
            // Invalid token, expired token, signature mismatch, etc.
            return false;
        }
    }

    /**
     * Extract username from token
     * 
     * @param token JWT token
     * @return username
     */
    public String getUsernameFromToken(String token) {
        Key key = Keys.hmacShaKeyFor(jwtSecret.getBytes(StandardCharsets.UTF_8));
        Claims claims = Jwts.parserBuilder()
                .setSigningKey(key)
                .build()
                .parseClaimsJws(token)
                .getBody();
        return claims.getSubject();
    }

    /**
     * Extract user ID from token
     * 
     * @param token JWT token
     * @return user ID
     */
    public Long getUserIdFromToken(String token) {
        Key key = Keys.hmacShaKeyFor(jwtSecret.getBytes(StandardCharsets.UTF_8));
        Claims claims = Jwts.parserBuilder()
                .setSigningKey(key)
                .build()
                .parseClaimsJws(token)
                .getBody();
        return claims.get("userId", Long.class);
    }

    /**
     * Extract user role from token
     * 
     * @param token JWT token
     * @return user role
     */
    public String getRoleFromToken(String token) {
        Key key = Keys.hmacShaKeyFor(jwtSecret.getBytes(StandardCharsets.UTF_8));
        Claims claims = Jwts.parserBuilder()
                .setSigningKey(key)
                .build()
                .parseClaimsJws(token)
                .getBody();
        return claims.get("role", String.class);
    }

    /**
     * Get token expiration time
     * 
     * @param token JWT token
     * @return expiration date
     */
    public Date getExpirationDateFromToken(String token) {
        Key key = Keys.hmacShaKeyFor(jwtSecret.getBytes(StandardCharsets.UTF_8));
        Claims claims = Jwts.parserBuilder()
                .setSigningKey(key)
                .build()
                .parseClaimsJws(token)
                .getBody();
        return claims.getExpiration();
    }
}
```

### AuthController - Handle Login Requests

```java
package com.grocerystore.billing.controller;

import com.grocerystore.billing.dto.LoginRequestDTO;
import com.grocerystore.billing.dto.LoginResponseDTO;
import com.grocerystore.billing.entity.User;
import com.grocerystore.billing.response.ApiResponse;
import com.grocerystore.billing.security.JwtTokenProvider;
import com.grocerystore.billing.service.AuthService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * Authentication Controller
 * Handles user login and token generation
 */
@RestController
@RequestMapping("/api/v1/auth")
@RequiredArgsConstructor
@Slf4j
public class AuthController {

    private final AuthService authService;
    private final JwtTokenProvider jwtTokenProvider;

    /**
     * POST /api/v1/auth/login
     * 
     * Login with username and password
     * Returns JWT token on success
     * 
     * @param loginRequest Contains username and password
     * @return JWT token and user details
     */
    @PostMapping("/login")
    public ResponseEntity<ApiResponse<LoginResponseDTO>> login(
            @RequestBody LoginRequestDTO loginRequest) {

        try {
            log.info("Login attempt for user: {}", loginRequest.getUsername());

            // Validate username and password against database
            User user = authService.authenticateUser(
                    loginRequest.getUsername(),
                    loginRequest.getPassword()
            );

            // Check if user is active
            if (!user.isActive()) {
                log.warn("Login attempt for inactive user: {}", user.getUsername());
                return ResponseEntity
                        .status(HttpStatus.UNAUTHORIZED)
                        .body(new ApiResponse<>(
                                false,
                                "User account is inactive",
                                null
                        ));
            }

            // Generate JWT token
            String token = jwtTokenProvider.generateToken(
                    user.getUsername(),
                    user.getId(),
                    user.getRole().name()
            );

            // Create response
            LoginResponseDTO response = new LoginResponseDTO(
                    token,
                    user.getId(),
                    user.getUsername(),
                    user.getRole().name(),
                    user.getEmail()
            );

            log.info("User {} logged in successfully", user.getUsername());

            return ResponseEntity.ok(new ApiResponse<>(
                    true,
                    "Login successful",
                    response
            ));

        } catch (IllegalArgumentException e) {
            // Invalid credentials
            log.warn("Invalid credentials for user: {}", loginRequest.getUsername());
            return ResponseEntity
                    .status(HttpStatus.UNAUTHORIZED)
                    .body(new ApiResponse<>(
                            false,
                            "Invalid username or password",
                            null
                    ));
        } catch (Exception e) {
            log.error("Login error", e);
            return ResponseEntity
                    .status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(new ApiResponse<>(
                            false,
                            "Login failed. Please try again.",
                            null
                    ));
        }
    }

    /**
     * POST /api/v1/auth/verify
     * 
     * Verify if a token is valid
     * 
     * @param token JWT token to verify
     * @return Verification result
     */
    @PostMapping("/verify")
    public ResponseEntity<ApiResponse<Boolean>> verifyToken(
            @RequestHeader("Authorization") String token) {

        try {
            // Extract token from "Bearer {token}" format
            String jwtToken = token.replace("Bearer ", "");

            // Validate token
            boolean isValid = jwtTokenProvider.validateToken(jwtToken);

            return ResponseEntity.ok(new ApiResponse<>(
                    true,
                    "Token verification completed",
                    isValid
            ));

        } catch (Exception e) {
            return ResponseEntity.ok(new ApiResponse<>(
                    true,
                    "Token is invalid",
                    false
            ));
        }
    }

    /**
     * POST /api/v1/auth/logout
     * 
     * Logout user (token invalidation on client side)
     * Note: JWT is stateless, so logout is primarily client-side
     */
    @PostMapping("/logout")
    public ResponseEntity<ApiResponse<String>> logout() {
        log.info("User logged out");
        return ResponseEntity.ok(new ApiResponse<>(
                true,
                "Logout successful. Please delete token from client.",
                null
        ));
    }
}
```

### AuthService - Authentication Logic

```java
package com.grocerystore.billing.service;

import com.grocerystore.billing.entity.User;
import com.grocerystore.billing.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

/**
 * Authentication Service
 * Handles user authentication logic
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    /**
     * Authenticate user with username and password
     * 
     * @param username User's username
     * @param password User's password (plain text)
     * @return Authenticated user
     * @throws IllegalArgumentException if credentials are invalid
     */
    public User authenticateUser(String username, String password) {
        log.debug("Authenticating user: {}", username);

        // Step 1: Find user by username
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> {
                    log.warn("User not found: {}", username);
                    return new IllegalArgumentException("User not found");
                });

        // Step 2: Verify password
        // Password is stored as BCrypt hash in database
        // We compare plain password with hash
        if (!passwordEncoder.matches(password, user.getPassword())) {
            log.warn("Invalid password for user: {}", username);
            throw new IllegalArgumentException("Invalid password");
        }

        // Step 3: User authenticated successfully
        log.info("User authenticated successfully: {}", username);
        return user;
    }
}
```

### JwtAuthenticationFilter - Validate Token in Requests

```java
package com.grocerystore.billing.filter;

import com.grocerystore.billing.security.JwtTokenProvider;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.util.StringUtils;
import org.springframework.web.filter.OncePerRequestFilter;

import javax.servlet.FilterChain;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.ArrayList;

/**
 * JWT Authentication Filter
 * Validates JWT token in every request
 * Runs once per request
 */
@RequiredArgsConstructor
@Slf4j
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private final JwtTokenProvider tokenProvider;

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response,
                                    FilterChain filterChain) throws ServletException, IOException {
        try {
            // Extract JWT token from Authorization header
            String jwt = extractJwtFromRequest(request);

            // If token exists and is valid
            if (StringUtils.hasText(jwt) && tokenProvider.validateToken(jwt)) {
                // Extract user information from token
                String username = tokenProvider.getUsernameFromToken(jwt);
                Long userId = tokenProvider.getUserIdFromToken(jwt);
                String role = tokenProvider.getRoleFromToken(jwt);

                // Create authentication token
                UsernamePasswordAuthenticationToken authentication =
                        new UsernamePasswordAuthenticationToken(
                                username,
                                null,
                                new ArrayList<>()  // Authorities can be populated here
                        );

                authentication.setDetails(
                        new WebAuthenticationDetailsSource().buildDetails(request)
                );

                // Set authentication in security context
                SecurityContextHolder.getContext().setAuthentication(authentication);

                log.debug("JWT token validated for user: {}", username);
            }
        } catch (Exception ex) {
            log.error("Could not set user authentication in security context", ex);
        }

        // Continue with filter chain
        filterChain.doFilter(request, response);
    }

    /**
     * Extract JWT token from Authorization header
     * Expected format: "Bearer {token}"
     * 
     * @param request HTTP request
     * @return JWT token or null if not found
     */
    private String extractJwtFromRequest(HttpServletRequest request) {
        String bearerToken = request.getHeader("Authorization");

        if (StringUtils.hasText(bearerToken) && bearerToken.startsWith("Bearer ")) {
            return bearerToken.substring(7);  // Remove "Bearer " prefix
        }

        return null;
    }
}
```

### DTO Classes

```java
// LoginRequestDTO - Login form data
package com.grocerystore.billing.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class LoginRequestDTO {
    private String username;      // User's username
    private String password;      // User's password
    private boolean rememberMe;   // Remember me flag (optional)
}

// LoginResponseDTO - Response after successful login
package com.grocerystore.billing.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class LoginResponseDTO {
    private String token;         // JWT Token
    private Long userId;          // User's ID
    private String username;      // User's username
    private String role;          // User's role
    private String email;         // User's email
}
```

---

## 🐍 Part 3: Django Frontend Authentication

### Django View - Handle Login

```python
# apps/auth/views.py

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
import json
import logging

from apps.core.api_client import api_client

logger = logging.getLogger(__name__)

@require_http_methods(["GET", "POST"])
@csrf_protect
def login_view(request):
    """
    Handle user login
    GET: Display login form
    POST: Process login credentials
    """
    
    if request.method == 'GET':
        # If user is already logged in, redirect to dashboard
        if request.session.get('token'):
            return redirect('dashboard:index')
        
        # Display login page
        return render(request, 'auth/login.html')
    
    # POST: Process login
    if request.method == 'POST':
        try:
            # Get JSON data from request
            data = json.loads(request.body)
            username = data.get('username', '').strip()
            password = data.get('password', '')
            
            # Validate inputs
            if not username or not password:
                return JsonResponse({
                    'success': False,
                    'message': 'Username and password are required'
                }, status=400)
            
            # Call Java backend API to authenticate
            login_response = api_client.login(username, password)
            
            # Check if login was successful
            if login_response and login_response.get('success'):
                data = login_response.get('data', {})
                token = data.get('token')
                user_id = data.get('userId')
                user_role = data.get('role')
                
                # Store token and user info in Django session
                request.session['token'] = token
                request.session['user_id'] = user_id
                request.session['username'] = data.get('username')
                request.session['user_role'] = user_role
                request.session['user_email'] = data.get('email')
                
                # Set session expiration (24 hours)
                request.session.set_expiry(86400)
                
                logger.info(f"User {username} logged in successfully")
                
                return JsonResponse({
                    'success': True,
                    'message': 'Login successful',
                    'redirect': '/dashboard/'
                }, status=200)
            else:
                # Authentication failed
                logger.warning(f"Failed login attempt for user: {username}")
                return JsonResponse({
                    'success': False,
                    'message': login_response.get('message', 'Invalid credentials')
                }, status=401)
        
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'Login failed. Please try again.'
            }, status=500)


@require_http_methods(["POST"])
def logout_view(request):
    """
    Handle user logout
    Clears session data
    """
    
    # Get username for logging
    username = request.session.get('username', 'unknown')
    
    # Clear session
    request.session.flush()
    
    logger.info(f"User {username} logged out")
    
    # Redirect to login page
    return redirect('auth:login')
```

### API Client - Login Method

```python
# apps/core/api_client.py (relevant portion)

import requests
import json
import logging

logger = logging.getLogger(__name__)

class APIClient:
    """
    REST API Client for communicating with Java backend
    """
    
    def __init__(self, base_url, timeout=10):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
    
    def login(self, username, password):
        """
        Authenticate user and get JWT token
        
        POST /api/v1/auth/login
        
        Request body:
        {
            "username": "admin",
            "password": "admin123"
        }
        
        Response:
        {
            "success": true,
            "message": "Login successful",
            "data": {
                "token": "eyJhbGciOiJIUzI1NiIs...",
                "userId": 1,
                "username": "admin",
                "role": "ADMIN",
                "email": "admin@grocery.com"
            }
        }
        
        Args:
            username: User's username
            password: User's password (plain text)
        
        Returns:
            dict: Response containing token and user info
        """
        
        endpoint = '/auth/login'
        payload = {
            'username': username,
            'password': password
        }
        
        logger.info(f"Login attempt for user: {username}")
        
        return self._make_request(
            method='POST',
            endpoint=endpoint,
            data=payload,
            token=None  # No token needed for login
        )
    
    def verify_token(self, token):
        """
        Verify if JWT token is valid
        
        POST /api/v1/auth/verify
        
        Args:
            token: JWT token to verify
        
        Returns:
            dict: Verification result
        """
        
        endpoint = '/auth/verify'
        
        return self._make_request(
            method='POST',
            endpoint=endpoint,
            token=token
        )
    
    def _make_request(self, method, endpoint, token=None, data=None, params=None):
        """
        Make HTTP request to backend API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            token: JWT token for authorization
            data: Request body (for POST/PUT)
            params: Query parameters (for GET)
        
        Returns:
            dict: Parsed JSON response or error
        """
        
        url = f"{self.base_url}/api/v1{endpoint}"
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Add JWT token to Authorization header
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        try:
            if method == 'GET':
                response = self.session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=self.timeout
                )
            elif method == 'POST':
                response = self.session.post(
                    url,
                    json=data,
                    headers=headers,
                    timeout=self.timeout
                )
            elif method == 'PUT':
                response = self.session.put(
                    url,
                    json=data,
                    headers=headers,
                    timeout=self.timeout
                )
            elif method == 'DELETE':
                response = self.session.delete(
                    url,
                    headers=headers,
                    timeout=self.timeout
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Parse response
            result = response.json()
            
            # Log response
            if response.status_code >= 400:
                logger.error(f"API Error: {response.status_code} - {result}")
            
            return result
        
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout: {url}")
            return {
                'success': False,
                'message': 'Request timeout. Please try again.'
            }
        
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error: {url}")
            return {
                'success': False,
                'message': 'Cannot connect to server. Please check backend service.'
            }
        
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON response from: {url}")
            return {
                'success': False,
                'message': 'Invalid response from server.'
            }
        
        except Exception as e:
            logger.error(f"API request error: {str(e)}")
            return {
                'success': False,
                'message': 'An error occurred. Please try again.'
            }

# Global instance
api_client = APIClient(
    base_url='http://localhost:8080',
    timeout=10
)
```

### Django Decorator - Verify Token in Requests

```python
# apps/core/decorators.py

from django.shortcuts import redirect
from django.http import JsonResponse
from functools import wraps
import logging

from apps.core.api_client import api_client

logger = logging.getLogger(__name__)

def login_required_custom(view_func):
    """
    Custom login required decorator
    Checks if user has valid token in session
    """
    
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if token exists in session
        token = request.session.get('token')
        
        if not token:
            logger.warning("Access attempt without token")
            return redirect('auth:login')
        
        # Optional: Verify token with backend
        # Uncomment if you want to verify token freshness
        # verification = api_client.verify_token(token)
        # if not verification.get('data', False):
        #     logger.warning("Token verification failed")
        #     request.session.flush()
        #     return redirect('auth:login')
        
        # Store token in request for use in view
        request.token = token
        request.user_id = request.session.get('user_id')
        request.user_role = request.session.get('user_role')
        request.username = request.session.get('username')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def role_required(*roles):
    """
    Check if user has required role
    
    Usage:
    @role_required('ADMIN', 'MANAGER')
    def my_view(request):
        ...
    """
    
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user_role = request.session.get('user_role')
            
            if not user_role or user_role not in roles:
                logger.warning(f"Unauthorized access attempt. User role: {user_role}, Required: {roles}")
                return JsonResponse({
                    'success': False,
                    'message': 'Unauthorized access'
                }, status=403)
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    
    return decorator
```

### Django Session Configuration

```python
# config/settings.py (relevant session configuration)

# Session Configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Store in database
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
CSRF_COOKIE_SECURE = False  # Set to True in production
CSRF_COOKIE_HTTPONLY = True
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://localhost:8080',
    'https://yourdomain.com'  # Add your domain
]
```

---

## 🔄 Part 4: Complete Authentication Flow (Step-by-Step)

### Step 1: User Enters Credentials
```
User opens browser → http://localhost:8000/auth/login/
User sees login form
User enters username: "admin" and password: "admin123"
User clicks "Sign In" button
```

### Step 2: Frontend Sends Request to Django
```javascript
// client-side JavaScript
fetch('/auth/login/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
        username: 'admin',
        password: 'admin123'
    })
})
```

### Step 3: Django Processes Login (views.py)
```python
# Django receives the request
username = 'admin'
password = 'admin123'

# Call Java backend to authenticate
login_response = api_client.login(username, password)
# Returns: {
#     "success": true,
#     "message": "Login successful",
#     "data": {
#         "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#         "userId": 1,
#         "username": "admin",
#         "role": "ADMIN"
#     }
# }
```

### Step 4: Java Backend Authenticates User
```java
// AuthController receives login request
@PostMapping("/auth/login")
public ResponseEntity<ApiResponse<LoginResponseDTO>> login(
        @RequestBody LoginRequestDTO loginRequest) {
    
    // Step 1: Find user in database
    User user = userRepository.findByUsername("admin");
    
    // Step 2: Verify password with BCrypt
    boolean passwordMatch = passwordEncoder.matches(
        "admin123",
        user.getPassword()  // stored as: $2a$10$xxxxxx...
    );
    
    if (passwordMatch) {
        // Step 3: Generate JWT token
        String token = jwtTokenProvider.generateToken(
            "admin",
            1L,
            "ADMIN"
        );
        
        // Token structure (3 parts separated by dots):
        // eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9     (Header)
        // .eyJzdWIiOiJhZG1pbiIsImFkbWluIjoic2...   (Payload/Claims)
        // .SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQ   (Signature)
        
        // Step 4: Return token to Django
        return ResponseEntity.ok(new ApiResponse<>(
            true,
            "Login successful",
            new LoginResponseDTO(token, 1L, "admin", "ADMIN", "admin@grocery.com")
        ));
    }
}
```

### Step 5: Django Stores Token in Session
```python
# After receiving token from Java backend
token = login_response['data']['token']

# Store in Django session (server-side)
request.session['token'] = token
request.session['user_id'] = 1
request.session['username'] = 'admin'
request.session['user_role'] = 'ADMIN'
request.session.set_expiry(86400)  # 24 hours

# Django creates session cookie in browser
# Cookie name: sessionid
# Cookie value: random session ID that maps to server-side session data
```

### Step 6: Browser Receives Session Cookie
```
Response Headers:
Set-Cookie: sessionid=a1b2c3d4e5f6...; Path=/; HttpOnly; SameSite=Lax
```

### Step 7: User Redirected to Dashboard
```javascript
// JavaScript redirects user
window.location.href = '/dashboard/';
```

### Step 8: Subsequent API Calls with Token
```python
# When user browses products
@login_required_custom
def product_list(request):
    # Token is available in request.token
    # API client uses it for all requests
    
    products = api_client.get_products(request.token)
    # Sends request with Authorization header:
    # Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Step 9: Java Backend Verifies Token
```java
// JwtAuthenticationFilter intercepts request
String token = "eyJhbGciOiJIUzI1NiIs...";

// Validate token signature
boolean isValid = jwtTokenProvider.validateToken(token);

// Extract user information
String username = jwtTokenProvider.getUsernameFromToken(token);
Long userId = jwtTokenProvider.getUserIdFromToken(token);
String role = jwtTokenProvider.getRoleFromToken(token);

// If valid, process request
// If invalid, return 401 Unauthorized
```

### Step 10: User Logout
```python
# User clicks logout button
@require_http_methods(["POST"])
def logout_view(request):
    # Clear session on server
    request.session.flush()
    
    # Return to login page
    return redirect('auth:login')
```

---

## 🛡️ Security Measures

### 1. **Password Security**
- Passwords are hashed using BCrypt (one-way encryption)
- Never stored in plain text
- Comparison is done using `passwordEncoder.matches()`

### 2. **JWT Token Security**
- Signed with secret key (HMAC SHA-256)
- Cannot be forged without the secret key
- Contains expiration time (24 hours)
- Token signature is validated on every request

### 3. **Session Security**
- Django session ID is stored server-side
- Browser only stores session cookie (not the token)
- HttpOnly flag prevents JavaScript access
- SameSite=Lax prevents CSRF attacks

### 4. **CSRF Protection**
- CSRF token is required for POST requests
- Django validates X-CSRFToken header
- Tokens are unique per session

### 5. **HTTPS (Production)**
- All communication should be over HTTPS
- Set SESSION_COOKIE_SECURE = True
- Set CSRF_COOKIE_SECURE = True

### 6. **Token Expiration**
- JWT expires in 24 hours
- User must login again after expiration
- Server-side session also expires

### 7. **Input Validation**
- Username and password are validated
- Inputs are checked for empty values
- Password length is enforced

### 8. **Logging & Monitoring**
- All login attempts are logged
- Failed login attempts are recorded
- Unauthorized access attempts are logged

---

## 📝 Example API Requests

### Login Request (from Django)
```bash
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

### Response
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJJZCI6MSwicm9sZSI6IkFETUlOIiwiaWF0IjoxNjczMDAwMDAwLCJleHAiOjE2NzMwODYwMDB9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
    "userId": 1,
    "username": "admin",
    "role": "ADMIN",
    "email": "admin@grocery.com"
  }
}
```

### Authenticated Request (with Token)
```bash
curl -X GET http://localhost:8080/api/v1/products \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Verify Token Request
```bash
curl -X POST http://localhost:8080/api/v1/auth/verify \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## 🔑 JWT Token Structure

JWT tokens have 3 parts separated by dots (`.`):

### Header
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```
Specifies algorithm (HMAC SHA-256) and token type

### Payload (Claims)
```json
{
  "sub": "admin",
  "userId": 1,
  "role": "ADMIN",
  "iat": 1673000000,
  "exp": 1673086400
}
```
- `sub` (subject): username
- `userId`: unique user ID
- `role`: user's role
- `iat` (issued at): token creation time
- `exp` (expiration): when token expires

### Signature
```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  "your-secret-key"
)
```
Ensures token hasn't been tampered with

---

## 📋 Configuration

### application.properties (Java)
```properties
# JWT Configuration
app.jwt.secret=your-secret-key-must-be-at-least-32-characters-long-for-HS256
app.jwt.expiration=86400000  # 24 hours in milliseconds

# Database
spring.datasource.url=jdbc:mysql://localhost:3306/grocery_billing
spring.datasource.username=root
spring.datasource.password=password

# Security
spring.security.filter.order=5
server.port=8080
```

### settings.py (Django)
```python
# Session Configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# API Configuration
BACKEND_API_URL = 'http://localhost:8080'
BACKEND_API_TIMEOUT = 10

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:8080',
]
```

---

## ✅ Testing Authentication

### Test Users
```
Admin:
  Username: admin
  Password: admin123
  Role: ADMIN

Cashier:
  Username: cashier1
  Password: cashier123
  Role: CASHIER

Manager:
  Username: manager1
  Password: manager123
  Role: INVENTORY_MANAGER
```

### Test Scenarios
1. ✅ Login with valid credentials
2. ✅ Login with invalid password
3. ✅ Login with non-existent user
4. ✅ Access dashboard with valid token
5. ✅ Access dashboard without token (redirect to login)
6. ✅ Logout and verify session is cleared
7. ✅ Token expiration after 24 hours
8. ✅ Access denied for role without permission

---

## 🎯 Summary

| Component | Responsibility |
|-----------|-----------------|
| **Login UI** | Collect username/password from user |
| **Django View** | Receive credentials, call Java API |
| **API Client** | Make HTTP request to Java backend |
| **Java AuthController** | Verify credentials, return JWT token |
| **JwtTokenProvider** | Generate and validate JWT tokens |
| **Django Session** | Store token and user info server-side |
| **JwtAuthenticationFilter** | Validate token in subsequent requests |
| **Decorators** | Enforce authentication/authorization |

The system is **stateless on Java backend** (JWT) and **stateful on Django** (sessions), providing both security and scalability! 🚀
