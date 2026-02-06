# Grocery Store Billing Software - MySQL Database Design

**Document Version:** 1.0  
**Date:** January 21, 2026  
**Database Type:** MySQL 8.0+  
**Character Set:** UTF8MB4 (Unicode support)  
**Collation:** utf8mb4_unicode_ci

---

## Executive Summary

This document provides complete MySQL database design for the Grocery Store Billing Software, including table structures, data types, relationships, constraints, and indexing strategies optimized for retail point-of-sale operations.

---

## 1. Entity-Relationship Diagram (ERD)

### 1.1 Text-Based ER Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        DATABASE RELATIONSHIPS                           │
└─────────────────────────────────────────────────────────────────────────┘

                            ┌──────────────┐
                            │    users     │
                            ├──────────────┤
                            │ user_id (PK) │
                            │ username     │
                            │ password     │
                            │ role         │
                            └──────┬───────┘
                                   │
                    ┌──────────────┘│└──────────────┐
                    │               │               │
                    ▼               ▼               ▼
            ┌──────────────┐  ┌────────────┐  ┌────────────┐
            │   bills      │  │audit_logs  │  │inventory_  │
            │(transactions)│  │            │  │adjustments │
            ├──────────────┤  ├────────────┤  ├────────────┤
            │ bill_id (PK) │  │ log_id(PK) │  │ adj_id(PK) │
            │ cashier_id(FK)  │ user_id(FK)│  │ user_id(FK)│
            │ customer_id(FK) │ action     │  │ product_id(FK)
            │ bill_date    │  │ entity_id  │  │ qty_change │
            │ total        │  │ timestamp  │  │ reason     │
            └──────┬───────┘  └────────────┘  └────────────┘
                   │
                   │ (1:N relationship)
                   │
                   ▼
        ┌────────────────────┐
        │   bill_items       │
        ├────────────────────┤
        │ item_id (PK)       │
        │ bill_id (FK)       │
        │ product_id (FK) ──────────┐
        │ quantity           │       │
        │ unit_price         │       │
        │ line_total         │       │
        │ discount_applied   │       │
        └────────────────────┘       │
                                     │
                    ┌────────────────┘
                    │
                    ▼
        ┌──────────────────────┐
        │     products         │
        ├──────────────────────┤
        │ product_id (PK)      │
        │ sku (UNIQUE)         │
        │ barcode (UNIQUE)     │
        │ name                 │
        │ description          │
        │ category_id (FK) ──────────┐
        │ supplier_id (FK)     │      │
        │ price                │      │
        │ cost_price           │      │
        │ quantity_on_hand     │      │
        │ reorder_level        │      │
        │ reorder_quantity     │      │
        │ expiry_date          │      │
        │ is_active            │      │
        │ created_at           │      │
        │ updated_at           │      │
        └──────────────────────┘      │
                                      │
              ┌───────────────────────┘
              │
              ▼
        ┌──────────────┐
        │  categories  │
        ├──────────────┤
        │ category_id(PK)
        │ name         │
        │ description  │
        │ parent_id(FK)│ (Self-referencing for hierarchy)
        │ is_active    │
        └──────────────┘


        ┌──────────────────┐
        │    customers     │
        ├──────────────────┤
        │ customer_id (PK) │
        │ phone (UNIQUE)   │
        │ email (UNIQUE)   │
        │ first_name       │
        │ last_name        │
        │ address          │
        │ city             │
        │ loyalty_points   │
        │ total_spent      │
        │ is_active        │
        │ created_at       │
        └──────────┬───────┘
                   │
                   │ (1:N)
                   │
                   ▼
        ┌────────────────────┐
        │     payments       │
        ├────────────────────┤
        │ payment_id (PK)    │
        │ bill_id (FK)       │
        │ customer_id (FK)   │
        │ payment_method     │
        │ amount             │
        │ status             │
        │ reference_number   │
        │ gateway_response   │
        │ created_at         │
        └────────────────────┘

        ┌──────────────┐
        │   suppliers  │
        ├──────────────┤
        │ supplier_id(PK)
        │ name         │
        │ email        │
        │ phone        │
        │ address      │
        │ contact_person
        │ is_active    │
        └──────────────┘
```

---

## 2. Complete Database Schema

### 2.1 Users Table

**Purpose:** Store system user information and authentication data

```sql
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique user identifier',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT 'Login username',
    password_hash VARCHAR(255) NOT NULL COMMENT 'Bcrypt hashed password',
    email VARCHAR(100) NOT NULL UNIQUE COMMENT 'User email address',
    first_name VARCHAR(100) NOT NULL COMMENT 'User first name',
    last_name VARCHAR(100) NOT NULL COMMENT 'User last name',
    role ENUM('ADMIN', 'MANAGER', 'CASHIER', 'INVENTORY_MANAGER', 'ACCOUNTANT') 
        NOT NULL DEFAULT 'CASHIER' COMMENT 'User role for access control',
    is_active BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'Account active status',
    last_login TIMESTAMP NULL COMMENT 'Last successful login timestamp',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Account creation timestamp',
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last update timestamp',
    
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='System users with authentication and role-based access control';
```

**Data Types Explanation:**
- `INT`: Integer ID for auto-increment primary key
- `VARCHAR(50)`: Variable length string for username (max 50 characters)
- `VARCHAR(255)`: For password hash (bcrypt produces ~60 char hashes)
- `VARCHAR(100)`: For email and names
- `ENUM`: Restricted set of values for role (storage efficient)
- `BOOLEAN`: Store true/false for active status (internally stored as TINYINT)
- `TIMESTAMP`: Automatic date/time tracking

---

### 2.2 Categories Table

**Purpose:** Product classification with hierarchical support

```sql
CREATE TABLE categories (
    category_id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique category identifier',
    name VARCHAR(100) NOT NULL UNIQUE COMMENT 'Category name',
    description TEXT COMMENT 'Detailed category description',
    parent_id INT COMMENT 'Parent category ID for hierarchical structure',
    is_active BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'Category active status',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last update timestamp',
    
    FOREIGN KEY (parent_id) REFERENCES categories(category_id) 
        ON DELETE SET NULL ON UPDATE CASCADE COMMENT 'Self-referencing for category hierarchy',
    INDEX idx_parent_id (parent_id),
    INDEX idx_is_active (is_active),
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Product categories with support for hierarchical structure (e.g., Produce > Vegetables > Leafy Greens)';
```

**Hierarchical Example:**
```
Produce (parent_id = NULL)
├── Vegetables (parent_id = 1)
│   ├── Leafy Greens (parent_id = 2)
│   └── Root Vegetables (parent_id = 2)
└── Fruits (parent_id = 1)
    ├── Citrus (parent_id = 4)
    └── Berries (parent_id = 4)
```

---

### 2.3 Suppliers Table

**Purpose:** Supplier information for inventory management

```sql
CREATE TABLE suppliers (
    supplier_id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique supplier identifier',
    name VARCHAR(150) NOT NULL UNIQUE COMMENT 'Supplier company name',
    contact_person VARCHAR(100) COMMENT 'Primary contact person name',
    email VARCHAR(100) COMMENT 'Supplier email address',
    phone VARCHAR(20) COMMENT 'Supplier contact phone',
    address VARCHAR(255) COMMENT 'Supplier physical address',
    city VARCHAR(100) COMMENT 'Supplier city',
    state VARCHAR(50) COMMENT 'Supplier state/province',
    postal_code VARCHAR(20) COMMENT 'Postal/ZIP code',
    country VARCHAR(100) COMMENT 'Supplier country',
    payment_terms VARCHAR(100) COMMENT 'Payment terms (e.g., Net 30)',
    is_active BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'Supplier active status',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Record creation timestamp',
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last update timestamp',
    
    INDEX idx_name (name),
    INDEX idx_is_active (is_active),
    INDEX idx_city (city)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Supplier/Vendor information for purchase order and inventory management';
```

---

### 2.4 Products Table

**Purpose:** Core product catalog with inventory tracking

```sql
CREATE TABLE products (
    product_id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique product identifier',
    sku VARCHAR(50) NOT NULL UNIQUE COMMENT 'Stock Keeping Unit - unique product code',
    barcode VARCHAR(50) NOT NULL UNIQUE COMMENT 'Barcode for scanning at POS',
    name VARCHAR(200) NOT NULL COMMENT 'Product display name',
    description TEXT COMMENT 'Detailed product description',
    category_id INT NOT NULL COMMENT 'Foreign key to categories table',
    supplier_id INT NOT NULL COMMENT 'Foreign key to suppliers table',
    price DECIMAL(10, 2) NOT NULL COMMENT 'Current selling price',
    cost_price DECIMAL(10, 2) NOT NULL COMMENT 'Cost/wholesale price for profit calculation',
    quantity_on_hand INT NOT NULL DEFAULT 0 COMMENT 'Current stock level',
    reorder_level INT NOT NULL DEFAULT 10 COMMENT 'Minimum stock level to trigger reorder',
    reorder_quantity INT NOT NULL DEFAULT 100 COMMENT 'Quantity to order when reordering',
    expiry_date DATE COMMENT 'Product expiration date (NULL for non-perishables)',
    unit_of_measure VARCHAR(20) DEFAULT 'PIECE' COMMENT 'Unit type (PIECE, KG, LITER, etc.)',
    image_url VARCHAR(255) COMMENT 'URL to product image',
    is_active BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'Product availability status',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Product creation timestamp',
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last update timestamp',
    
    FOREIGN KEY (category_id) REFERENCES categories(category_id) 
        ON DELETE RESTRICT ON UPDATE CASCADE COMMENT 'Link to product category',
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) 
        ON DELETE RESTRICT ON UPDATE CASCADE COMMENT 'Link to product supplier',
    
    INDEX idx_sku (sku),
    INDEX idx_barcode (barcode),
    INDEX idx_category_id (category_id),
    INDEX idx_supplier_id (supplier_id),
    INDEX idx_expiry_date (expiry_date),
    INDEX idx_is_active (is_active),
    INDEX idx_quantity_on_hand (quantity_on_hand),
    INDEX idx_name (name),
    FULLTEXT INDEX idx_fulltext_name_description (name, description)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Product master catalog with pricing, inventory levels, and supplier information';
```

**Data Types Explanation:**
- `DECIMAL(10, 2)`: 10 total digits, 2 decimal places (for currency: $99999999.99)
- `INT`: Integer for quantities
- `DATE`: Date only (no time) for expiry dates
- `FULLTEXT INDEX`: For fast text search on product names

---

### 2.5 Customers Table

**Purpose:** Customer information and loyalty program tracking

```sql
CREATE TABLE customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique customer identifier',
    phone VARCHAR(20) NOT NULL UNIQUE COMMENT 'Customer phone number (primary identifier)',
    email VARCHAR(100) UNIQUE COMMENT 'Customer email address',
    first_name VARCHAR(100) NOT NULL COMMENT 'Customer first name',
    last_name VARCHAR(100) NOT NULL COMMENT 'Customer last name',
    address VARCHAR(255) COMMENT 'Customer street address',
    city VARCHAR(100) COMMENT 'Customer city',
    state VARCHAR(50) COMMENT 'Customer state/province',
    postal_code VARCHAR(20) COMMENT 'Customer postal code',
    country VARCHAR(100) COMMENT 'Customer country',
    loyalty_points INT NOT NULL DEFAULT 0 COMMENT 'Accumulated loyalty/reward points',
    total_spent DECIMAL(12, 2) NOT NULL DEFAULT 0.00 COMMENT 'Total amount spent across all transactions',
    member_since TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Customer registration date',
    is_active BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'Customer account active status',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Record creation timestamp',
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last update timestamp',
    
    INDEX idx_phone (phone),
    INDEX idx_email (email),
    INDEX idx_customer_name (first_name, last_name),
    INDEX idx_created_at (created_at),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Customer information with loyalty program data for targeted promotions and purchase analytics';
```

---

### 2.6 Bills Table

**Purpose:** Main transaction/bill records (renamed from "transactions" to avoid SQL keyword conflicts)

```sql
CREATE TABLE bills (
    bill_id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique bill/transaction identifier',
    bill_number VARCHAR(50) NOT NULL UNIQUE COMMENT 'Formatted bill number for receipt (e.g., BIL-2026-001)',
    cashier_id INT NOT NULL COMMENT 'Foreign key to users table (who processed the bill)',
    customer_id INT COMMENT 'Foreign key to customers table (NULL for walk-in customers)',
    bill_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Date and time of transaction',
    subtotal DECIMAL(12, 2) NOT NULL COMMENT 'Total before taxes and discounts',
    discount_amount DECIMAL(12, 2) NOT NULL DEFAULT 0.00 COMMENT 'Total discount applied to bill',
    tax_amount DECIMAL(12, 2) NOT NULL DEFAULT 0.00 COMMENT 'Total tax calculated',
    total_amount DECIMAL(12, 2) NOT NULL COMMENT 'Final bill total (subtotal - discount + tax)',
    status ENUM('COMPLETED', 'VOIDED', 'REFUNDED') 
        NOT NULL DEFAULT 'COMPLETED' COMMENT 'Transaction status',
    void_reason VARCHAR(255) COMMENT 'Reason for voiding (if applicable)',
    void_date TIMESTAMP NULL COMMENT 'Date/time when bill was voided',
    void_by_user_id INT COMMENT 'User who voided the bill',
    notes TEXT COMMENT 'Additional notes/comments about the transaction',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Record creation timestamp',
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last update timestamp',
    
    FOREIGN KEY (cashier_id) REFERENCES users(user_id) 
        ON DELETE RESTRICT ON UPDATE CASCADE COMMENT 'Link to cashier who processed bill',
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) 
        ON DELETE SET NULL ON UPDATE CASCADE COMMENT 'Link to customer (nullable for anonymous transactions)',
    FOREIGN KEY (void_by_user_id) REFERENCES users(user_id) 
        ON DELETE SET NULL ON UPDATE CASCADE COMMENT 'Link to manager who voided bill',
    
    INDEX idx_bill_number (bill_number),
    INDEX idx_bill_date (bill_date),
    INDEX idx_cashier_id (cashier_id),
    INDEX idx_customer_id (customer_id),
    INDEX idx_status (status),
    INDEX idx_bill_date_status (bill_date, status),
    INDEX idx_total_amount (total_amount)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Main transaction records for billing with complete audit trail and status tracking';
```

**Status Values:**
- `COMPLETED`: Normal finalized transaction
- `VOIDED`: Transaction cancelled by manager
- `REFUNDED`: Transaction refunded to customer

---

### 2.7 Bill_Items Table

**Purpose:** Line items for each bill (one-to-many relationship with bills)

```sql
CREATE TABLE bill_items (
    item_id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique line item identifier',
    bill_id INT NOT NULL COMMENT 'Foreign key to bills table',
    product_id INT NOT NULL COMMENT 'Foreign key to products table',
    quantity INT NOT NULL COMMENT 'Quantity of product sold',
    unit_price DECIMAL(10, 2) NOT NULL COMMENT 'Price per unit at time of sale',
    line_total DECIMAL(12, 2) NOT NULL COMMENT 'quantity * unit_price (before discount)',
    discount_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00 COMMENT 'Discount applied to this line item',
    final_line_total DECIMAL(12, 2) NOT NULL COMMENT 'line_total - discount_amount',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Record creation timestamp',
    
    FOREIGN KEY (bill_id) REFERENCES bills(bill_id) 
        ON DELETE CASCADE ON UPDATE CASCADE COMMENT 'Link to parent bill (cascade delete if bill deleted)',
    FOREIGN KEY (product_id) REFERENCES products(product_id) 
        ON DELETE RESTRICT ON UPDATE CASCADE COMMENT 'Link to product sold',
    
    INDEX idx_bill_id (bill_id),
    INDEX idx_product_id (product_id),
    UNIQUE KEY uk_bill_product (bill_id, product_id) COMMENT 'Prevent duplicate line items in same bill'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Individual line items within bills with pricing snapshot and discount tracking';
```

**Unique Constraint:** Prevents selling the same product twice in one bill (quantities are cumulative)

---

### 2.8 Payments Table

**Purpose:** Payment processing and reconciliation

```sql
CREATE TABLE payments (
    payment_id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique payment identifier',
    bill_id INT NOT NULL UNIQUE COMMENT 'Foreign key to bills table (one payment per bill)',
    customer_id INT COMMENT 'Foreign key to customers table',
    payment_method ENUM('CASH', 'CREDIT_CARD', 'DEBIT_CARD', 'DIGITAL_WALLET', 'CHECK') 
        NOT NULL COMMENT 'Method of payment used',
    amount DECIMAL(12, 2) NOT NULL COMMENT 'Amount paid',
    status ENUM('PENDING', 'APPROVED', 'DECLINED', 'FAILED') 
        NOT NULL DEFAULT 'PENDING' COMMENT 'Payment processing status',
    reference_number VARCHAR(100) COMMENT 'Payment gateway reference (transaction ID from processor)',
    card_last_four VARCHAR(4) COMMENT 'Last 4 digits of card (if card payment)',
    card_brand VARCHAR(20) COMMENT 'Card brand (VISA, MASTERCARD, AMEX, etc.)',
    gateway_response TEXT COMMENT 'Full response from payment gateway (JSON)',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Payment timestamp',
    processed_at TIMESTAMP NULL COMMENT 'When payment was processed (approved/declined)',
    
    FOREIGN KEY (bill_id) REFERENCES bills(bill_id) 
        ON DELETE RESTRICT ON UPDATE CASCADE COMMENT 'Link to bill being paid',
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) 
        ON DELETE SET NULL ON UPDATE CASCADE COMMENT 'Link to customer',
    
    INDEX idx_bill_id (bill_id),
    INDEX idx_customer_id (customer_id),
    INDEX idx_payment_method (payment_method),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    INDEX idx_reference_number (reference_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Payment transaction details with gateway integration for credit card processing and reconciliation';
```

**PCI-DSS Compliance:**
- Only store last 4 digits of card
- Never store full card numbers or CVV
- Actual card data processed by PCI-DSS compliant gateway

---

### 2.9 Audit_Logs Table

**Purpose:** Complete audit trail for compliance and security

```sql
CREATE TABLE audit_logs (
    log_id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique audit log identifier',
    user_id INT NOT NULL COMMENT 'Foreign key to users table (who performed action)',
    action VARCHAR(100) NOT NULL COMMENT 'Action performed (CREATE, UPDATE, DELETE, VOID, etc.)',
    entity_type VARCHAR(50) NOT NULL COMMENT 'Type of entity affected (PRODUCT, BILL, CUSTOMER, etc.)',
    entity_id INT NOT NULL COMMENT 'ID of the affected entity',
    old_value TEXT COMMENT 'Previous value (JSON format for complex data)',
    new_value TEXT COMMENT 'New value (JSON format for complex data)',
    changed_columns VARCHAR(255) COMMENT 'Comma-separated list of changed columns',
    ip_address VARCHAR(45) COMMENT 'IP address of user making change (supports IPv4 and IPv6)',
    user_agent VARCHAR(255) COMMENT 'Browser/client user agent string',
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'When action occurred',
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) 
        ON DELETE RESTRICT ON UPDATE CASCADE COMMENT 'Link to user who made change',
    
    INDEX idx_user_id (user_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_entity_type_id (entity_type, entity_id),
    INDEX idx_action (action)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Complete audit trail of all system changes for compliance, security, and debugging';
```

**Use Cases:**
- Track who changed product prices
- Audit bill voids and refunds
- Monitor user access patterns
- Comply with regulations

---

### 2.10 Inventory_Adjustments Table

**Purpose:** Track manual inventory adjustments with reasons

```sql
CREATE TABLE inventory_adjustments (
    adjustment_id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique adjustment identifier',
    product_id INT NOT NULL COMMENT 'Foreign key to products table',
    user_id INT NOT NULL COMMENT 'Foreign key to users table (who made adjustment)',
    adjustment_type ENUM('RECEIVED', 'DAMAGED', 'RETURNED', 'LOST', 'INVENTORY_COUNT', 'CORRECTION') 
        NOT NULL COMMENT 'Type of inventory adjustment',
    quantity_change INT NOT NULL COMMENT 'Change in quantity (positive or negative)',
    reason TEXT NOT NULL COMMENT 'Detailed reason for adjustment',
    reference_number VARCHAR(100) COMMENT 'Reference (PO number, damage report ID, etc.)',
    before_quantity INT NOT NULL COMMENT 'Stock level before adjustment',
    after_quantity INT NOT NULL COMMENT 'Stock level after adjustment',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Adjustment timestamp',
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last update timestamp',
    
    FOREIGN KEY (product_id) REFERENCES products(product_id) 
        ON DELETE RESTRICT ON UPDATE CASCADE COMMENT 'Link to product adjusted',
    FOREIGN KEY (user_id) REFERENCES users(user_id) 
        ON DELETE RESTRICT ON UPDATE CASCADE COMMENT 'Link to user making adjustment',
    
    INDEX idx_product_id (product_id),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    INDEX idx_adjustment_type (adjustment_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Stock adjustment records with complete change history for inventory accuracy and loss tracking';
```

---

### 2.11 Reports_Cache Table

**Purpose:** Cache generated reports for performance

```sql
CREATE TABLE reports_cache (
    cache_id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique cache entry identifier',
    report_type VARCHAR(50) NOT NULL COMMENT 'Type of report (DAILY_SALES, CATEGORY_SALES, etc.)',
    report_date DATE NOT NULL COMMENT 'Date for which report was generated',
    store_location VARCHAR(100) COMMENT 'For future multi-store support',
    data LONGTEXT NOT NULL COMMENT 'Cached report data (JSON format)',
    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'When cache was created',
    expires_at TIMESTAMP NOT NULL DEFAULT (DATE_ADD(NOW(), INTERVAL 24 HOUR)) COMMENT 'Cache expiration time',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Record creation timestamp',
    
    UNIQUE KEY uk_report_date (report_type, report_date, store_location),
    INDEX idx_report_type (report_type),
    INDEX idx_report_date (report_date),
    INDEX idx_expires_at (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Cached report data to improve dashboard performance and reduce database load';
```

---

## 3. Table Relationships & Constraints

### 3.1 Relationship Matrix

| From Table | To Table | Type | Relationship | Cascade |
|-----------|----------|------|-------------|---------|
| users | - | - | Root entity | - |
| categories | categories | 1:N | Self-referencing (hierarchy) | SET NULL |
| suppliers | - | - | Referenced by products | - |
| products | categories | N:1 | Many products per category | RESTRICT |
| products | suppliers | N:1 | Many products per supplier | RESTRICT |
| customers | - | - | Referenced by bills & payments | - |
| bills | users (cashier) | N:1 | Many bills per cashier | RESTRICT |
| bills | customers | N:1 | Many bills per customer | SET NULL |
| bills | users (void) | N:1 | Bill can be voided by manager | SET NULL |
| bill_items | bills | N:1 | Many items per bill | CASCADE |
| bill_items | products | N:1 | Many line items reference product | RESTRICT |
| payments | bills | 1:1 | One payment per bill | RESTRICT |
| payments | customers | N:1 | Many payments per customer | SET NULL |
| audit_logs | users | N:1 | Many logs per user | RESTRICT |
| inventory_adjustments | products | N:1 | Many adjustments per product | RESTRICT |
| inventory_adjustments | users | N:1 | Many adjustments per user | RESTRICT |
| reports_cache | - | - | No foreign keys | - |

---

### 3.2 Key Constraint Explanations

**CASCADE:**
- When a parent record is deleted, child records are automatically deleted
- Used for: `bill_items → bills` (deleting a bill deletes its items)
- **Danger:** Must be careful with CASCADE to avoid accidental data loss

**RESTRICT:**
- Prevents deletion of parent if child records exist
- Used for: `products → categories` (can't delete category with products)
- **Safety:** Ensures data integrity

**SET NULL:**
- Sets foreign key to NULL when parent is deleted
- Used for: `bills → customers` (delete customer but keep bill record)
- **Use case:** Historical data preservation

---

## 4. Data Type Selection Rationale

### 4.1 Numeric Types

```
User IDs, Product IDs, etc.       → INT (0 to 4.3 billion)
Quantities                         → INT (sufficient for inventory)
Loyalty Points                     → INT (reasonable limit)
Large numeric IDs (audit logs)     → BIGINT (for extreme growth)
Money/Prices                       → DECIMAL(12, 2) (exact precision)
Percentages/Ratios                 → DECIMAL(5, 2) or FLOAT
```

### 4.2 String Types

```
Fixed-length codes (SKU, phone)    → VARCHAR with exact limit
Variable text (names)              → VARCHAR(100-200)
Descriptions                       → TEXT (up to 65,535 chars)
Large content                      → LONGTEXT (for reports cache)
Email addresses                    → VARCHAR(100)
```

### 4.3 Date/Time Types

```
Date only (expiry dates)           → DATE
Date + Time (transactions)         → TIMESTAMP
Automatic current timestamp        → DEFAULT CURRENT_TIMESTAMP
```

### 4.4 Boolean Type

```
Status flags (is_active, etc.)     → BOOLEAN (TINYINT internally)
```

---

## 5. Indexing Strategy

### 5.1 Index Types & Usage

```
PRIMARY KEY:
  - Automatic unique index on ID columns
  - Fastest lookup for exact matches

UNIQUE INDEX:
  - Ensures uniqueness (barcode, SKU, email, phone)
  - Can be used for lookups like PRIMARY KEY

REGULAR INDEX:
  - Used on frequently searched columns
  - Speeds up WHERE, JOIN, ORDER BY clauses

COMPOSITE INDEX:
  - Index multiple columns for common query patterns
  - e.g., idx_bill_date_status (bill_date, status)

FULLTEXT INDEX:
  - Text search optimization for product names
  - Enables natural language searching
```

### 5.2 Indexed Columns by Table

| Table | Indexed Columns | Purpose |
|-------|-----------------|---------|
| users | username, email, role, created_at | Fast user lookup, filtering |
| categories | parent_id, is_active, name | Hierarchy navigation |
| suppliers | name, city | Supplier lookup, filtering |
| products | sku, barcode, category_id, supplier_id, expiry_date, is_active, quantity_on_hand | POS barcode scanning, reports |
| customers | phone, email, name, created_at | Customer lookup |
| bills | bill_number, bill_date, cashier_id, customer_id, status | Daily reconciliation, reporting |
| bill_items | bill_id, product_id | Join queries |
| payments | bill_id, customer_id, payment_method, status, reference_number | Payment reconciliation |
| audit_logs | user_id, timestamp, entity_type, entity_id, action | Compliance audits |
| inventory_adjustments | product_id, user_id, created_at | Stock history |

---

## 6. Sample Data

### 6.1 Sample Users

```sql
INSERT INTO users (username, password_hash, email, first_name, last_name, role) VALUES
('admin_user', '$2a$10$...hash...', 'admin@grocerystore.com', 'Admin', 'User', 'ADMIN'),
('manager_john', '$2a$10$...hash...', 'john@grocerystore.com', 'John', 'Manager', 'MANAGER'),
('cashier_mary', '$2a$10$...hash...', 'mary@grocerystore.com', 'Mary', 'Smith', 'CASHIER'),
('cashier_bob', '$2a$10$...hash...', 'bob@grocerystore.com', 'Bob', 'Johnson', 'CASHIER'),
('inventory_sam', '$2a$10$...hash...', 'sam@grocerystore.com', 'Sam', 'Wilson', 'INVENTORY_MANAGER');
```

### 6.2 Sample Categories

```sql
INSERT INTO categories (name, description, parent_id) VALUES
('Produce', 'Fresh fruits and vegetables', NULL),
('Vegetables', 'Fresh vegetables', 1),
('Leafy Greens', 'Lettuce, spinach, cabbage', 2),
('Root Vegetables', 'Carrots, potatoes, onions', 2),
('Fruits', 'Fresh fruits', 1),
('Citrus', 'Oranges, lemons, limes', 5),
('Berries', 'Strawberries, blueberries', 5),
('Dairy', 'Milk, cheese, yogurt', NULL),
('Meat', 'Fresh meat and poultry', NULL),
('Pantry', 'Canned goods and dry items', NULL);
```

### 6.3 Sample Products

```sql
INSERT INTO products (sku, barcode, name, description, category_id, supplier_id, price, cost_price, quantity_on_hand, reorder_level, reorder_quantity, expiry_date, unit_of_measure) VALUES
('SKU-001', '5901234123457', 'Organic Spinach', 'Fresh organic spinach - 200g bag', 3, 1, 3.99, 1.50, 50, 20, 100, '2026-02-15', 'PIECE'),
('SKU-002', '5901234123458', 'Carrots', 'Fresh carrots - 1 kg', 4, 1, 2.49, 0.80, 120, 50, 200, '2026-03-01', 'KG'),
('SKU-003', '5901234123459', 'Whole Milk', '1 Liter - Fresh milk', 8, 2, 4.99, 2.50, 80, 30, 150, '2026-01-28', 'LITER'),
('SKU-004', '5901234123460', 'Chicken Breast', '500g - Fresh chicken breast', 9, 3, 8.99, 4.00, 40, 15, 50, '2026-01-25', 'KG'),
('SKU-005', '5901234123461', 'Canned Beans', '400g - Black beans', 10, 4, 1.29, 0.45, 200, 50, 300, NULL, 'PIECE');
```

### 6.4 Sample Customers

```sql
INSERT INTO customers (phone, email, first_name, last_name, address, city, loyalty_points, total_spent) VALUES
('555-0001', 'john.doe@email.com', 'John', 'Doe', '123 Main St', 'Springfield', 150, 450.75),
('555-0002', 'jane.smith@email.com', 'Jane', 'Smith', '456 Oak Ave', 'Springfield', 200, 625.50),
('555-0003', 'bob.wilson@email.com', 'Bob', 'Wilson', '789 Elm St', 'Springfield', 75, 225.25),
('555-0004', NULL, 'Alice', 'Brown', '321 Pine Rd', 'Springfield', 0, 99.99);
```

### 6.5 Sample Bills

```sql
INSERT INTO bills (bill_number, cashier_id, customer_id, bill_date, subtotal, discount_amount, tax_amount, total_amount, status) VALUES
('BIL-2026-001', 3, 1, '2026-01-21 14:30:00', 22.47, 2.00, 1.97, 22.44, 'COMPLETED'),
('BIL-2026-002', 4, 2, '2026-01-21 14:45:00', 31.96, 0.00, 2.80, 34.76, 'COMPLETED'),
('BIL-2026-003', 3, NULL, '2026-01-21 15:00:00', 13.27, 1.00, 1.16, 13.43, 'COMPLETED'),
('BIL-2026-004', 4, 1, '2026-01-21 15:15:00', 44.98, 5.00, 3.50, 43.48, 'VOIDED');
```

### 6.6 Sample Bill Items

```sql
INSERT INTO bill_items (bill_id, product_id, quantity, unit_price, line_total, discount_amount, final_line_total) VALUES
(1, 1, 2, 3.99, 7.98, 1.00, 6.98),
(1, 3, 1, 4.99, 4.99, 0.00, 4.99),
(1, 5, 4, 1.29, 5.16, 1.00, 4.16),
(2, 2, 1, 2.49, 2.49, 0.00, 2.49),
(2, 4, 3, 8.99, 26.97, 0.00, 26.97),
(3, 1, 3, 3.99, 11.97, 1.00, 10.97),
(3, 5, 1, 1.29, 1.29, 0.00, 1.29);
```

### 6.7 Sample Payments

```sql
INSERT INTO payments (bill_id, customer_id, payment_method, amount, status, reference_number, processed_at) VALUES
(1, 1, 'CREDIT_CARD', 22.44, 'APPROVED', 'TXN-20260121-001', NOW()),
(2, 2, 'CASH', 34.76, 'APPROVED', NULL, NOW()),
(3, NULL, 'DEBIT_CARD', 13.43, 'APPROVED', 'TXN-20260121-002', NOW());
```

---

## 7. Database Configuration

### 7.1 Database Creation Script

```sql
-- Create database with UTF-8 support
CREATE DATABASE IF NOT EXISTS grocery_billing_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- Select the database
USE grocery_billing_db;

-- Set SQL mode for strict compliance
SET GLOBAL sql_mode='STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- Enable binary logging for replication
-- (Add to my.cnf: log_bin=mysql-bin)

-- Create all tables (as shown above)
-- ... [Include all CREATE TABLE statements] ...
```

### 7.2 Performance Optimization Settings

```ini
[mysqld]
# Performance
max_connections = 1000
max_allowed_packet = 16M
thread_cache_size = 100
sort_buffer_size = 2M
bulk_insert_buffer_size = 16M
tmp_table_size = 32M
max_heap_table_size = 32M

# InnoDB Settings
innodb_buffer_pool_size = 4G        # 50-80% of available RAM
innodb_log_file_size = 512M
innodb_flush_log_at_trx_commit = 2   # Balance between safety and performance
innodb_flush_method = O_DIRECT

# Replication
server_id = 1
log_bin = mysql-bin
binlog_format = ROW
relay_log = mysql-relay-bin

# Query Cache (if MySQL 5.7)
query_cache_type = 1
query_cache_size = 256M
```

---

## 8. Backup & Recovery Strategy

### 8.1 Backup Methods

**Full Backup (Daily at 1:00 AM):**
```bash
mysqldump -u root -p grocery_billing_db > backup_$(date +%Y%m%d).sql
gzip backup_$(date +%Y%m%d).sql
```

**Incremental Backup (Binary Logs):**
```bash
# Backups are automatic if binary logging enabled
# For point-in-time recovery, keep binlog files
```

**Automated Backup Script:**
```bash
#!/bin/bash
BACKUP_DIR="/backups/mysql"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Full backup
mysqldump -u root -p grocery_billing_db | \
  gzip > $BACKUP_DIR/full_backup_$DATE.sql.gz

# Keep only 30 days of backups
find $BACKUP_DIR -name "full_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete
```

### 8.2 Recovery Procedures

**Full Restore:**
```sql
gunzip < backup_20260121.sql.gz | mysql -u root -p grocery_billing_db
```

**Point-in-Time Recovery:**
```bash
mysqlbinlog mysql-bin.000001 mysql-bin.000002 mysql-bin.000003 \
  --stop-date="2026-01-21 15:00:00" | mysql -u root -p grocery_billing_db
```

---

## 9. Query Examples

### 9.1 Daily Sales Report

```sql
SELECT 
    DATE(b.bill_date) AS sale_date,
    COUNT(DISTINCT b.bill_id) AS transaction_count,
    SUM(b.total_amount) AS total_sales,
    SUM(b.tax_amount) AS total_tax,
    AVG(b.total_amount) AS avg_transaction,
    u.first_name AS cashier_name,
    u.user_id
FROM bills b
JOIN users u ON b.cashier_id = u.user_id
WHERE DATE(b.bill_date) = CURDATE()
  AND b.status = 'COMPLETED'
GROUP BY DATE(b.bill_date), u.user_id, u.first_name
ORDER BY sale_date DESC, cashier_name;
```

### 9.2 Top 10 Selling Products

```sql
SELECT 
    p.product_id,
    p.name,
    c.name AS category,
    SUM(bi.quantity) AS total_quantity_sold,
    SUM(bi.final_line_total) AS total_revenue,
    AVG(bi.unit_price) AS avg_price,
    COUNT(DISTINCT bi.bill_id) AS num_transactions
FROM bill_items bi
JOIN products p ON bi.product_id = p.product_id
JOIN categories c ON p.category_id = c.category_id
JOIN bills b ON bi.bill_id = b.bill_id
WHERE b.bill_date >= DATE_SUB(NOW(), INTERVAL 7 DAY)
  AND b.status = 'COMPLETED'
GROUP BY p.product_id, p.name, c.name
ORDER BY total_revenue DESC
LIMIT 10;
```

### 9.3 Low Stock Alert

```sql
SELECT 
    p.product_id,
    p.sku,
    p.name,
    p.quantity_on_hand,
    p.reorder_level,
    p.reorder_quantity,
    s.name AS supplier_name,
    s.phone AS supplier_phone
FROM products p
JOIN suppliers s ON p.supplier_id = s.supplier_id
WHERE p.quantity_on_hand <= p.reorder_level
  AND p.is_active = TRUE
ORDER BY p.quantity_on_hand ASC;
```

### 9.4 Customer Purchase History

```sql
SELECT 
    c.customer_id,
    c.first_name,
    c.last_name,
    c.phone,
    b.bill_id,
    b.bill_number,
    b.bill_date,
    b.total_amount,
    GROUP_CONCAT(p.name SEPARATOR ', ') AS products_purchased
FROM customers c
LEFT JOIN bills b ON c.customer_id = b.customer_id
LEFT JOIN bill_items bi ON b.bill_id = bi.bill_id
LEFT JOIN products p ON bi.product_id = p.product_id
WHERE c.customer_id = ? -- Parameter: customer ID
GROUP BY b.bill_id
ORDER BY b.bill_date DESC;
```

### 9.5 Inventory Audit Trail

```sql
SELECT 
    p.name,
    ia.adjustment_type,
    ia.quantity_change,
    ia.before_quantity,
    ia.after_quantity,
    u.first_name,
    u.last_name,
    ia.reason,
    ia.created_at
FROM inventory_adjustments ia
JOIN products p ON ia.product_id = p.product_id
JOIN users u ON ia.user_id = u.user_id
WHERE ia.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY ia.created_at DESC;
```

---

## 10. Database Maintenance

### 10.1 Regular Maintenance Tasks

```sql
-- Optimize tables (reclaim space, improve query speed)
-- Schedule: Weekly
OPTIMIZE TABLE bills, bill_items, products, customers, payments;

-- Analyze tables (update statistics for query optimizer)
-- Schedule: Weekly
ANALYZE TABLE bills, bill_items, products, customers, payments;

-- Check table integrity
-- Schedule: Monthly
CHECK TABLE bills, bill_items, products, customers, payments;

-- Rebuild fragmented tables
-- Schedule: Monthly
REBUILD TABLE bills PARTITION ALL;
```

### 10.2 Archive Old Data

```sql
-- Archive completed transactions older than 2 years
-- Schedule: Quarterly
INSERT INTO bills_archive
SELECT * FROM bills 
WHERE bill_date < DATE_SUB(NOW(), INTERVAL 2 YEAR)
  AND status = 'COMPLETED';

DELETE FROM bills 
WHERE bill_date < DATE_SUB(NOW(), INTERVAL 2 YEAR)
  AND status = 'COMPLETED';
```

---

## 11. Security Best Practices

### 11.1 User Access Control

```sql
-- Create application user (limited privileges)
CREATE USER 'app_user'@'localhost' IDENTIFIED BY 'strong_password_here';
GRANT SELECT, INSERT, UPDATE ON grocery_billing_db.* TO 'app_user'@'localhost';
GRANT DELETE ON grocery_billing_db.bills TO 'app_user'@'localhost'; -- Only bills (with cascade)

-- Create backup user
CREATE USER 'backup_user'@'localhost' IDENTIFIED BY 'backup_password_here';
GRANT SELECT, LOCK TABLES, SHOW VIEW ON grocery_billing_db.* TO 'backup_user'@'localhost';

-- Create analytics user (read-only, replica database)
CREATE USER 'analytics_user'@'%' IDENTIFIED BY 'analytics_password_here';
GRANT SELECT ON grocery_billing_db.* TO 'analytics_user'@'replica-server.local';
```

### 11.2 Encryption

```sql
-- Enable SSL for client connections
-- Add to my.cnf:
-- [mysqld]
-- ssl-ca=/path/to/ca.pem
-- ssl-cert=/path/to/server-cert.pem
-- ssl-key=/path/to/server-key.pem

-- Require SSL for user connections
ALTER USER 'app_user'@'localhost' REQUIRE SSL;

-- For sensitive data columns, use AES encryption in application layer
-- Never store unencrypted sensitive data
```

---

## 12. Monitoring & Alerts

### 12.1 Key Metrics to Monitor

```sql
-- Check table sizes
SELECT 
    TABLE_NAME,
    ROUND(((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024), 2) AS size_mb
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'grocery_billing_db'
ORDER BY size_mb DESC;

-- Check slow queries
-- Enable: SET GLOBAL slow_query_log = 'ON';
-- Min duration: SET GLOBAL long_query_time = 2;

-- Monitor replication lag (on slave)
SHOW SLAVE STATUS\G
```

### 12.2 Performance Alerts

| Alert | Threshold | Action |
|-------|-----------|--------|
| Database size | > 10GB | Archive old data, add storage |
| Slow query | > 2 seconds | Analyze query, add indexes |
| Replication lag | > 5 seconds | Check slave performance |
| Lock wait timeout | Any occurrence | Identify blocking query |
| Disk usage | > 85% | Add storage immediately |

---

## Conclusion

This comprehensive MySQL database design provides:

✅ **Data Integrity:** Primary and foreign keys, constraints, normalization  
✅ **Performance:** Strategic indexing on frequently queried columns  
✅ **Scalability:** Efficient schema design to handle millions of records  
✅ **Security:** User access control, audit trails, PCI-DSS compliance  
✅ **Maintainability:** Clear documentation, backup strategies, monitoring  
✅ **Compliance:** Complete audit trail for regulatory requirements  

The schema is production-ready and can be deployed immediately with automated backups and monitoring.

---

**Document Completed:** January 21, 2026  
**Next Step:** API Endpoint Design & Java Spring Boot Implementation
