# Grocery Store Billing Software - System Architecture Design

**Document Version:** 1.0  
**Date:** January 21, 2026  
**Architecture Type:** Microservices-Ready Layered Architecture

---

## Executive Summary

This document outlines the complete system architecture for the Grocery Store Billing Software using a Django frontend, Java Spring Boot backend REST API, and MySQL database. The architecture is designed for scalability, security, maintainability, and high performance in retail point-of-sale environments.

---

## 1. Architecture Overview

### 1.1 High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT TIER                                  │
├─────────────────────────────────────────────────────────────────────┤
│  Web Browser (POS Terminal)                                         │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Frontend Application (Django + HTML/CSS/JavaScript)          │  │
│  │ - POS Interface                                              │  │
│  │ - Dashboard & Reports                                        │  │
│  │ - Inventory Management UI                                    │  │
│  │ - Customer Management UI                                     │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │  HTTPS / REST API │
                    │   Communication   │
                    └─────────┬─────────┘
                              │
┌─────────────────────────────────────────────────────────────────────┐
│                      APPLICATION TIER                                │
├─────────────────────────────────────────────────────────────────────┤
│  Spring Boot REST API Server(s)                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ API Gateway / Load Balancer                                  │  │
│  │ - Route requests to appropriate microservices               │  │
│  │ - Authentication & Authorization                            │  │
│  │ - Rate limiting & throttling                                │  │
│  └──────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Microservices Layer                                          │  │
│  │  ├─ Transaction Service                                      │  │
│  │  ├─ Inventory Service                                        │  │
│  │  ├─ Product Service                                          │  │
│  │  ├─ Customer Service                                         │  │
│  │  ├─ Payment Service                                          │  │
│  │  ├─ Reporting Service                                        │  │
│  │  └─ Authentication Service                                   │  │
│  └──────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Business Logic Layer                                         │  │
│  │ - Transaction processing                                     │  │
│  │ - Inventory calculations                                     │  │
│  │ - Tax & discount calculations                                │  │
│  │ - Report generation                                          │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │  JDBC / Connection│
                    │  Pool (HikariCP)  │
                    └─────────┬─────────┘
                              │
┌─────────────────────────────────────────────────────────────────────┐
│                       DATABASE TIER                                  │
├─────────────────────────────────────────────────────────────────────┤
│  MySQL Database Server(s)                                           │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Primary Database Instance                                    │  │
│  │ ├─ Products Table                                            │  │
│  │ ├─ Inventory Table                                           │  │
│  │ ├─ Transactions Table                                        │  │
│  │ ├─ Customers Table                                           │  │
│  │ ├─ Payments Table                                            │  │
│  │ ├─ Users Table                                               │  │
│  │ └─ Reports/Logs Table                                        │  │
│  └──────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Replica Database Instance (Read-only)                        │  │
│  │ - For reporting & analytics                                  │  │
│  │ - Master-Slave replication                                   │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Architecture

### 2.1 Frontend Components (Django + HTML/CSS/JavaScript)

#### Frontend Application Structure:
```
FRONTEND (Django Application)
│
├── Django Server
│   ├── Views Layer
│   │   ├── POS Views (checkout, payment, transaction)
│   │   ├── Dashboard Views (sales, inventory, analytics)
│   │   ├── Inventory Views (stock management, transfers)
│   │   ├── Product Views (product catalog, management)
│   │   ├── Customer Views (customer profiles, loyalty)
│   │   └── Report Views (sales, financial, audit reports)
│   │
│   ├── Forms Layer
│   │   ├── TransactionForm
│   │   ├── ProductForm
│   │   ├── CustomerForm
│   │   ├── PaymentForm
│   │   └── InventoryAdjustmentForm
│   │
│   ├── Authentication & Middleware
│   │   ├── User Authentication (JWT token validation)
│   │   ├── Permission Checking
│   │   ├── CSRF Protection
│   │   ├── Rate Limiting
│   │   └── Audit Logging
│   │
│   ├── API Client
│   │   └── HTTP Requests to Spring Boot REST API
│   │
│   └── Templates (HTML + CSS + JavaScript)
│       ├── Base Templates
│       ├── POS Interface
│       ├── Dashboard & Charts
│       ├── Inventory Management
│       ├── Customer Management
│       └── Report Pages
│
├── Static Assets
│   ├── CSS (Bootstrap, custom styles)
│   ├── JavaScript
│   │   ├── JQuery / Fetch API for API calls
│   │   ├── Chart.js for analytics
│   │   ├── DataTables for data display
│   │   └── Custom POS logic
│   │
│   ├── Images & Icons
│   └── Barcode Scanner Integration
│
└── Offline Mode
    └── Service Workers & IndexedDB for local caching
```

### 2.2 Backend Components (Java Spring Boot)

#### Backend Application Structure:
```
BACKEND (Spring Boot REST API)
│
├── API Gateway / Zuul Router
│   ├── Request Routing
│   ├── Authentication Gateway
│   ├── Rate Limiting
│   └── Load Balancing
│
├── Controller Layer (REST Endpoints)
│   ├── TransactionController
│   │   ├── POST /api/v1/transactions (create transaction)
│   │   ├── GET /api/v1/transactions/{id} (get transaction)
│   │   ├── POST /api/v1/transactions/{id}/refund (refund)
│   │   └── GET /api/v1/transactions (list with filters)
│   │
│   ├── InventoryController
│   │   ├── GET /api/v1/inventory (list stock)
│   │   ├── PUT /api/v1/inventory/{productId} (update stock)
│   │   ├── GET /api/v1/inventory/low-stock (alerts)
│   │   └── POST /api/v1/inventory/adjustments (manual adjustments)
│   │
│   ├── ProductController
│   │   ├── GET /api/v1/products (product catalog)
│   │   ├── GET /api/v1/products/{id} (product details)
│   │   ├── POST /api/v1/products (create product)
│   │   ├── PUT /api/v1/products/{id} (update product)
│   │   └── GET /api/v1/products/barcode/{code} (barcode lookup)
│   │
│   ├── PaymentController
│   │   ├── POST /api/v1/payments/process (process payment)
│   │   ├── POST /api/v1/payments/refund (refund payment)
│   │   └── GET /api/v1/payments/{id}/status (payment status)
│   │
│   ├── CustomerController
│   │   ├── GET /api/v1/customers (customer list)
│   │   ├── POST /api/v1/customers (create customer)
│   │   ├── GET /api/v1/customers/{id} (customer profile)
│   │   ├── POST /api/v1/customers/{id}/loyalty (loyalty points)
│   │   └── GET /api/v1/customers/{id}/transactions (history)
│   │
│   ├── ReportController
│   │   ├── GET /api/v1/reports/daily-sales (daily summary)
│   │   ├── GET /api/v1/reports/category-sales (by category)
│   │   ├── GET /api/v1/reports/cashier-performance (staff metrics)
│   │   └── GET /api/v1/reports/financial (financial reports)
│   │
│   └── AuthController
│       ├── POST /api/v1/auth/login (authenticate user)
│       ├── POST /api/v1/auth/logout (logout)
│       └── POST /api/v1/auth/refresh-token (refresh JWT)
│
├── Service Layer (Business Logic)
│   ├── TransactionService
│   │   ├── createTransaction()
│   │   ├── processRefund()
│   │   ├── voidTransaction()
│   │   ├── calculateTotals()
│   │   └── applyDiscounts()
│   │
│   ├── InventoryService
│   │   ├── getStockLevel()
│   │   ├── deductStock()
│   │   ├── updateStock()
│   │   ├── checkLowStock()
│   │   └── generateReorderList()
│   │
│   ├── ProductService
│   │   ├── getAllProducts()
│   │   ├── getProductByBarcode()
│   │   ├── createProduct()
│   │   ├── updateProduct()
│   │   └── searchProducts()
│   │
│   ├── PaymentService
│   │   ├── processPayment()
│   │   ├── validatePayment()
│   │   ├── handlePaymentGatewayIntegration()
│   │   └── refundPayment()
│   │
│   ├── CustomerService
│   │   ├── createCustomer()
│   │   ├── updateCustomerProfile()
│   │   ├── manageLoyaltyPoints()
│   │   └── getPurchaseHistory()
│   │
│   ├── AuthenticationService
│   │   ├── authenticateUser()
│   │   ├── generateJWTToken()
│   │   ├── validateToken()
│   │   └── refreshToken()
│   │
│   ├── ReportService
│   │   ├── generateDailySalesReport()
│   │   ├── generateCategoryAnalysis()
│   │   ├── generateCashierMetrics()
│   │   └── generateFinancialReport()
│   │
│   └── AuditLoggingService
│       ├── logTransaction()
│       ├── logUserAction()
│       ├── logDataChanges()
│       └── generateAuditTrail()
│
├── Repository Layer (Data Access)
│   ├── TransactionRepository (JPA/Hibernate)
│   ├── InventoryRepository
│   ├── ProductRepository
│   ├── CustomerRepository
│   ├── PaymentRepository
│   ├── UserRepository
│   └── AuditLogRepository
│
├── Entity/Model Layer
│   ├── Transaction Entity
│   ├── TransactionLineItem Entity
│   ├── Inventory Entity
│   ├── Product Entity
│   ├── Customer Entity
│   ├── Payment Entity
│   ├── User Entity
│   └── AuditLog Entity
│
├── Security Layer
│   ├── JWT Token Provider
│   ├── Spring Security Configuration
│   ├── CORS Configuration
│   ├── Encryption/Decryption Utilities
│   └── Role-based Access Control (RBAC)
│
├── Utility & Helper Classes
│   ├── TaxCalculator
│   ├── PriceCalculator
│   ├── BarcodeValidator
│   ├── CurrencyConverter
│   ├── ReceiptGenerator
│   └── ValidationUtils
│
├── Exception Handling
│   ├── CustomExceptionHandler
│   ├── GlobalExceptionMapper
│   └── Custom Exception Classes
│
├── Configuration
│   ├── DataSourceConfig (Database connection)
│   ├── SecurityConfig (Spring Security)
│   ├── JpaConfig (Hibernate/JPA)
│   ├── CorsConfig (Cross-Origin Resource Sharing)
│   └── ApplicationProperties (application.yml/properties)
│
└── Scheduling & Async Tasks
    ├── DailyReportScheduler
    ├── InventoryCheckScheduler
    ├── BackupScheduler
    └── CacheRefreshScheduler
```

### 2.3 Database Components (MySQL)

#### Database Schema Structure:
```
MySQL Database
│
├── Core Tables
│   ├── users
│   │   ├── user_id (PK)
│   │   ├── username (UNIQUE)
│   │   ├── password_hash
│   │   ├── email
│   │   ├── role (RBAC)
│   │   ├── is_active
│   │   ├── last_login
│   │   └── created_at
│   │
│   ├── products
│   │   ├── product_id (PK)
│   │   ├── sku (UNIQUE)
│   │   ├── barcode (UNIQUE)
│   │   ├── name
│   │   ├── description
│   │   ├── category_id (FK)
│   │   ├── supplier_id (FK)
│   │   ├── price
│   │   ├── cost_price
│   │   ├── expiry_date
│   │   ├── is_active
│   │   └── created_at
│   │
│   ├── categories
│   │   ├── category_id (PK)
│   │   ├── name
│   │   ├── parent_category_id (FK - hierarchical)
│   │   └── description
│   │
│   ├── inventory
│   │   ├── inventory_id (PK)
│   │   ├── product_id (FK)
│   │   ├── quantity_on_hand
│   │   ├── reorder_level
│   │   ├── reorder_quantity
│   │   ├── last_counted_date
│   │   └── warehouse_location
│   │
│   ├── transactions
│   │   ├── transaction_id (PK)
│   │   ├── transaction_date
│   │   ├── cashier_id (FK - users)
│   │   ├── customer_id (FK, nullable)
│   │   ├── subtotal
│   │   ├── tax_amount
│   │   ├── discount_amount
│   │   ├── total_amount
│   │   ├── status (COMPLETED, VOID, REFUNDED)
│   │   ├── created_at
│   │   └── void_reason (nullable)
│   │
│   ├── transaction_line_items
│   │   ├── line_item_id (PK)
│   │   ├── transaction_id (FK)
│   │   ├── product_id (FK)
│   │   ├── quantity
│   │   ├── unit_price
│   │   ├── line_total
│   │   └── discount_applied
│   │
│   ├── customers
│   │   ├── customer_id (PK)
│   │   ├── phone (UNIQUE)
│   │   ├── email (UNIQUE)
│   │   ├── first_name
│   │   ├── last_name
│   │   ├── address
│   │   ├── city
│   │   ├── loyalty_points
│   │   ├── total_spent
│   │   ├── member_since
│   │   └── is_active
│   │
│   ├── payments
│   │   ├── payment_id (PK)
│   │   ├── transaction_id (FK)
│   │   ├── payment_method (CASH, CARD, DIGITAL)
│   │   ├── amount
│   │   ├── status (PENDING, APPROVED, DECLINED)
│   │   ├── reference_number
│   │   ├── gateway_response
│   │   └── created_at
│   │
│   ├── audit_logs
│   │   ├── log_id (PK)
│   │   ├── user_id (FK)
│   │   ├── action
│   │   ├── entity_type
│   │   ├── entity_id
│   │   ├── old_value
│   │   ├── new_value
│   │   ├── timestamp
│   │   └── ip_address
│   │
│   ├── suppliers
│   │   ├── supplier_id (PK)
│   │   ├── name
│   │   ├── contact_person
│   │   ├── email
│   │   ├── phone
│   │   └── address
│   │
│   └── reports_cache
│       ├── cache_id (PK)
│       ├── report_type
│       ├── report_date
│       ├── data (JSON)
│       └── generated_at
│
├── Indexes for Performance
│   ├── idx_product_barcode (products.barcode)
│   ├── idx_transaction_date (transactions.transaction_date)
│   ├── idx_transaction_cashier (transactions.cashier_id)
│   ├── idx_customer_phone (customers.phone)
│   └── idx_audit_log_user (audit_logs.user_id)
│
└── Replication
    ├── Master-Slave replication enabled
    ├── Slave database for read-only queries
    └── Automatic failover configuration
```

---

## 3. Data Flow Architecture

### 3.1 Complete Transaction Flow (POS Checkout)

```
┌─────────────────────────────────────────────────────────────────────┐
│ FRONTEND (Django)                                                   │
│                                                                     │
│ 1. Cashier scans product barcode or searches                       │
│    ↓                                                                │
│ 2. JavaScript sends HTTP GET request                               │
│    GET /api/v1/products/barcode/123456789                          │
└────────────────────────┬────────────────────────────────────────────┘
                         │ HTTPS Request
                         ↓
┌─────────────────────────────────────────────────────────────────────┐
│ BACKEND (Spring Boot)                                               │
│                                                                     │
│ 3. API Gateway routes to ProductController                         │
│    ↓                                                                │
│ 4. ProductController receives request                              │
│    ↓                                                                │
│ 5. Service Layer: ProductService.getProductByBarcode()             │
│    ↓                                                                │
│ 6. Repository Layer: ProductRepository.findByBarcode()             │
└────────────────────────┬────────────────────────────────────────────┘
                         │ SQL Query
                         ↓
┌─────────────────────────────────────────────────────────────────────┐
│ DATABASE (MySQL)                                                    │
│                                                                     │
│ 7. Execute: SELECT * FROM products WHERE barcode = '123456789'     │
│    ↓                                                                │
│ 8. Return product record with price, category, etc.                │
└────────────────────────┬────────────────────────────────────────────┘
                         │ JSON Response
                         ↓
┌─────────────────────────────────────────────────────────────────────┐
│ BACKEND (Spring Boot)                                               │
│                                                                     │
│ 9. Map product entity to DTO                                       │
│    ↓                                                                │
│ 10. Return JSON: {productId, name, price, inventory_level}         │
└────────────────────────┬────────────────────────────────────────────┘
                         │ HTTPS Response (JSON)
                         ↓
┌─────────────────────────────────────────────────────────────────────┐
│ FRONTEND (Django)                                                   │
│                                                                     │
│ 11. Receive JSON response                                          │
│     ↓                                                               │
│ 12. Display product in cart (HTML table/div)                       │
│     ↓                                                               │
│ 13. Update cart totals via JavaScript                              │
│     - Subtotal calculation                                         │
│     - Tax calculation (local rate)                                 │
│     - Display total to cashier                                     │
│     ↓                                                               │
│ 14. Repeat steps 1-13 for each item until checkout                │
│     ↓                                                               │
│ 15. Cashier selects payment method and submits transaction         │
│     POST /api/v1/transactions                                      │
│     Body: {                                                         │
│       items: [{productId, quantity, price}],                       │
│       paymentMethod: "CARD",                                       │
│       customerId: null,                                            │
│       appliedDiscounts: []                                         │
│     }                                                               │
└────────────────────────┬────────────────────────────────────────────┘
                         │ HTTPS Request (JSON)
                         ↓
┌─────────────────────────────────────────────────────────────────────┐
│ BACKEND (Spring Boot)                                               │
│                                                                     │
│ 16. API Gateway validates authentication (JWT token)               │
│     ↓                                                               │
│ 17. TransactionController.createTransaction() receives request     │
│     ↓                                                               │
│ 18. Service: TransactionService.createTransaction()                │
│     - Validate inventory availability                              │
│     - Calculate taxes based on location                            │
│     - Apply discounts                                              │
│     - Calculate final total                                        │
│     ↓                                                               │
│ 19. Create Transaction entity in memory                            │
│     ↓                                                               │
│ 20. Call PaymentService.processPayment()                           │
│     - Route to payment gateway (Stripe, Square, etc.)             │
│     - Validate card/payment method                                 │
│     - Authorize transaction                                        │
│     - Return payment status & reference number                     │
│     ↓                                                               │
│ 21. If payment APPROVED:                                           │
│     a) Begin database transaction (ACID)                           │
│     b) Save Transaction to database                                │
│     c) Save TransactionLineItems to database                       │
│     d) Call InventoryService.deductStock()                         │
│     e) Update inventory table for each item                        │
│     f) Save Payment record                                         │
│     g) Log audit entry via AuditLoggingService                     │
│     h) Commit database transaction                                 │
│     ↓                                                               │
│ 22. Return response JSON:                                          │
│     {                                                               │
│       transactionId: "TXN20260121001",                             │
│       status: "COMPLETED",                                         │
│       totalAmount: 125.99,                                         │
│       paymentId: "PAY123456",                                      │
│       receiptUrl: "/api/v1/transactions/TXN001/receipt"            │
│     }                                                               │
└────────────────────────┬────────────────────────────────────────────┘
                         │ HTTPS Response (JSON)
                         ↓
┌─────────────────────────────────────────────────────────────────────┐
│ FRONTEND (Django)                                                   │
│                                                                     │
│ 23. Receive success response                                       │
│     ↓                                                               │
│ 24. Display confirmation message to cashier                        │
│     ↓                                                               │
│ 25. Generate receipt:                                              │
│     - Fetch: GET /api/v1/transactions/{transactionId}/receipt      │
│     ↓                                                               │
│ 26. Receive receipt HTML/PDF                                       │
│     ↓                                                               │
│ 27. Print receipt via thermal printer (JavaScript integration)     │
│     ↓                                                               │
│ 28. Clear cart, reset UI for next transaction                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Inventory Update Flow

```
FRONTEND                    BACKEND                      DATABASE
    │                          │                             │
    │─── Scan Product ────────>│                             │
    │                          │                             │
    │                    Check Inventory                      │
    │                    (ProductService)                     │
    │                          │                             │
    │                    Query InventoryRepository ─────────>│
    │                          │<────── Stock Level ────────│
    │                    Calculate Available Qty              │
    │                          │                             │
    │<──── Display Product ────│                             │
    │      with Qty Available  │                             │
    │                          │                             │
    │─── Add to Cart ────────>│                             │
    │     (Quantity: 2)        │                             │
    │                          │                             │
    │─── Complete Transaction >│                             │
    │                          │                             │
    │                    Deduct Stock                         │
    │                    (InventoryService.deductStock)       │
    │                          │                             │
    │                    Update SQL ──────────────────────>  │
    │                    UPDATE inventory SET                 │
    │                    quantity_on_hand = quantity_on_hand - 2
    │                    WHERE product_id = X                 │
    │                          │<────── Confirmation ───────│
    │                          │                             │
    │                    Check Low Stock                      │
    │                    (quantity_on_hand < reorder_level)   │
    │                          │                             │
    │                    IF LOW: Update Status                │
    │                    INSERT alert notification ───────>  │
    │                          │<────── Alert Created ─────│
    │                          │                             │
    │<──── Transaction Complete ─────────────────────────────│
    │      Print Receipt                                      │
    │                          │                             │
    │─── Request Daily Inventory Report                       │
    │─── GET /api/v1/inventory                               │
    │                          │                             │
    │                    Query Read Replica DB ────────────> │
    │                    SELECT product_id, name,             │
    │                    quantity_on_hand, reorder_level      │
    │                          │<────── Full Inventory ──────│
    │                          │                             │
    │<──── Display Report ────│                             │
```

### 3.3 Reporting & Analytics Flow

```
FRONTEND (Django)              BACKEND (Spring Boot)        DATABASE (MySQL)
        │                              │                            │
        │─ Request Daily Report ─────>│                            │
        │ GET /api/v1/reports/daily   │                            │
        │                              │                            │
        │                     ReportService.                         │
        │                     generateDailySalesReport()            │
        │                              │                            │
        │                     Check Cache ──────────────────────>  │
        │                     SELECT * FROM reports_cache           │
        │                     WHERE report_type='DAILY'             │
        │                     AND report_date=TODAY                 │
        │                              │<─── Cache Hit? ────────── │
        │                              │                            │
        │              IF CACHE MISS:                               │
        │                     Query Replica Database                │
        │                              │                            │
        │                     Complex SQL ──────────────────────>  │
        │                     SELECT t.transaction_date,            │
        │                            SUM(t.total_amount),           │
        │                            COUNT(t.transaction_id),       │
        │                            SUM(t.tax_amount)              │
        │                     FROM transactions t                   │
        │                     WHERE DATE(t.transaction_date)        │
        │                           = CURDATE()                     │
        │                     GROUP BY DATE(t.transaction_date)     │
        │                              │<─── Data Aggregated ──────│
        │                              │                            │
        │                     Format to JSON DTO                    │
        │                     Cache Result ────────────────────>   │
        │                     INSERT INTO reports_cache             │
        │                     VALUES (...)                          │
        │                              │<─── Cached ────────────── │
        │                              │                            │
        │<─── Return JSON Report ─────│                            │
        │     {                                                     │
        │       "date": "2026-01-21",                              │
        │       "totalSales": 5420.50,                             │
        │       "transactionCount": 87,                            │
        │       "totalTax": 420.50,                                │
        │       "averageTransaction": 62.30,                       │
        │       "topProduct": {...},                               │
        │       "paymentMethods": {...}                            │
        │     }                                                     │
        │                                                            │
        │ Display Charts & Graphs                                   │
        │ (Chart.js rendering)                                      │
        │                                                            │
        │─ Request Trend Analysis                                   │
        │ GET /api/v1/reports/category-sales?period=7days         │
        │                              │                            │
        │                     Query Replica DB                      │
        │                     Complex JOIN query ───────────────>  │
        │                              │<─── Sales by Category ────│
        │                              │                            │
        │<─── JSON with trend data ────│                            │
        │                                                            │
        │ Export to CSV/PDF                                         │
        │ (Generate file on backend)                                │
        │                                                            │
        │─ GET /api/v1/reports/export?format=pdf                   │
        │                              │                            │
        │                     Generate PDF ─────────────────────>  │
        │                     (iText/PDFBox library)                │
        │                              │                            │
        │<─── PDF File Download ──────│                            │
```

### 3.4 Authentication & Authorization Flow

```
FRONTEND (Browser)             BACKEND (Spring Boot)        Database (MySQL)
        │                              │                            │
        │─ Login Form Submission ───> │                            │
        │ POST /api/v1/auth/login     │                            │
        │ {username, password}        │                            │
        │                              │                            │
        │                     AuthController.login()                 │
        │                              │                            │
        │                     AuthenticationService ──────────────>  │
        │                     Query users table                      │
        │                     WHERE username = 'user@store.com'      │
        │                              │<─── User Record ──────────│
        │                              │                            │
        │                     Compare password hash                  │
        │                     (BCrypt verification)                  │
        │                              │                            │
        │              IF VALID:                                     │
        │                     Generate JWT Token                     │
        │                     {                                      │
        │                       header: {alg: 'HS256'},             │
        │                       payload: {                           │
        │                         sub: 'user_id',                   │
        │                         role: 'CASHIER',                  │
        │                         exp: timestamp+1hr,               │
        │                         iat: timestamp                     │
        │                       },                                   │
        │                       signature: HMAC-SHA256(...)         │
        │                     }                                      │
        │                              │                            │
        │<─── Return Token ──────────│                            │
        │     {                                                     │
        │       "token": "eyJhbGc...",                             │
        │       "expiresIn": 3600,                                  │
        │       "role": "CASHIER"                                   │
        │     }                                                     │
        │                                                            │
        │ Store token in localStorage                               │
        │ (or sessionStorage for security)                          │
        │                                                            │
        │─ Subsequent API Request ──>│                            │
        │ GET /api/v1/products       │                            │
        │ Headers: {                 │                            │
        │   Authorization: Bearer    │                            │
        │   eyJhbGc...               │                            │
        │ }                          │                            │
        │                              │                            │
        │                     API Gateway Filter                     │
        │                     Extract JWT Token                      │
        │                     Validate Signature                     │
        │                     Check Expiration                       │
        │                     Extract Claims (role, userId)          │
        │                              │                            │
        │              IF VALID:                                     │
        │                     Route to Controller                    │
        │                     Check RBAC: Can role access this?      │
        │                     (e.g., CASHIER can GET /products)      │
        │                              │                            │
        │              IF AUTHORIZED:                                │
        │                     Execute business logic                 │
        │                              │                            │
        │<─── Return Protected Data ─│                            │
        │                              │                            │
        │              IF UNAUTHORIZED:                              │
        │                     Return 403 Forbidden                   │
        │                              │                            │
        │              IF TOKEN EXPIRED:                             │
        │                     Return 401 Unauthorized                │
        │                              │                            │
        │─ Request New Token ──────> │                            │
        │ POST /api/v1/auth/refresh  │                            │
        │ {refreshToken}             │                            │
        │                              │                            │
        │                     Validate refresh token                 │
        │                     Generate new JWT access token          │
        │                              │                            │
        │<─── New Token ─────────────│                            │
        │                                                            │
        │─ Logout ───────────────────>│                            │
        │ POST /api/v1/auth/logout    │                            │
        │                              │                            │
        │                     Invalidate token (blacklist)           │
        │                     Log audit entry ────────────────────> │
        │                     INSERT INTO audit_logs ...             │
        │                              │<─── Logged ────────────── │
        │                              │                            │
        │<─── Logout Confirmed ──────│                            │
        │                                                            │
        │ Clear localStorage                                         │
        │ Redirect to login page                                     │
```

---

## 4. Communication Protocols

### 4.1 Frontend to Backend Communication

**Protocol:** HTTPS (TLS 1.3)

**Format:** JSON Request/Response

**Example Request:**
```json
POST /api/v1/transactions HTTP/1.1
Host: api.grocerypos.local
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "items": [
    {
      "productId": 1001,
      "quantity": 2,
      "unitPrice": 4.99
    },
    {
      "productId": 1502,
      "quantity": 1,
      "unitPrice": 12.99
    }
  ],
  "paymentMethod": "CARD",
  "customerId": null,
  "discounts": []
}
```

**Example Response:**
```json
HTTP/1.1 201 Created
Content-Type: application/json

{
  "transactionId": "TXN20260121001",
  "status": "COMPLETED",
  "subtotal": 22.97,
  "tax": 1.84,
  "total": 24.81,
  "paymentId": "PAY20260121001",
  "timestamp": "2026-01-21T14:35:22Z",
  "receiptUrl": "/api/v1/receipts/RCP20260121001"
}
```

### 4.2 Backend to Database Communication

**Protocol:** TCP/IP with JDBC (Java Database Connectivity)

**Connection Pooling:** HikariCP (optimized for high concurrency)

**Configuration:**
- Max pool size: 20 connections
- Min idle: 5 connections
- Connection timeout: 30 seconds
- Idle timeout: 10 minutes

**Example Query (via Hibernate/JPA):**
```java
// Entity-mapped query
Transaction transaction = transactionRepository.findById(transactionId);

// Native SQL (when needed)
List<Object[]> sales = entityManager.createNativeQuery(
  "SELECT DATE(transaction_date), SUM(total_amount) " +
  "FROM transactions " +
  "WHERE transaction_date >= ? AND transaction_date < ? " +
  "GROUP BY DATE(transaction_date)"
).setParameter(1, startDate).setParameter(2, endDate).getResultList();
```

---

## 5. Why This Architecture is Suitable

### 5.1 Django Frontend Advantages

| Advantage | Benefit |
|-----------|---------|
| **Rapid Development** | Built-in admin panel, ORM, form validation reduce development time |
| **Template Engine** | Server-side rendering for POS UI with dynamic content |
| **Authentication** | Built-in user management and session handling |
| **Security** | CSRF protection, SQL injection prevention, XSS protection |
| **Scalability** | Excellent for serving multiple POS terminals in a single store |
| **Integration** | Easy integration with HTML5, JavaScript, third-party libraries |
| **Offline Support** | Service Workers can cache templates for offline POS operation |
| **Maintenance** | Large community, extensive documentation, easy to find developers |

### 5.2 Spring Boot Backend Advantages

| Advantage | Benefit |
|-----------|---------|
| **Microservices Ready** | RESTful APIs designed for potential service separation |
| **High Performance** | Fast request processing, optimized for high throughput |
| **Scalability** | Horizontal scaling with stateless architecture |
| **Reliability** | Enterprise-grade application server, production-ready |
| **Security** | Spring Security for authentication/authorization, OAuth2 support |
| **Flexibility** | Supports multiple data sources, caching strategies, async operations |
| **Monitoring** | Spring Boot Actuator for health checks and metrics |
| **Integration** | Easy integration with payment gateways, reporting tools, external APIs |
| **Transaction Management** | Built-in ACID transaction support for critical operations |
| **Developer Ecosystem** | Large enterprise community, extensive libraries |

### 5.3 MySQL Database Advantages

| Advantage | Benefit |
|-----------|---------|
| **Reliability** | ACID compliance for transactional integrity (critical for POS) |
| **Performance** | Fast read/write operations for high transaction volume |
| **Scalability** | Master-Slave replication for read scaling |
| **Cost** | Open-source, no licensing costs |
| **Backup** | Easy backup and recovery procedures |
| **Familiarity** | Widely used in retail systems, standard choice |
| **Replication** | Built-in replication for reporting database |
| **Indexing** | Flexible indexing for query optimization |
| **Storage** | Sufficient storage capacity for multi-year transaction history |

### 5.4 Architectural Separation Benefits

| Component | Reason |
|-----------|--------|
| **Frontend/Backend Separation** | Independent scaling, easy to maintain, allows frontend devs to work independently |
| **Database Replication** | Production transactions on master, read-heavy reports on replica (no contention) |
| **API Gateway** | Centralized security, rate limiting, routing (future multi-service support) |
| **Service Layer** | Business logic isolation, reusability, testability |
| **Repository Pattern** | Data access abstraction, easier to switch databases if needed |

### 5.5 Scalability Path

```
Current Architecture:
┌─────────────┐  ┌──────────────────┐  ┌─────────┐
│  Django POS │─→│ Spring Boot API   │─→│ MySQL   │
│  (Single)   │  │ (Single Instance) │  │(Master) │
└─────────────┘  └──────────────────┘  └────┬────┘
                                              │
                                         ┌────▼────┐
                                         │  Slave  │
                                         │(Reports)│
                                         └─────────┘

Future Architecture (Multi-Store):
┌──────────────────────────────────────────────┐
│ Multiple Django Frontends (Different Stores) │
└──────────────────────┬───────────────────────┘
                       │
            ┌──────────┴──────────┐
            │   Load Balancer    │
            │  (Nginx/HAProxy)   │
            └──────────┬──────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
    ┌───▼───┐   ┌─────▼──┐   ┌──────▼──┐
    │Spring │   │Spring  │   │ Spring  │
    │Boot 1 │   │Boot 2  │   │ Boot 3  │
    └───┬───┘   └────┬───┘   └───┬─────┘
        │            │            │
        └────────────┼────────────┘
                     │
        ┌────────────┴────────────┐
        │   Database Connection   │
        │   Pool & Routing        │
        └────────────┬────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
    ┌───▼───┐   ┌────▼────┐  ┌──────▼───┐
    │MySQL  │   │MySQL    │  │ MySQL    │
    │Master │───│Slave 1  │  │ Slave 2  │
    └───────┘   │(Reports)│  │(Analytics)
                └─────────┘  └──────────┘
```

### 5.6 Resilience & Disaster Recovery

**Database Replication Strategy:**
- **Primary Database:** Handles all write operations (transactions, inventory)
- **Replica Database:** Handles all read operations (reports, analytics)
- **Automatic Failover:** If primary fails, replica can be promoted
- **Backup Schedule:** Automated daily backups with weekly archival

**API Server Redundancy:**
- Multiple Spring Boot instances behind load balancer
- If one server fails, requests route to others
- Health checks every 10 seconds
- Graceful shutdown procedures

**Frontend Resilience:**
- Offline mode with local IndexedDB caching
- Automatic sync when connectivity restored
- Service Workers for offline transaction capability

---

## 6. Technology Stack Summary

### 6.1 Frontend Stack
```
Client Device (POS Terminal)
├── Browser: Chrome/Firefox/Edge
├── Framework: Django (Templates)
├── Styling: Bootstrap 5 + Custom CSS
├── Scripting: JavaScript ES6+
├── API Communication: Fetch API
├── Charts: Chart.js
├── Tables: DataTables
├── Barcode Scanner: JavaScript integration
├── Printer: CUPS/Native print API
└── Offline: Service Workers + IndexedDB
```

### 6.2 Backend Stack
```
Java Spring Boot Application
├── Framework: Spring Boot 3.x
├── REST API: Spring Web (MVC)
├── Data Access: Spring Data JPA + Hibernate
├── Security: Spring Security 6.x
├── Validation: Jakarta Bean Validation
├── JSON: Jackson
├── Caching: Spring Cache + Redis (optional)
├── Task Scheduling: Spring Scheduling
├── Logging: SLF4J + Logback
├── Testing: JUnit 5 + Mockito
├── Build: Maven
└── Server: Embedded Tomcat
```

### 6.3 Database Stack
```
MySQL 8.0+
├── Storage Engine: InnoDB (ACID)
├── Character Set: UTF8MB4
├── Replication: MySQL Master-Slave
├── Backup: mysqldump + automated scripts
├── Monitoring: MySQL Workbench / Percona Monitoring
└── Query Optimization: Indexes + Query analysis
```

---

## 7. Deployment Architecture

### 7.1 Single Store Deployment

```
┌─────────────────────────────────────┐
│         POS Terminal                │
│  (Windows/Linux with Browser)       │
└─────────┬───────────────────────────┘
          │ HTTP/HTTPS
          ▼
┌─────────────────────────────────────┐
│      Application Server             │
│  Django (Port 8000) + Spring Boot   │
│  (Port 8080)                        │
│  - Can be on same VM or separate   │
│  - Firewall rules: Allow 8000, 8080│
└─────────┬───────────────────────────┘
          │ TCP Port 3306
          ▼
┌─────────────────────────────────────┐
│      Database Server (MySQL)        │
│      Port 3306 (Internal Only)      │
│  - Local replication for backups   │
│  - Backup Storage: External USB/NAS│
└─────────────────────────────────────┘
```

### 7.2 Multi-Store Deployment

```
        Store 1                 Store 2              Store N
    ┌────────────┐          ┌────────────┐       ┌──────────────┐
    │ Django POS │          │ Django POS │       │ Django POS   │
    └─────┬──────┘          └─────┬──────┘       └───────┬──────┘
          │                       │                      │
          └───────────────────────┼──────────────────────┘
                                  │ HTTPS
                                  ▼
                        ┌─────────────────────┐
                        │ API Gateway/Router  │
                        │ Load Balancer       │
                        │ (Nginx/HAProxy)     │
                        └─────────┬───────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                ┌───▼──┐     ┌────▼────┐   ┌──▼───┐
                │Spring│     │Spring   │   │Spring│
                │Boot 1│     │Boot 2   │   │Boot 3│
                └───┬──┘     └────┬────┘   └───┬──┘
                    │             │            │
                    └─────────────┼────────────┘
                                  │ TCP 3306
                                  ▼
                        ┌─────────────────────┐
                        │ Central MySQL DB    │
                        │ (Shared Database)   │
                        │ Multi-store support │
                        └─────────────────────┘
```

---

## 8. API Endpoint Summary

### 8.1 Core REST Endpoints

```
Authentication:
  POST   /api/v1/auth/login              - User login
  POST   /api/v1/auth/logout             - User logout
  POST   /api/v1/auth/refresh-token      - Refresh JWT token

Products:
  GET    /api/v1/products                - List all products
  GET    /api/v1/products/{id}           - Get product details
  GET    /api/v1/products/barcode/{code} - Lookup by barcode
  POST   /api/v1/products                - Create product (Admin)
  PUT    /api/v1/products/{id}           - Update product (Admin)
  DELETE /api/v1/products/{id}           - Soft delete product (Admin)

Transactions:
  POST   /api/v1/transactions            - Create transaction
  GET    /api/v1/transactions/{id}       - Get transaction details
  GET    /api/v1/transactions            - List transactions (with filters)
  POST   /api/v1/transactions/{id}/void  - Void transaction
  POST   /api/v1/transactions/{id}/refund- Refund transaction
  GET    /api/v1/transactions/{id}/receipt- Generate receipt

Inventory:
  GET    /api/v1/inventory               - Get inventory levels
  GET    /api/v1/inventory/{productId}   - Get product stock
  PUT    /api/v1/inventory/{productId}   - Update stock (Receive goods)
  POST   /api/v1/inventory/adjustments   - Manual stock adjustment
  GET    /api/v1/inventory/low-stock     - Get low stock alerts

Payments:
  POST   /api/v1/payments/process        - Process payment
  GET    /api/v1/payments/{id}/status    - Check payment status
  POST   /api/v1/payments/{id}/refund    - Refund payment

Customers:
  GET    /api/v1/customers               - List customers
  POST   /api/v1/customers               - Create customer
  GET    /api/v1/customers/{id}          - Get customer profile
  GET    /api/v1/customers/{id}/history  - Get purchase history
  POST   /api/v1/customers/{id}/loyalty  - Manage loyalty points

Reports:
  GET    /api/v1/reports/daily-sales     - Daily sales report
  GET    /api/v1/reports/category-sales  - Sales by category
  GET    /api/v1/reports/top-products    - Top selling products
  GET    /api/v1/reports/cashier-performance - Cashier metrics
  GET    /api/v1/reports/financial       - Financial reports
  GET    /api/v1/reports/export          - Export reports (PDF/CSV)
```

---

## 9. Security Architecture

### 9.1 Layers of Security

```
┌──────────────────────────────────────┐
│ 1. Network Security                  │
│    - HTTPS/TLS 1.3 encryption       │
│    - Firewall rules                  │
│    - VPN access (if remote)          │
│    - DDoS protection                 │
└──────────────────────────────────────┘
                  │
┌──────────────────────────────────────┐
│ 2. API Gateway Security              │
│    - Rate limiting (100 req/min)    │
│    - JWT validation                  │
│    - CORS policy enforcement         │
│    - Request/Response logging        │
└──────────────────────────────────────┘
                  │
┌──────────────────────────────────────┐
│ 3. Application Security              │
│    - Role-based access control      │
│    - Input validation                │
│    - SQL injection prevention        │
│    - XSS protection                  │
│    - CSRF tokens                     │
└──────────────────────────────────────┘
                  │
┌──────────────────────────────────────┐
│ 4. Data Security                     │
│    - At-rest encryption (AES-256)   │
│    - Password hashing (BCrypt)       │
│    - PII masking in logs             │
│    - Audit trail logging             │
└──────────────────────────────────────┘
                  │
┌──────────────────────────────────────┐
│ 5. Database Security                 │
│    - MySQL user privileges           │
│    - Connection encryption           │
│    - Stored procedure access         │
│    - Backup encryption               │
└──────────────────────────────────────┘
```

### 9.2 PCI-DSS Compliance

- Payment processing isolated from frontend
- Tokenization for card data
- No storage of sensitive card info
- Compliance certificates managed by payment gateway
- Regular security audits

---

## 10. Performance Considerations

### 10.1 Optimization Strategies

```
Frontend (Django):
  ├─ Caching: HTTP cache headers, Django cache framework
  ├─ Compression: GZIP compression for responses
  ├─ Asset Optimization: Minified CSS/JS, image optimization
  ├─ CDN: Static files served from CDN (optional)
  └─ Lazy Loading: Load scripts/images on demand

Backend (Spring Boot):
  ├─ Database Caching: Spring Cache + Redis
  ├─ Connection Pooling: HikariCP with optimized settings
  ├─ Query Optimization: Indexed queries, avoid N+1 problems
  ├─ Async Processing: @Async for non-blocking operations
  ├─ Batch Operations: Bulk inserts for imports
  └─ Monitoring: Micrometer metrics collection

Database (MySQL):
  ├─ Indexes: Strategic indexes on frequently queried columns
  ├─ Partitioning: Historical transaction data partitioning
  ├─ Query Cache: MySQL query cache enabled
  ├─ Replication: Replica DB for reporting
  ├─ Archival: Old transactions moved to archive tables
  └─ Maintenance: Regular ANALYZE TABLE, OPTIMIZE TABLE
```

### 10.2 Expected Performance Targets

```
Barcode Scan Lookup:          < 1 second   (Local cache + indexed DB)
Transaction Completion:       < 3 seconds  (Processing + DB write)
Report Generation (Daily):    < 10 seconds (Cached + aggregated queries)
User Login:                   < 2 seconds  (JWT generation + DB query)
Inventory Update:             < 500ms      (Single row update)
Concurrent Transactions:      50+          (With HikariCP + Load Balancer)
Daily Throughput:             3000+ transactions
```

---

## 11. Maintenance & Operations

### 11.1 Backup Strategy

```
Daily Backups:
  ├─ Full database backup every night (1:00 AM)
  ├─ Location: External storage (NAS/Cloud)
  ├─ Retention: 30 days rolling
  └─ Verification: Test restores weekly

Weekly Backups:
  ├─ Archive backup every Sunday (2:00 AM)
  ├─ Location: Off-site storage
  ├─ Retention: 1 year
  └─ Verification: Test restores monthly

Transaction Logs:
  ├─ Binary logs enabled for point-in-time recovery
  ├─ Retention: 7 days
  └─ Archival: Compress old logs
```

### 11.2 Monitoring & Alerting

```
Database Monitoring:
  ├─ CPU usage > 80% → Alert
  ├─ Memory usage > 90% → Alert
  ├─ Disk space < 10% free → Alert
  ├─ Replication lag > 5 seconds → Alert
  └─ Query slow log analysis daily

Application Monitoring:
  ├─ Response time > 5 seconds → Alert
  ├─ Error rate > 1% → Alert
  ├─ Thread count > 100 → Alert
  ├─ Memory leaks detection
  └─ JVM heap monitoring

Business Monitoring:
  ├─ Transactions per hour (vs. baseline)
  ├─ Failed payment attempts
  ├─ System uptime tracking
  └─ User activity logging
```

---

## 12. Future Scalability Roadmap

### Phase 1 (Current):
- Single store, single API server, single DB master

### Phase 2 (6-12 months):
- Multiple Spring Boot instances with load balancer
- Database read replica for reporting
- Redis caching layer for frequently accessed data

### Phase 3 (12-18 months):
- Multiple stores with central database
- Microservices separation (Transaction, Inventory, Payments services)
- Message queue (RabbitMQ) for async operations
- Elasticsearch for advanced search/reporting

### Phase 4 (18+ months):
- Kubernetes containerization
- Cloud deployment (AWS/Azure/GCP)
- Advanced analytics (big data processing)
- AI/ML for demand forecasting

---

## Conclusion

This three-tier architecture with Django frontend, Spring Boot backend, and MySQL database provides:

✅ **Scalability:** From single store to enterprise chain  
✅ **Reliability:** ACID transactions, replication, backup strategies  
✅ **Security:** PCI-DSS compliance, encryption, audit trails  
✅ **Maintainability:** Clean separation of concerns, standard technologies  
✅ **Performance:** Optimized queries, caching strategies, connection pooling  
✅ **Flexibility:** Easy to extend with new features, integrate with external systems  

The architecture is proven in retail environments and can grow with the business needs while maintaining system integrity and user experience.

---

**Document Completed:** January 21, 2026  
**Next Step:** Technical Specification & Database Schema Design
