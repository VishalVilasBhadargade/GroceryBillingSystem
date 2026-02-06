# Grocery Store Billing Software - REST API Specification

**Document Version:** 1.0  
**Date:** January 21, 2026  
**Framework:** Java Spring Boot 3.x  
**API Version:** v1  
**Base URL:** `http://localhost:8080/api/v1`  
**Content Type:** `application/json`  
**Authentication:** JWT Bearer Token

---

## Executive Summary

This document defines all REST API endpoints for the Grocery Store Billing Software, including request/response formats, authentication, error handling, and usage examples for Java Spring Boot implementation.

---

## 1. API Overview

### 1.1 API Architecture

```
┌─────────────────────────────────────────────┐
│ HTTP Request                                │
│ GET /api/v1/products/barcode/5901234123457 │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│ Spring Boot API Gateway                     │
│ - Route to appropriate controller           │
│ - Validate JWT token                        │
│ - Apply CORS headers                        │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│ Controller Layer                            │
│ ProductController.getProductByBarcode()     │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│ Service Layer                               │
│ ProductService.getProductByBarcode()        │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│ Repository Layer                            │
│ ProductRepository.findByBarcode()           │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│ Database                                    │
│ SELECT * FROM products WHERE barcode = ?   │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│ JSON Response                               │
│ {                                           │
│   "productId": 1,                           │
│   "barcode": "5901234123457",               │
│   "name": "Organic Spinach",                │
│   "price": 3.99                             │
│ }                                           │
└─────────────────────────────────────────────┘
```

### 1.2 Global API Features

```
Authentication:     JWT Bearer Token required (except login endpoint)
Rate Limiting:      100 requests per minute per user
Pagination:         limit=10, offset=0 parameters
Sorting:            sort=name:asc, sort=price:desc
Filtering:          category=1, is_active=true
Response Format:    JSON with standardized envelope
Error Handling:     HTTP status codes + error messages
Timestamps:         ISO 8601 format (2026-01-21T14:30:00Z)
Versioning:         API version in URL (/api/v1)
```

### 1.3 HTTP Status Codes

| Code | Meaning | Scenario |
|------|---------|----------|
| 200 | OK | Successful GET/PUT request |
| 201 | Created | Successful POST request (resource created) |
| 204 | No Content | Successful DELETE request |
| 400 | Bad Request | Invalid input parameters |
| 401 | Unauthorized | Missing or invalid JWT token |
| 403 | Forbidden | Insufficient permissions for action |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Duplicate unique field (SKU, barcode, email) |
| 422 | Unprocessable Entity | Validation error in request body |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side error |
| 503 | Service Unavailable | Database or external service down |

---

## 2. Authentication Endpoints

### 2.1 User Login

**Purpose:** Authenticate user and obtain JWT token

**Endpoint:** `POST /api/v1/auth/login`

**HTTP Method:** POST

**Authentication:** None (Public endpoint)

**Request Body:**
```json
{
  "username": "cashier_mary",
  "password": "secure_password_123"
}
```

**Request Validation:**
```
- username: required, string, 3-50 characters
- password: required, string, 8-100 characters
```

**Success Response (200 OK):**
```json
{
  "status": "SUCCESS",
  "message": "Login successful",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwicm9sZSI6IkNBU0hJRVIiLCJleHAiOjE2MzczODk2MDAsImlhdCI6MTYzNzM4NjAwMH0.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ",
    "expiresIn": 3600,
    "user": {
      "userId": 3,
      "username": "cashier_mary",
      "email": "mary@grocerystore.com",
      "firstName": "Mary",
      "lastName": "Smith",
      "role": "CASHIER"
    }
  }
}
```

**Error Response (401 Unauthorized):**
```json
{
  "status": "ERROR",
  "message": "Invalid credentials",
  "error": {
    "code": "AUTH_001",
    "details": "Username or password is incorrect"
  }
}
```

**Error Response (422 Validation Error):**
```json
{
  "status": "ERROR",
  "message": "Validation failed",
  "error": {
    "code": "VALIDATION_001",
    "details": {
      "username": "Username is required",
      "password": "Password must be at least 8 characters"
    }
  }
}
```

**Spring Boot Controller Implementation:**
```java
@RestController
@RequestMapping("/api/v1/auth")
public class AuthController {
    
    @PostMapping("/login")
    public ResponseEntity<?> login(@Valid @RequestBody LoginRequest loginRequest) {
        try {
            User user = authenticationService.authenticate(
                loginRequest.getUsername(), 
                loginRequest.getPassword()
            );
            
            String token = jwtTokenProvider.generateToken(user);
            
            LoginResponse response = LoginResponse.builder()
                .token(token)
                .expiresIn(3600)
                .user(UserDTO.fromEntity(user))
                .build();
            
            return ResponseEntity.ok(ApiResponse.success(response));
        } catch (AuthenticationException e) {
            return ResponseEntity.status(401)
                .body(ApiResponse.error("AUTH_001", "Invalid credentials"));
        }
    }
}
```

---

### 2.2 User Logout

**Endpoint:** `POST /api/v1/auth/logout`

**HTTP Method:** POST

**Authentication:** Required (JWT Bearer token)

**Request Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Request Body:** Empty (no body required)

**Success Response (200 OK):**
```json
{
  "status": "SUCCESS",
  "message": "Logout successful",
  "data": {
    "message": "Token invalidated"
  }
}
```

**Spring Boot Implementation:**
```java
@PostMapping("/logout")
@PreAuthorize("isAuthenticated()")
public ResponseEntity<?> logout(@RequestHeader("Authorization") String token) {
    try {
        // Invalidate token (add to blacklist in cache)
        tokenBlacklistService.addToBlacklist(token);
        
        return ResponseEntity.ok(ApiResponse.success(
            "Logout successful"
        ));
    } catch (Exception e) {
        return ResponseEntity.status(500)
            .body(ApiResponse.error("SYSTEM_001", "Logout failed"));
    }
}
```

---

### 2.3 Refresh JWT Token

**Endpoint:** `POST /api/v1/auth/refresh-token`

**HTTP Method:** POST

**Authentication:** Required (Refresh token)

**Request Body:**
```json
{
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Success Response (200 OK):**
```json
{
  "status": "SUCCESS",
  "message": "Token refreshed",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwicm9sZSI6IkNBU0hJRVIiLCJleHAiOjE2MzczODk2MDAsImlhdCI6MTYzNzM4NjAwMH0...",
    "expiresIn": 3600
  }
}
```

**Spring Boot Implementation:**
```java
@PostMapping("/refresh-token")
public ResponseEntity<?> refreshToken(
        @Valid @RequestBody RefreshTokenRequest request) {
    try {
        String newToken = jwtTokenProvider.refreshToken(
            request.getRefreshToken()
        );
        
        return ResponseEntity.ok(ApiResponse.success(
            new TokenResponse(newToken, 3600)
        ));
    } catch (InvalidTokenException e) {
        return ResponseEntity.status(401)
            .body(ApiResponse.error("AUTH_002", "Invalid refresh token"));
    }
}
```

---

## 3. Product Management Endpoints

### 3.1 Get All Products

**Endpoint:** `GET /api/v1/products`

**HTTP Method:** GET

**Authentication:** Required

**Query Parameters:**
```
- limit: number of results (default: 10, max: 100)
- offset: pagination offset (default: 0)
- sort: sort field and order (default: name:asc)
- category: filter by category ID
- is_active: filter by active status (true/false)
- search: full-text search in name and description
```

**Example Request:**
```
GET /api/v1/products?limit=20&offset=0&category=3&sort=price:asc&is_active=true
```

**Success Response (200 OK):**
```json
{
  "status": "SUCCESS",
  "message": "Products retrieved successfully",
  "data": {
    "items": [
      {
        "productId": 1,
        "sku": "SKU-001",
        "barcode": "5901234123457",
        "name": "Organic Spinach",
        "description": "Fresh organic spinach - 200g bag",
        "category": {
          "categoryId": 3,
          "name": "Leafy Greens"
        },
        "supplier": {
          "supplierId": 1,
          "name": "Fresh Produce Inc"
        },
        "price": 3.99,
        "costPrice": 1.50,
        "quantityOnHand": 50,
        "reorderLevel": 20,
        "expiryDate": "2026-02-15",
        "isActive": true,
        "createdAt": "2026-01-15T10:30:00Z",
        "updatedAt": "2026-01-21T14:30:00Z"
      },
      {
        "productId": 2,
        "sku": "SKU-002",
        "barcode": "5901234123458",
        "name": "Carrots",
        "description": "Fresh carrots - 1 kg",
        "category": {
          "categoryId": 4,
          "name": "Root Vegetables"
        },
        "supplier": {
          "supplierId": 1,
          "name": "Fresh Produce Inc"
        },
        "price": 2.49,
        "costPrice": 0.80,
        "quantityOnHand": 120,
        "reorderLevel": 50,
        "expiryDate": "2026-03-01",
        "isActive": true,
        "createdAt": "2026-01-15T10:30:00Z",
        "updatedAt": "2026-01-21T14:30:00Z"
      }
    ],
    "pagination": {
      "limit": 20,
      "offset": 0,
      "totalCount": 45,
      "totalPages": 3,
      "currentPage": 1,
      "hasNextPage": true,
      "hasPreviousPage": false
    }
  }
}
```

**Spring Boot Controller:**
```java
@GetMapping
@PreAuthorize("hasAnyRole('ADMIN', 'MANAGER', 'CASHIER')")
public ResponseEntity<?> getAllProducts(
        @RequestParam(defaultValue = "10") int limit,
        @RequestParam(defaultValue = "0") int offset,
        @RequestParam(required = false) Integer category,
        @RequestParam(required = false) Boolean isActive,
        @RequestParam(required = false) String search,
        @RequestParam(defaultValue = "name:asc") String sort) {
    
    ProductFilter filter = ProductFilter.builder()
        .categoryId(category)
        .isActive(isActive)
        .searchTerm(search)
        .build();
    
    Page<Product> products = productService.findProducts(
        filter, 
        PageRequest.of(offset / limit, limit, parseSort(sort))
    );
    
    return ResponseEntity.ok(ApiResponse.success(
        new ProductListResponse(
            products.getContent().stream()
                .map(ProductDTO::fromEntity)
                .collect(Collectors.toList()),
            new PaginationInfo(products)
        )
    ));
}
```

---

### 3.2 Get Product by ID

**Endpoint:** `GET /api/v1/products/{productId}`

**HTTP Method:** GET

**Authentication:** Required

**Path Parameters:**
```
- productId: integer (product ID)
```

**Success Response (200 OK):**
```json
{
  "status": "SUCCESS",
  "message": "Product retrieved successfully",
  "data": {
    "productId": 1,
    "sku": "SKU-001",
    "barcode": "5901234123457",
    "name": "Organic Spinach",
    "description": "Fresh organic spinach - 200g bag",
    "category": {
      "categoryId": 3,
      "name": "Leafy Greens"
    },
    "supplier": {
      "supplierId": 1,
      "name": "Fresh Produce Inc",
      "contactPerson": "John Supplier",
      "email": "john@freshproduce.com",
      "phone": "555-1234"
    },
    "price": 3.99,
    "costPrice": 1.50,
    "quantityOnHand": 50,
    "reorderLevel": 20,
    "reorderQuantity": 100,
    "expiryDate": "2026-02-15",
    "unitOfMeasure": "PIECE",
    "isActive": true,
    "createdAt": "2026-01-15T10:30:00Z",
    "updatedAt": "2026-01-21T14:30:00Z"
  }
}
```

**Error Response (404 Not Found):**
```json
{
  "status": "ERROR",
  "message": "Product not found",
  "error": {
    "code": "PRODUCT_001",
    "details": "Product with ID 999 does not exist"
  }
}
```

---

### 3.3 Get Product by Barcode

**Endpoint:** `GET /api/v1/products/barcode/{barcode}`

**HTTP Method:** GET

**Authentication:** Required

**Path Parameters:**
```
- barcode: string (product barcode)
```

**Example Request:**
```
GET /api/v1/products/barcode/5901234123457
```

**Success Response (200 OK):**
```json
{
  "status": "SUCCESS",
  "message": "Product retrieved successfully",
  "data": {
    "productId": 1,
    "sku": "SKU-001",
    "barcode": "5901234123457",
    "name": "Organic Spinach",
    "price": 3.99,
    "quantityOnHand": 50,
    "isActive": true
  }
}
```

**Spring Boot Controller:**
```java
@GetMapping("/barcode/{barcode}")
@PreAuthorize("hasAnyRole('ADMIN', 'MANAGER', 'CASHIER')")
public ResponseEntity<?> getProductByBarcode(
        @PathVariable String barcode) {
    try {
        Product product = productService.getProductByBarcode(barcode);
        return ResponseEntity.ok(ApiResponse.success(
            ProductDTO.fromEntity(product)
        ));
    } catch (ProductNotFoundException e) {
        return ResponseEntity.status(404)
            .body(ApiResponse.error("PRODUCT_001", "Product not found"));
    }
}
```

---

### 3.4 Create Product

**Endpoint:** `POST /api/v1/products`

**HTTP Method:** POST

**Authentication:** Required (ADMIN or MANAGER role)

**Authorization:** `@PreAuthorize("hasAnyRole('ADMIN', 'MANAGER')")`

**Request Body:**
```json
{
  "sku": "SKU-006",
  "barcode": "5901234123462",
  "name": "Greek Yogurt",
  "description": "500g container - Plain Greek yogurt",
  "categoryId": 8,
  "supplierId": 2,
  "price": 5.99,
  "costPrice": 2.75,
  "quantityOnHand": 75,
  "reorderLevel": 25,
  "reorderQuantity": 150,
  "expiryDate": "2026-02-10",
  "unitOfMeasure": "PIECE",
  "isActive": true
}
```

**Request Validation:**
```
- sku: required, string, 3-50 chars, UNIQUE
- barcode: required, string, UNIQUE
- name: required, string, 1-200 chars
- categoryId: required, integer, must exist
- supplierId: required, integer, must exist
- price: required, decimal, > 0
- costPrice: required, decimal, > 0
- quantityOnHand: required, integer, >= 0
- reorderLevel: required, integer, >= 0
```

**Success Response (201 Created):**
```json
{
  "status": "SUCCESS",
  "message": "Product created successfully",
  "data": {
    "productId": 6,
    "sku": "SKU-006",
    "barcode": "5901234123462",
    "name": "Greek Yogurt",
    "description": "500g container - Plain Greek yogurt",
    "categoryId": 8,
    "supplierId": 2,
    "price": 5.99,
    "costPrice": 2.75,
    "quantityOnHand": 75,
    "reorderLevel": 25,
    "reorderQuantity": 150,
    "expiryDate": "2026-02-10",
    "isActive": true,
    "createdAt": "2026-01-21T15:00:00Z",
    "updatedAt": "2026-01-21T15:00:00Z"
  }
}
```

**Error Response (409 Conflict - Duplicate SKU):**
```json
{
  "status": "ERROR",
  "message": "Conflict",
  "error": {
    "code": "PRODUCT_002",
    "details": "SKU 'SKU-006' already exists"
  }
}
```

**Spring Boot Controller:**
```java
@PostMapping
@PreAuthorize("hasAnyRole('ADMIN', 'MANAGER')")
public ResponseEntity<?> createProduct(
        @Valid @RequestBody CreateProductRequest request) {
    try {
        Product product = productService.createProduct(request);
        return ResponseEntity.status(201)
            .body(ApiResponse.success(ProductDTO.fromEntity(product)));
    } catch (DuplicateResourceException e) {
        return ResponseEntity.status(409)
            .body(ApiResponse.error("PRODUCT_002", e.getMessage()));
    }
}
```

---

### 3.5 Update Product

**Endpoint:** `PUT /api/v1/products/{productId}`

**HTTP Method:** PUT

**Authentication:** Required (ADMIN or MANAGER role)

**Path Parameters:**
```
- productId: integer (product ID)
```

**Request Body:**
```json
{
  "name": "Organic Spinach (Updated)",
  "price": 4.29,
  "quantityOnHand": 45,
  "reorderLevel": 20,
  "isActive": true
}
```

**Success Response (200 OK):**
```json
{
  "status": "SUCCESS",
  "message": "Product updated successfully",
  "data": {
    "productId": 1,
    "sku": "SKU-001",
    "barcode": "5901234123457",
    "name": "Organic Spinach (Updated)",
    "price": 4.29,
    "quantityOnHand": 45,
    "updatedAt": "2026-01-21T15:30:00Z"
  }
}
```

**Spring Boot Controller:**
```java
@PutMapping("/{productId}")
@PreAuthorize("hasAnyRole('ADMIN', 'MANAGER')")
public ResponseEntity<?> updateProduct(
        @PathVariable Integer productId,
        @Valid @RequestBody UpdateProductRequest request) {
    try {
        Product product = productService.updateProduct(productId, request);
        return ResponseEntity.ok(ApiResponse.success(
            ProductDTO.fromEntity(product)
        ));
    } catch (ProductNotFoundException e) {
        return ResponseEntity.status(404)
            .body(ApiResponse.error("PRODUCT_001", "Product not found"));
    }
}
```

---

### 3.6 Delete Product

**Endpoint:** `DELETE /api/v1/products/{productId}`

**HTTP Method:** DELETE

**Authentication:** Required (ADMIN role only)

**Path Parameters:**
```
- productId: integer (product ID)
```

**Success Response (204 No Content):**
```
(Empty body, HTTP 204)
```

**Spring Boot Controller:**
```java
@DeleteMapping("/{productId}")
@PreAuthorize("hasRole('ADMIN')")
public ResponseEntity<?> deleteProduct(@PathVariable Integer productId) {
    try {
        productService.deleteProduct(productId);
        return ResponseEntity.noContent().build();
    } catch (ProductNotFoundException e) {
        return ResponseEntity.status(404)
            .body(ApiResponse.error("PRODUCT_001", "Product not found"));
    }
}
```

---

## 4. Customer Management Endpoints

### 4.1 Get All Customers

**Endpoint:** `GET /api/v1/customers`

**HTTP Method:** GET

**Authentication:** Required

**Query Parameters:**
```
- limit: number of results (default: 10)
- offset: pagination offset (default: 0)
- search: search by name or phone
- isActive: filter by active status
```

**Example Request:**
```
GET /api/v1/customers?limit=20&offset=0&search=John&isActive=true
```

**Success Response (200 OK):**
```json
{
  "status": "SUCCESS",
  "message": "Customers retrieved successfully",
  "data": {
    "items": [
      {
        "customerId": 1,
        "phone": "555-0001",
        "email": "john.doe@email.com",
        "firstName": "John",
        "lastName": "Doe",
        "address": "123 Main St",
        "city": "Springfield",
        "loyaltyPoints": 150,
        "totalSpent": 450.75,
        "memberSince": "2025-06-15",
        "isActive": true,
        "createdAt": "2025-06-15T10:00:00Z",
        "updatedAt": "2026-01-21T14:30:00Z"
      }
    ],
    "pagination": {
      "totalCount": 25,
      "totalPages": 3,
      "currentPage": 1
    }
  }
}
```

---

### 4.2 Get Customer by ID

**Endpoint:** `GET /api/v1/customers/{customerId}`

**HTTP Method:** GET

**Authentication:** Required

**Path Parameters:**
```
- customerId: integer (customer ID)
```

**Success Response (200 OK):**
```json
{
  "status": "SUCCESS",
  "message": "Customer retrieved successfully",
  "data": {
    "customerId": 1,
    "phone": "555-0001",
    "email": "john.doe@email.com",
    "firstName": "John",
    "lastName": "Doe",
    "address": "123 Main St",
    "city": "Springfield",
    "state": "IL",
    "postalCode": "62701",
    "country": "USA",
    "loyaltyPoints": 150,
    "totalSpent": 450.75,
    "memberSince": "2025-06-15",
    "isActive": true
  }
}
```

---

### 4.3 Create Customer

**Endpoint:** `POST /api/v1/customers`

**HTTP Method:** POST

**Authentication:** Required (CASHIER or higher role)

**Request Body:**
```json
{
  "phone": "555-0005",
  "email": "alice.brown@email.com",
  "firstName": "Alice",
  "lastName": "Brown",
  "address": "321 Pine Rd",
  "city": "Springfield",
  "state": "IL",
  "postalCode": "62701",
  "country": "USA"
}
```

**Request Validation:**
```
- phone: required, string, UNIQUE, 7-20 chars
- email: required, string, UNIQUE, valid email format
- firstName: required, string, 1-100 chars
- lastName: required, string, 1-100 chars
```

**Success Response (201 Created):**
```json
{
  "status": "SUCCESS",
  "message": "Customer created successfully",
  "data": {
    "customerId": 5,
    "phone": "555-0005",
    "email": "alice.brown@email.com",
    "firstName": "Alice",
    "lastName": "Brown",
    "loyaltyPoints": 0,
    "totalSpent": 0.00,
    "memberSince": "2026-01-21T15:00:00Z",
    "isActive": true,
    "createdAt": "2026-01-21T15:00:00Z"
  }
}
```

**Spring Boot Controller:**
```java
@PostMapping
@PreAuthorize("hasAnyRole('CASHIER', 'MANAGER', 'ADMIN')")
public ResponseEntity<?> createCustomer(
        @Valid @RequestBody CreateCustomerRequest request) {
    try {
        Customer customer = customerService.createCustomer(request);
        return ResponseEntity.status(201)
            .body(ApiResponse.success(CustomerDTO.fromEntity(customer)));
    } catch (DuplicateResourceException e) {
        return ResponseEntity.status(409)
            .body(ApiResponse.error("CUSTOMER_001", e.getMessage()));
    }
}
```

---

### 4.4 Update Customer

**Endpoint:** `PUT /api/v1/customers/{customerId}`

**HTTP Method:** PUT

**Authentication:** Required

**Request Body:**
```json
{
  "email": "john.doe.new@email.com",
  "address": "456 Oak Ave",
  "city": "Shelbyville",
  "isActive": true
}
```

**Success Response (200 OK):**
```json
{
  "status": "SUCCESS",
  "message": "Customer updated successfully",
  "data": {
    "customerId": 1,
    "phone": "555-0001",
    "email": "john.doe.new@email.com",
    "firstName": "John",
    "lastName": "Doe",
    "address": "456 Oak Ave",
    "city": "Shelbyville",
    "updatedAt": "2026-01-21T15:30:00Z"
  }
}
```

---

### 4.5 Get Customer Purchase History

**Endpoint:** `GET /api/v1/customers/{customerId}/history`

**HTTP Method:** GET

**Authentication:** Required

**Path Parameters:**
```
- customerId: integer
```

**Query Parameters:**
```
- limit: number of results (default: 10)
- offset: pagination offset
- startDate: filter by date range
- endDate: filter by date range
```

**Success Response (200 OK):**
```json
{
  "status": "SUCCESS",
  "message": "Customer purchase history retrieved",
  "data": {
    "customerId": 1,
    "customerName": "John Doe",
    "totalPurchases": 5,
    "totalSpent": 450.75,
    "purchases": [
      {
        "billId": 1,
        "billNumber": "BIL-2026-001",
        "billDate": "2026-01-21T14:30:00Z",
        "totalAmount": 22.44,
        "itemCount": 3,
        "items": [
          {
            "productName": "Organic Spinach",
            "quantity": 2,
            "unitPrice": 3.99,
            "lineTotal": 7.98
          }
        ]
      }
    ],
    "pagination": {
      "totalCount": 5,
      "totalPages": 1
    }
  }
}
```

**Spring Boot Controller:**
```java
@GetMapping("/{customerId}/history")
@PreAuthorize("hasAnyRole('MANAGER', 'ACCOUNTANT')")
public ResponseEntity<?> getCustomerHistory(
        @PathVariable Integer customerId,
        @RequestParam(defaultValue = "10") int limit,
        @RequestParam(defaultValue = "0") int offset) {
    try {
        List<BillDTO> bills = billService.getCustomerBills(customerId);
        return ResponseEntity.ok(ApiResponse.success(bills));
    } catch (CustomerNotFoundException e) {
        return ResponseEntity.status(404)
            .body(ApiResponse.error("CUSTOMER_002", "Customer not found"));
    }
}
```

---

## 5. Billing (Transactions) Endpoints

### 5.1 Create Bill (Checkout)

**Endpoint:** `POST /api/v1/bills`

**HTTP Method:** POST

**Authentication:** Required (CASHIER or higher)

**Request Body:**
```json
{
  "customerId": null,
  "items": [
    {
      "productId": 1,
      "quantity": 2,
      "unitPrice": 3.99
    },
    {
      "productId": 3,
      "quantity": 1,
      "unitPrice": 4.99
    },
    {
      "productId": 5,
      "quantity": 4,
      "unitPrice": 1.29
    }
  ],
  "discountAmount": 2.00,
  "appliedDiscounts": [
    {
      "type": "COUPON",
      "code": "SAVE10",
      "amount": 2.00
    }
  ]
}
```

**Request Validation:**
```
- customerId: optional, integer
- items: required, array, min 1 item
- items[].productId: required, integer, must exist
- items[].quantity: required, integer, > 0
- items[].unitPrice: required, decimal, > 0
- discountAmount: optional, decimal, >= 0
```

**Success Response (201 Created):**
```json
{
  "status": "SUCCESS",
  "message": "Bill created successfully",
  "data": {
    "billId": 1,
    "billNumber": "BIL-2026-001",
    "cashierId": 3,
    "customerId": null,
    "billDate": "2026-01-21T14:30:00Z",
    "items": [
      {
        "itemId": 1,
        "productId": 1,
        "productName": "Organic Spinach",
        "quantity": 2,
        "unitPrice": 3.99,
        "lineTotal": 7.98,
        "discountApplied": 1.00,
        "finalLineTotal": 6.98
      },
      {
        "itemId": 2,
        "productId": 3,
        "productName": "Whole Milk",
        "quantity": 1,
        "unitPrice": 4.99,
        "lineTotal": 4.99,
        "discountApplied": 0.00,
        "finalLineTotal": 4.99
      },
      {
        "itemId": 3,
        "productId": 5,
        "productName": "Canned Beans",
        "quantity": 4,
        "unitPrice": 1.29,
        "lineTotal": 5.16,
        "discountApplied": 1.00,
        "finalLineTotal": 4.16
      }
    ],
    "subtotal": 22.47,
    "discountAmount": 2.00,
    "taxAmount": 1.97,
    "totalAmount": 22.44,
    "status": "COMPLETED",
    "receiptUrl": "/api/v1/bills/1/receipt"
  }
}
```

**Business Logic:**
```
1. Validate all products exist
2. Check inventory availability
3. Calculate subtotal (sum of all line totals)
4. Apply discounts
5. Calculate tax (based on location or global tax rate)
6. Calculate final total
7. Deduct inventory for each item
8. Create bill record in database
9. Create bill_items records
10. Log transaction to audit trail
11. Update customer total_spent if customer provided
12. Return bill details with receipt URL
```

**Spring Boot Controller:**
```java
@PostMapping
@PreAuthorize("hasAnyRole('CASHIER', 'MANAGER', 'ADMIN')")
public ResponseEntity<?> createBill(
        @Valid @RequestBody CreateBillRequest request,
        @AuthenticationPrincipal UserPrincipal currentUser) {
    try {
        Bill bill = billService.createBill(request, currentUser.getUserId());
        return ResponseEntity.status(201)
            .body(ApiResponse.success(BillDTO.fromEntity(bill)));
    } catch (ProductNotFoundException e) {
        return ResponseEntity.status(404)
            .body(ApiResponse.error("BILL_001", "Product not found"));
    } catch (InsufficientInventoryException e) {
        return ResponseEntity.status(422)
            .body(ApiResponse.error("BILL_002", e.getMessage()));
    }
}
```

---

### 5.2 Get Bill Details

**Endpoint:** `GET /api/v1/bills/{billId}`

**HTTP Method:** GET

**Authentication:** Required

**Path Parameters:**
```
- billId: integer (bill ID)
```

**Success Response (200 OK):**
```json
{
  "status": "SUCCESS",
  "message": "Bill retrieved successfully",
  "data": {
    "billId": 1,
    "billNumber": "BIL-2026-001",
    "cashier": {
      "userId": 3,
      "firstName": "Mary",
      "lastName": "Smith"
    },
    "customer": null,
    "billDate": "2026-01-21T14:30:00Z",
    "items": [
      {
        "itemId": 1,
        "product": {
          "productId": 1,
          "name": "Organic Spinach",
          "barcode": "5901234123457"
        },
        "quantity": 2,
        "unitPrice": 3.99,
        "lineTotal": 7.98,
        "discountApplied": 1.00
      }
    ],
    "subtotal": 22.47,
    "discountAmount": 2.00,
    "taxAmount": 1.97,
    "totalAmount": 22.44,
    "status": "COMPLETED",
    "createdAt": "2026-01-21T14:30:00Z"
  }
}
```

---

### 5.3 Get All Bills (Daily Summary)

**Endpoint:** `GET /api/v1/bills`

**HTTP Method:** GET

**Authentication:** Required

**Query Parameters:**
```
- limit: number of results (default: 10)
- offset: pagination offset
- startDate: filter by date (YYYY-MM-DD)
- endDate: filter by date (YYYY-MM-DD)
- cashierId: filter by cashier
- status: filter by status (COMPLETED, VOIDED, REFUNDED)
```

**Example Request:**
```
GET /api/v1/bills?startDate=2026-01-21&endDate=2026-01-21&status=COMPLETED
```

**Success Response (200 OK):**
```json
{
  "status": "SUCCESS",
  "message": "Bills retrieved successfully",
  "data": {
    "items": [
      {
        "billId": 1,
        "billNumber": "BIL-2026-001",
        "billDate": "2026-01-21T14:30:00Z",
        "cashierName": "Mary Smith",
        "customerName": null,
        "totalAmount": 22.44,
        "itemCount": 3,
        "status": "COMPLETED"
      },
      {
        "billId": 2,
        "billNumber": "BIL-2026-002",
        "billDate": "2026-01-21T14:45:00Z",
        "cashierName": "Bob Johnson",
        "customerName": "Jane Smith",
        "totalAmount": 34.76,
        "itemCount": 2,
        "status": "COMPLETED"
      }
    ],
    "pagination": {
      "totalCount": 87,
      "totalPages": 9,
      "currentPage": 1
    }
  }
}
```

---

### 5.4 Void Bill

**Endpoint:** `POST /api/v1/bills/{billId}/void`

**HTTP Method:** POST

**Authentication:** Required (MANAGER or ADMIN role)

**Authorization:** Only managers can void bills

**Path Parameters:**
```
- billId: integer
```

**Request Body:**
```json
{
  "reason": "Customer requested cancellation - wrong item scanned"
}
```

**Success Response (200 OK):**
```json
{
  "status": "SUCCESS",
  "message": "Bill voided successfully",
  "data": {
    "billId": 4,
    "billNumber": "BIL-2026-004",
    "status": "VOIDED",
    "voidDate": "2026-01-21T15:15:00Z",
    "voidReason": "Customer requested cancellation - wrong item scanned",
    "inventoryRestored": true
  }
}
```

**Business Logic:**
```
1. Check user has MANAGER role
2. Verify bill exists and status is COMPLETED
3. Restore inventory for all items in bill
4. Update bill status to VOIDED
5. Record void_date and void_reason
6. Log to audit trail with before/after values
7. Return updated bill details
```

**Spring Boot Controller:**
```java
@PostMapping("/{billId}/void")
@PreAuthorize("hasAnyRole('MANAGER', 'ADMIN')")
public ResponseEntity<?> voidBill(
        @PathVariable Integer billId,
        @Valid @RequestBody VoidBillRequest request,
        @AuthenticationPrincipal UserPrincipal currentUser) {
    try {
        Bill bill = billService.voidBill(billId, request.getReason(), currentUser.getUserId());
        return ResponseEntity.ok(ApiResponse.success(BillDTO.fromEntity(bill)));
    } catch (BillNotFoundException e) {
        return ResponseEntity.status(404)
            .body(ApiResponse.error("BILL_003", "Bill not found"));
    } catch (InvalidBillStatusException e) {
        return ResponseEntity.status(422)
            .body(ApiResponse.error("BILL_004", "Cannot void a " + e.getStatus() + " bill"));
    }
}
```

---

### 5.5 Get Receipt

**Endpoint:** `GET /api/v1/bills/{billId}/receipt`

**HTTP Method:** GET

**Authentication:** Required

**Path Parameters:**
```
- billId: integer
```

**Query Parameters:**
```
- format: receipt format (HTML, PDF, TEXT) - default: HTML
```

**Success Response (200 OK - HTML):**
```html
<html>
<head><title>Receipt BIL-2026-001</title></head>
<body>
<pre>
═══════════════════════════════════
    GROCERY STORE BILLING SYSTEM
═══════════════════════════════════

Receipt: BIL-2026-001
Date: 01/21/2026 14:30:00
Cashier: Mary Smith

───────────────────────────────────
Item                    Qty  Price
───────────────────────────────────
Organic Spinach          2   $3.99
Carrots                  1   $2.49
Whole Milk               1   $4.99
───────────────────────────────────
Subtotal:                        $22.47
Discount:                       -$2.00
Tax (8.8%):                      $1.97
═══════════════════════════════════
TOTAL:                          $22.44
═══════════════════════════════════

Thank you for your purchase!
═══════════════════════════════════
</pre>
</body>
</html>
```

**Spring Boot Controller:**
```java
@GetMapping("/{billId}/receipt")
@PreAuthorize("hasAnyRole('CASHIER', 'MANAGER', 'ADMIN')")
public ResponseEntity<?> getReceipt(
        @PathVariable Integer billId,
        @RequestParam(defaultValue = "HTML") ReceiptFormat format) {
    try {
        String receipt = billService.generateReceipt(billId, format);
        
        if (format == ReceiptFormat.PDF) {
            return ResponseEntity.ok()
                .contentType(MediaType.APPLICATION_PDF)
                .body(receipt);
        } else {
            return ResponseEntity.ok()
                .contentType(MediaType.TEXT_HTML)
                .body(receipt);
        }
    } catch (BillNotFoundException e) {
        return ResponseEntity.status(404)
            .body(ApiResponse.error("BILL_003", "Bill not found"));
    }
}
```

---

## 6. Payment Endpoints

### 6.1 Process Payment

**Endpoint:** `POST /api/v1/payments/process`

**HTTP Method:** POST

**Authentication:** Required (CASHIER or higher)

**Request Body:**
```json
{
  "billId": 1,
  "paymentMethod": "CREDIT_CARD",
  "amount": 22.44,
  "cardData": {
    "cardNumber": "4532015112830366",
    "expiryMonth": "12",
    "expiryYear": "2026",
    "cvv": "123",
    "cardHolderName": "John Doe"
  },
  "deviceId": "TERMINAL_001"
}
```

**Important Security Notes:**
```
⚠️  NEVER store full card numbers
⚠️  Only transmit card data over HTTPS with TLS 1.3
⚠️  Use tokenization with payment gateway (Stripe, Square, etc.)
⚠️  PCI-DSS compliance is mandatory
⚠️  Log only last 4 digits of card for audit trail

Example: Only log "Card ending in 0366"
```

**Request Validation:**
```
- billId: required, integer, must exist
- paymentMethod: required, enum (CASH, CREDIT_CARD, DEBIT_CARD, DIGITAL_WALLET, CHECK)
- amount: required, decimal, must match bill total
- For card payments: validate card number, expiry, CVV format
```

**Success Response (200 OK):**
```json
{
  "status": "SUCCESS",
  "message": "Payment processed successfully",
  "data": {
    "paymentId": 1,
    "billId": 1,
    "paymentMethod": "CREDIT_CARD",
    "amount": 22.44,
    "status": "APPROVED",
    "referenceNumber": "TXN-20260121-001",
    "cardBrand": "VISA",
    "cardLastFour": "0366",
    "processedAt": "2026-01-21T14:30:15Z",
    "receipt": {
      "receiptNumber": "RCP-20260121-001",
      "url": "/api/v1/receipts/RCP-20260121-001"
    }
  }
}
```

**Error Response (422 Payment Declined):**
```json
{
  "status": "ERROR",
  "message": "Payment processing failed",
  "error": {
    "code": "PAYMENT_001",
    "details": "Card declined by issuing bank",
    "suggestedAction": "Use another card or payment method"
  }
}
```

**Spring Boot Controller:**
```java
@PostMapping("/process")
@PreAuthorize("hasAnyRole('CASHIER', 'MANAGER', 'ADMIN')")
public ResponseEntity<?> processPayment(
        @Valid @RequestBody ProcessPaymentRequest request) {
    try {
        // Validate bill exists
        Bill bill = billService.getBillById(request.getBillId());
        
        // Validate amount matches bill total
        if (!request.getAmount().equals(bill.getTotalAmount())) {
            return ResponseEntity.status(422)
                .body(ApiResponse.error("PAYMENT_002", 
                    "Payment amount does not match bill total"));
        }
        
        // Process payment through gateway
        PaymentResponse paymentResponse = paymentService.processPayment(request);
        
        // Save payment record
        Payment payment = paymentService.savePayment(
            bill.getBillId(), 
            paymentResponse
        );
        
        return ResponseEntity.ok(ApiResponse.success(
            PaymentDTO.fromEntity(payment)
        ));
        
    } catch (BillNotFoundException e) {
        return ResponseEntity.status(404)
            .body(ApiResponse.error("BILL_003", "Bill not found"));
    } catch (PaymentProcessingException e) {
        return ResponseEntity.status(422)
            .body(ApiResponse.error("PAYMENT_001", e.getMessage()));
    }
}
```

---

### 6.2 Get Payment Status

**Endpoint:** `GET /api/v1/payments/{paymentId}/status`

**HTTP Method:** GET

**Authentication:** Required

**Path Parameters:**
```
- paymentId: integer
```

**Success Response (200 OK):**
```json
{
  "status": "SUCCESS",
  "message": "Payment status retrieved",
  "data": {
    "paymentId": 1,
    "billId": 1,
    "paymentMethod": "CREDIT_CARD",
    "amount": 22.44,
    "status": "APPROVED",
    "referenceNumber": "TXN-20260121-001",
    "cardLastFour": "0366",
    "processedAt": "2026-01-21T14:30:15Z"
  }
}
```

---

### 6.3 Refund Payment

**Endpoint:** `POST /api/v1/payments/{paymentId}/refund`

**HTTP Method:** POST

**Authentication:** Required (MANAGER or ADMIN)

**Authorization:** `@PreAuthorize("hasAnyRole('MANAGER', 'ADMIN')")`

**Path Parameters:**
```
- paymentId: integer
```

**Request Body:**
```json
{
  "amount": 22.44,
  "reason": "Customer returned items",
  "referenceNumber": "BIL-2026-001"
}
```

**Success Response (200 OK):**
```json
{
  "status": "SUCCESS",
  "message": "Refund processed successfully",
  "data": {
    "refundId": 1,
    "originalPaymentId": 1,
    "billId": 1,
    "amount": 22.44,
    "status": "APPROVED",
    "referenceNumber": "REF-20260121-001",
    "reason": "Customer returned items",
    "processedAt": "2026-01-21T15:00:00Z"
  }
}
```

**Spring Boot Controller:**
```java
@PostMapping("/{paymentId}/refund")
@PreAuthorize("hasAnyRole('MANAGER', 'ADMIN')")
public ResponseEntity<?> refundPayment(
        @PathVariable Integer paymentId,
        @Valid @RequestBody RefundPaymentRequest request,
        @AuthenticationPrincipal UserPrincipal currentUser) {
    try {
        Payment payment = paymentService.getPaymentById(paymentId);
        
        Refund refund = paymentService.processRefund(
            paymentId, 
            request.getAmount(), 
            request.getReason(),
            currentUser.getUserId()
        );
        
        return ResponseEntity.ok(ApiResponse.success(
            RefundDTO.fromEntity(refund)
        ));
        
    } catch (PaymentNotFoundException e) {
        return ResponseEntity.status(404)
            .body(ApiResponse.error("PAYMENT_003", "Payment not found"));
    } catch (RefundException e) {
        return ResponseEntity.status(422)
            .body(ApiResponse.error("PAYMENT_004", e.getMessage()));
    }
}
```

---

## 7. Reporting Endpoints

### 7.1 Daily Sales Report

**Endpoint:** `GET /api/v1/reports/daily-sales`

**HTTP Method:** GET

**Authentication:** Required (MANAGER or ACCOUNTANT)

**Query Parameters:**
```
- date: report date (YYYY-MM-DD) - default: today
- format: output format (JSON, PDF, CSV) - default: JSON
```

**Example Request:**
```
GET /api/v1/reports/daily-sales?date=2026-01-21&format=JSON
```

**Success Response (200 OK):**
```json
{
  "status": "SUCCESS",
  "message": "Daily sales report generated",
  "data": {
    "reportDate": "2026-01-21",
    "summary": {
      "transactionCount": 87,
      "totalSales": 5420.50,
      "totalTax": 420.50,
      "totalDiscount": 250.25,
      "averageTransaction": 62.30,
      "totalRefunds": 0.00
    },
    "paymentMethods": {
      "cash": {
        "count": 35,
        "amount": 2100.50
      },
      "creditCard": {
        "count": 45,
        "amount": 3150.00
      },
      "debitCard": {
        "count": 7,
        "amount": 170.00
      }
    },
    "topProducts": [
      {
        "productId": 1,
        "name": "Organic Spinach",
        "quantity": 45,
        "revenue": 179.55
      },
      {
        "productId": 3,
        "name": "Whole Milk",
        "quantity": 38,
        "revenue": 189.62
      }
    ],
    "cashierPerformance": [
      {
        "cashierId": 3,
        "cashierName": "Mary Smith",
        "transactionCount": 35,
        "totalAmount": 2150.00,
        "averageTransaction": 61.43
      },
      {
        "cashierId": 4,
        "cashierName": "Bob Johnson",
        "transactionCount": 52,
        "totalAmount": 3270.50,
        "averageTransaction": 62.89
      }
    ]
  }
}
```

**Spring Boot Controller:**
```java
@GetMapping("/daily-sales")
@PreAuthorize("hasAnyRole('MANAGER', 'ACCOUNTANT', 'ADMIN')")
public ResponseEntity<?> getDailySalesReport(
        @RequestParam(required = false) LocalDate date,
        @RequestParam(defaultValue = "JSON") ReportFormat format) {
    
    if (date == null) {
        date = LocalDate.now();
    }
    
    DailySalesReport report = reportService.generateDailySalesReport(date);
    
    if (format == ReportFormat.PDF) {
        byte[] pdfContent = reportService.convertToPDF(report);
        return ResponseEntity.ok()
            .contentType(MediaType.APPLICATION_PDF)
            .header("Content-Disposition", "attachment; filename=\"report_" + date + ".pdf\"")
            .body(pdfContent);
    } else {
        return ResponseEntity.ok(ApiResponse.success(report));
    }
}
```

---

### 7.2 Category Sales Report

**Endpoint:** `GET /api/v1/reports/category-sales`

**HTTP Method:** GET

**Authentication:** Required

**Query Parameters:**
```
- startDate: start date (YYYY-MM-DD)
- endDate: end date (YYYY-MM-DD)
- format: output format (JSON, PDF, CSV)
```

**Success Response (200 OK):**
```json
{
  "status": "SUCCESS",
  "message": "Category sales report generated",
  "data": {
    "reportPeriod": {
      "startDate": "2026-01-15",
      "endDate": "2026-01-21"
    },
    "totalSales": 12450.75,
    "categories": [
      {
        "categoryId": 1,
        "categoryName": "Produce",
        "transactionCount": 156,
        "totalQuantity": 340,
        "totalRevenue": 4250.50,
        "percentageOfTotal": 34.15,
        "trend": "UP"
      },
      {
        "categoryId": 8,
        "categoryName": "Dairy",
        "transactionCount": 98,
        "totalQuantity": 212,
        "totalRevenue": 2850.75,
        "percentageOfTotal": 22.89,
        "trend": "STABLE"
      }
    ]
  }
}
```

---

### 7.3 Inventory Report

**Endpoint:** `GET /api/v1/reports/inventory`

**HTTP Method:** GET

**Authentication:** Required (INVENTORY_MANAGER, MANAGER, ADMIN)

**Query Parameters:**
```
- lowStockOnly: boolean - show only low stock items
- categoryId: integer - filter by category
- format: output format (JSON, PDF, CSV)
```

**Success Response (200 OK):**
```json
{
  "status": "SUCCESS",
  "message": "Inventory report generated",
  "data": {
    "reportDate": "2026-01-21T15:00:00Z",
    "summary": {
      "totalProducts": 152,
      "lowStockCount": 12,
      "totalValue": 45320.50
    },
    "lowStockProducts": [
      {
        "productId": 7,
        "sku": "SKU-007",
        "name": "Canned Tomato Sauce",
        "quantityOnHand": 15,
        "reorderLevel": 50,
        "reorderQuantity": 200,
        "supplier": "Food Wholesale Inc",
        "status": "CRITICAL"
      },
      {
        "productId": 12,
        "sku": "SKU-012",
        "name": "Olive Oil",
        "quantityOnHand": 8,
        "reorderLevel": 25,
        "reorderQuantity": 100,
        "supplier": "Mediterranean Foods",
        "status": "CRITICAL"
      }
    ]
  }
}
```

---

## 8. Global Response Format

### 8.1 Standard Success Response

```json
{
  "status": "SUCCESS",
  "message": "Operation completed successfully",
  "data": {
    // Actual response data
  },
  "metadata": {
    "timestamp": "2026-01-21T15:00:00Z",
    "requestId": "REQ-20260121-001",
    "version": "1.0"
  }
}
```

### 8.2 Error Response Format

```json
{
  "status": "ERROR",
  "message": "User-friendly error message",
  "error": {
    "code": "ERROR_CODE_001",
    "details": "Detailed error explanation",
    "field": "fieldName",
    "suggestedAction": "What user should do next"
  },
  "metadata": {
    "timestamp": "2026-01-21T15:00:00Z",
    "requestId": "REQ-20260121-001"
  }
}
```

### 8.3 Validation Error Response

```json
{
  "status": "ERROR",
  "message": "Validation failed",
  "error": {
    "code": "VALIDATION_001",
    "details": {
      "productName": "Product name is required",
      "price": "Price must be greater than 0",
      "categoryId": "Category does not exist"
    }
  }
}
```

---

## 9. Error Codes Reference

| Code | HTTP | Meaning | Action |
|------|------|---------|--------|
| AUTH_001 | 401 | Invalid credentials | Check username/password |
| AUTH_002 | 401 | Invalid/expired token | Re-login |
| PRODUCT_001 | 404 | Product not found | Check product ID |
| PRODUCT_002 | 409 | Duplicate SKU/barcode | Use unique identifier |
| BILL_001 | 404 | Product not found in bill | Check product exists |
| BILL_002 | 422 | Insufficient inventory | Reduce quantity or select other item |
| BILL_003 | 404 | Bill not found | Check bill ID |
| BILL_004 | 422 | Invalid bill status | Cannot void/refund non-completed bill |
| PAYMENT_001 | 422 | Payment declined | Retry with different payment method |
| PAYMENT_002 | 422 | Amount mismatch | Amount must equal bill total |
| PAYMENT_003 | 404 | Payment not found | Check payment ID |
| CUSTOMER_001 | 409 | Duplicate phone/email | Customer already exists |
| CUSTOMER_002 | 404 | Customer not found | Check customer ID |
| VALIDATION_001 | 422 | Validation failed | Check field errors |
| RATE_LIMIT_001 | 429 | Too many requests | Wait before retrying |

---

## 10. API Request Examples (cURL)

### 10.1 Login

```bash
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "cashier_mary",
    "password": "secure_password_123"
  }'
```

### 10.2 Get Product by Barcode

```bash
curl -X GET http://localhost:8080/api/v1/products/barcode/5901234123457 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 10.3 Create Bill

```bash
curl -X POST http://localhost:8080/api/v1/bills \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "customerId": null,
    "items": [
      {
        "productId": 1,
        "quantity": 2,
        "unitPrice": 3.99
      }
    ],
    "discountAmount": 0.00
  }'
```

### 10.4 Process Payment

```bash
curl -X POST http://localhost:8080/api/v1/payments/process \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "billId": 1,
    "paymentMethod": "CREDIT_CARD",
    "amount": 22.44,
    "cardData": {
      "cardNumber": "4532015112830366",
      "expiryMonth": "12",
      "expiryYear": "2026",
      "cvv": "123",
      "cardHolderName": "John Doe"
    }
  }'
```

---

## 11. API Security Best Practices

### 11.1 JWT Token Configuration

```java
@Configuration
public class JwtSecurityConfig {
    
    @Value("${jwt.secret}")
    private String jwtSecret;
    
    @Value("${jwt.expiration}")
    private int jwtExpiration; // in seconds (3600 = 1 hour)
    
    public String generateToken(User user) {
        return Jwts.builder()
            .setSubject(user.getUserId().toString())
            .claim("role", user.getRole())
            .claim("username", user.getUsername())
            .setIssuedAt(new Date())
            .setExpiration(new Date(System.currentTimeMillis() + jwtExpiration * 1000))
            .signWith(SignatureAlgorithm.HS512, jwtSecret)
            .compact();
    }
    
    public boolean validateToken(String token) {
        try {
            Jwts.parser().setSigningKey(jwtSecret).parseClaimsJws(token);
            return true;
        } catch (JwtException | IllegalArgumentException e) {
            return false;
        }
    }
}
```

### 11.2 HTTPS/TLS Configuration

```yaml
# application.yml
server:
  ssl:
    enabled: true
    key-store: classpath:keystore.p12
    key-store-password: ${SSL_PASSWORD}
    key-store-type: PKCS12
    key-alias: tomcat
  port: 8443

# Redirect HTTP to HTTPS
spring:
  mvc:
    redirect-slash: false
```

### 11.3 CORS Configuration

```java
@Configuration
public class CorsConfig {
    
    @Bean
    public WebMvcConfigurer corsConfigurer() {
        return new WebMvcConfigurer() {
            @Override
            public void addCorsMappings(CorsRegistry registry) {
                registry.addMapping("/api/**")
                    .allowedOrigins(
                        "http://localhost:3000",
                        "https://grocerystore.local"
                    )
                    .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
                    .allowedHeaders("*")
                    .allowCredentials(true)
                    .maxAge(3600);
            }
        };
    }
}
```

### 11.4 Rate Limiting

```java
@Configuration
public class RateLimitingConfig {
    
    @Bean
    public RateLimiter rateLimiter() {
        return RateLimiter.create(100.0 / 60.0); // 100 requests per minute
    }
}

@Component
public class RateLimitingInterceptor implements HandlerInterceptor {
    
    private final Map<String, RateLimiter> limiters = new ConcurrentHashMap<>();
    
    @Override
    public boolean preHandle(HttpServletRequest request, 
            HttpServletResponse response, Object handler) throws Exception {
        
        String username = SecurityContextHolder.getContext()
            .getAuthentication().getName();
        
        RateLimiter limiter = limiters.computeIfAbsent(username, 
            k -> RateLimiter.create(100.0 / 60.0));
        
        if (!limiter.tryAcquire()) {
            response.setStatus(429);
            response.setContentType("application/json");
            response.getWriter().write(
                "{\"error\": \"Rate limit exceeded\"}"
            );
            return false;
        }
        return true;
    }
}
```

---

## 12. API Testing with Postman

### 12.1 Postman Environment Variables

```json
{
  "id": "grocery-pos-env",
  "name": "Grocery POS Environment",
  "values": [
    {
      "key": "BASE_URL",
      "value": "http://localhost:8080/api/v1",
      "enabled": true
    },
    {
      "key": "AUTH_TOKEN",
      "value": "",
      "enabled": true
    },
    {
      "key": "USER_ID",
      "value": "3",
      "enabled": true
    }
  ]
}
```

### 12.2 Login Request (Postman)

```
POST {{BASE_URL}}/auth/login
Content-Type: application/json

{
  "username": "cashier_mary",
  "password": "secure_password_123"
}

// In Tests tab, save token:
var jsonData = pm.response.json();
pm.environment.set("AUTH_TOKEN", jsonData.data.token);
```

### 12.3 Product Lookup (Postman)

```
GET {{BASE_URL}}/products/barcode/5901234123457
Authorization: Bearer {{AUTH_TOKEN}}
```

---

## 13. Deployment & Configuration

### 13.1 application.yml Configuration

```yaml
spring:
  application:
    name: grocery-billing-api
  
  datasource:
    url: jdbc:mysql://localhost:3306/grocery_billing_db
    username: ${DB_USERNAME}
    password: ${DB_PASSWORD}
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 30000
      idle-timeout: 600000
  
  jpa:
    hibernate:
      ddl-auto: validate
    show-sql: false
    properties:
      hibernate:
        dialect: org.hibernate.dialect.MySQL8Dialect
        format_sql: true

jwt:
  secret: ${JWT_SECRET}
  expiration: 3600

logging:
  level:
    root: INFO
    com.grocerystore: DEBUG
  file:
    name: logs/application.log
  pattern:
    file: "%d{yyyy-MM-dd HH:mm:ss} - %msg%n"
```

### 13.2 Docker Deployment

```dockerfile
FROM openjdk:17-jdk-slim
WORKDIR /app
COPY target/grocery-billing-api-1.0.0.jar app.jar
EXPOSE 8080
ENV SPRING_PROFILES_ACTIVE=production
CMD ["java", "-jar", "app.jar"]
```

---

## Conclusion

This comprehensive REST API specification provides:

✅ **Complete endpoint coverage** for all core business functions  
✅ **Request/response examples** for every endpoint  
✅ **Error handling** with standardized error codes  
✅ **Security best practices** including JWT, HTTPS, and CORS  
✅ **Rate limiting** to prevent abuse  
✅ **Comprehensive documentation** for developers  
✅ **Postman-ready** format for easy testing  

The API is designed to be:
- **Secure:** JWT authentication, HTTPS encryption, PCI-DSS compliance
- **Scalable:** Stateless design, horizontal scaling ready
- **Maintainable:** Consistent response format, clear error messages
- **User-friendly:** Intuitive endpoint structure, detailed documentation

---

**Document Completed:** January 21, 2026  
**Next Step:** Frontend Implementation & Backend Service Layer Development
