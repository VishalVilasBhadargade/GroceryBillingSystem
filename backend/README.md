# Grocery Store Billing System - Project Structure

## Project Overview
This is a complete Spring Boot 3.x backend for a Grocery Store Billing System with REST API, JWT authentication, and comprehensive business logic.

## Directory Structure
```
grocery-billing-system/
├── backend/
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/grocerystore/billing/
│   │   │   │   ├── GroceryBillingApplication.java (Main entry point)
│   │   │   │   ├── controller/
│   │   │   │   │   ├── AuthController.java
│   │   │   │   │   ├── ProductController.java
│   │   │   │   │   ├── CustomerController.java
│   │   │   │   │   ├── BillController.java
│   │   │   │   │   ├── PaymentController.java
│   │   │   │   │   └── ReportController.java
│   │   │   │   ├── service/
│   │   │   │   │   ├── AuthService.java / AuthServiceImpl.java
│   │   │   │   │   ├── ProductService.java / ProductServiceImpl.java
│   │   │   │   │   ├── CustomerService.java / CustomerServiceImpl.java
│   │   │   │   │   ├── BillService.java / BillServiceImpl.java
│   │   │   │   │   ├── PaymentService.java / PaymentServiceImpl.java
│   │   │   │   │   └── ReportService.java / ReportServiceImpl.java
│   │   │   │   ├── repository/
│   │   │   │   │   ├── UserRepository.java
│   │   │   │   │   ├── ProductRepository.java
│   │   │   │   │   ├── CategoryRepository.java
│   │   │   │   │   ├── CustomerRepository.java
│   │   │   │   │   ├── BillRepository.java
│   │   │   │   │   ├── BillItemRepository.java
│   │   │   │   │   ├── PaymentRepository.java
│   │   │   │   │   └── SupplierRepository.java
│   │   │   │   ├── entity/
│   │   │   │   │   ├── User.java
│   │   │   │   │   ├── Product.java
│   │   │   │   │   ├── Category.java
│   │   │   │   │   ├── Customer.java
│   │   │   │   │   ├── Bill.java
│   │   │   │   │   ├── BillItem.java
│   │   │   │   │   ├── Payment.java
│   │   │   │   │   ├── Supplier.java
│   │   │   │   │   └── AuditLog.java
│   │   │   │   ├── dto/
│   │   │   │   │   ├── LoginRequestDTO.java
│   │   │   │   │   ├── LoginResponseDTO.java
│   │   │   │   │   ├── ProductDTO.java
│   │   │   │   │   ├── CustomerDTO.java
│   │   │   │   │   ├── BillDTO.java
│   │   │   │   │   ├── BillItemDTO.java
│   │   │   │   │   ├── CreateBillDTO.java
│   │   │   │   │   ├── PaymentDTO.java
│   │   │   │   │   └── ProcessPaymentDTO.java
│   │   │   │   ├── exception/
│   │   │   │   │   ├── ResourceNotFoundException.java
│   │   │   │   │   ├── DuplicateResourceException.java
│   │   │   │   │   ├── InsufficientInventoryException.java
│   │   │   │   │   └── GlobalExceptionHandler.java
│   │   │   │   ├── config/
│   │   │   │   │   ├── SecurityConfig.java
│   │   │   │   │   ├── CorsConfig.java
│   │   │   │   │   └── ModelMapperConfig.java
│   │   │   │   ├── security/
│   │   │   │   │   └── UserPrincipal.java
│   │   │   │   ├── filter/
│   │   │   │   │   └── JwtAuthenticationFilter.java
│   │   │   │   ├── util/
│   │   │   │   │   ├── JwtTokenProvider.java
│   │   │   │   │   └── GeneratorUtil.java
│   │   │   │   └── response/
│   │   │   │       └── ApiResponse.java
│   │   │   └── resources/
│   │   │       └── application.properties
│   │   └── test/ (for unit/integration tests)
│   └── pom.xml
└── frontend/
    └── (Django + HTML/CSS/JavaScript)
```

## Technology Stack
- **Language:** Java 17 LTS
- **Framework:** Spring Boot 3.2.1
- **Database:** MySQL 8.0+
- **Authentication:** JWT (JSON Web Tokens)
- **Build Tool:** Maven
- **Dependency Injection:** Lombok, Spring Dependency Injection
- **ORM:** JPA/Hibernate
- **Testing:** JUnit 5, Mockito

## Key Features Implemented
1. **User Authentication** - JWT-based login and token validation
2. **Product Management** - CRUD operations, barcode scanning, low-stock alerts
3. **Customer Management** - Profile management, loyalty points system
4. **Billing** - Bill creation, inventory deduction, void operations
5. **Payment Processing** - Multiple payment methods, refund handling
6. **Reporting** - Daily sales, inventory, and product reports
7. **Security** - Role-based access control (RBAC), password encryption
8. **Error Handling** - Centralized exception handling with meaningful error messages
9. **Audit Logging** - Track all system changes and transactions
10. **CORS** - Cross-origin resource sharing for frontend communication

## Database Schema
- 11 main tables (User, Product, Category, Customer, Bill, BillItem, Payment, Supplier, AuditLog, etc.)
- Proper relationships and constraints defined
- Indexes on frequently queried columns
- Master-slave replication support for reporting

## API Endpoints Summary
- **Auth:** POST /api/v1/auth/login
- **Products:** GET, POST, PUT, DELETE /api/v1/products
- **Customers:** GET, POST, PUT, DELETE /api/v1/customers
- **Bills:** GET, POST /api/v1/bills
- **Payments:** POST /api/v1/payments/process
- **Reports:** GET /api/v1/reports/*

## Running the Application
```bash
# Build
mvn clean install

# Run
mvn spring-boot:run

# Access
http://localhost:8080/api/v1
```

## Testing
```bash
# Run unit tests
mvn test

# Run with coverage
mvn clean test jacoco:report
```

## Deployment
- Create JAR: `mvn clean package`
- Docker support: Create Dockerfile with Java 17 base image
- Cloud deployment: AWS, Azure, Google Cloud compatible

## Security Features
- JWT token-based stateless authentication
- Role-based access control (ADMIN, MANAGER, CASHIER, INVENTORY_MANAGER, ACCOUNTANT)
- Password encryption using BCrypt
- SQL injection prevention via parameterized queries
- CORS configuration for secure frontend communication
- HTTPS/TLS support recommended for production

## Next Steps
1. Complete remaining service implementations
2. Create integration tests
3. Add caching layer (Redis)
4. Set up CI/CD pipeline
5. Deploy to production environment
6. Monitor performance and optimize queries
