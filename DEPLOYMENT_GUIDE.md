# Deployment Guide - Grocery Billing Software

## 🚀 Complete Deployment Instructions

This guide covers deploying the complete Grocery Billing Software system with MySQL, Java Spring Boot backend, and Django frontend.

---

## 📋 Prerequisites

### System Requirements
- **OS**: Windows 10/11, macOS, or Linux (Ubuntu 20.04+)
- **RAM**: Minimum 4GB, Recommended 8GB
- **Disk Space**: Minimum 5GB
- **Network**: Internet connection for package downloads

### Software Requirements
- **Java**: OpenJDK 17 LTS or Oracle JDK 17+
- **Python**: 3.8 or higher
- **MySQL**: 8.0+ or MariaDB 10.5+
- **Maven**: 3.8+ (for building Spring Boot)
- **Node.js**: 14+ (optional, for frontend build tools)
- **Git**: Latest version (for cloning repositories)

### Tools (Optional but Recommended)
- **Postman** or **Insomnia**: API testing
- **DBeaver** or **MySQL Workbench**: Database management
- **VS Code** or **IntelliJ IDEA**: Code editing
- **Docker**: For containerized deployment (optional)

---

## 🗄️ Part 1: MySQL Database Setup

### Step 1: Install MySQL

#### Windows
```bash
# Download from https://dev.mysql.com/downloads/mysql/

# Or use Chocolatey
choco install mysql

# Or use Windows Installer and follow setup wizard
```

#### macOS
```bash
# Using Homebrew
brew install mysql

# Start MySQL service
brew services start mysql

# Verify installation
mysql --version
```

#### Linux (Ubuntu/Debian)
```bash
# Update package manager
sudo apt update

# Install MySQL Server
sudo apt install mysql-server

# Start service
sudo systemctl start mysql

# Verify installation
mysql --version
```

### Step 2: Secure MySQL Installation

```bash
# Run security script
mysql_secure_installation

# When prompted:
# 1. Enter current password (none on first installation - just press Enter)
# 2. Set root password: YES
# 3. Remove anonymous users: YES
# 4. Disable remote root login: YES
# 5. Remove test database: YES
# 6. Reload privilege tables: YES
```

### Step 3: Create Database and User

```bash
# Login to MySQL
mysql -u root -p

# Enter password when prompted
```

```sql
-- Create database
CREATE DATABASE grocery_billing CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user
CREATE USER 'billing_user'@'localhost' IDENTIFIED BY 'secure_password_123';

-- Grant privileges
GRANT ALL PRIVILEGES ON grocery_billing.* TO 'billing_user'@'localhost';

-- Apply changes
FLUSH PRIVILEGES;

-- Verify
SHOW DATABASES;
SHOW GRANTS FOR 'billing_user'@'localhost';

-- Exit
EXIT;
```

### Step 4: Initialize Database Tables

#### Option A: Using SQL Script
```sql
-- Save this as schema.sql and run:
-- mysql -u billing_user -p grocery_billing < schema.sql

USE grocery_billing;

-- Users Table
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    role ENUM('ADMIN', 'MANAGER', 'CASHIER', 'INVENTORY_MANAGER', 'ACCOUNTANT') DEFAULT 'CASHIER',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
);

-- Categories Table
CREATE TABLE categories (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE INDEX idx_name (name)
);

-- Products Table
CREATE TABLE products (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category_id BIGINT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock INT DEFAULT 0,
    reorder_level INT DEFAULT 10,
    barcode VARCHAR(50) UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    INDEX idx_barcode (barcode),
    INDEX idx_category (category_id)
);

-- Customers Table
CREATE TABLE customers (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    loyalty_points INT DEFAULT 0,
    total_spent DECIMAL(10, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_phone (phone),
    INDEX idx_email (email)
);

-- Bills Table
CREATE TABLE bills (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    bill_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id BIGINT,
    subtotal DECIMAL(10, 2) NOT NULL,
    discount_amount DECIMAL(10, 2) DEFAULT 0,
    discount_percentage DECIMAL(5, 2) DEFAULT 0,
    tax_amount DECIMAL(10, 2) DEFAULT 0,
    total_amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    bill_status VARCHAR(50) DEFAULT 'COMPLETED',
    notes TEXT,
    created_by BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_bill_number (bill_number),
    INDEX idx_created_at (created_at),
    INDEX idx_bill_status (bill_status)
);

-- Bill Items Table
CREATE TABLE bill_items (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    bill_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bill_id) REFERENCES bills(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id),
    INDEX idx_bill_id (bill_id)
);

-- Payments Table
CREATE TABLE payments (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    bill_id BIGINT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    transaction_ref VARCHAR(100),
    payment_status VARCHAR(50) DEFAULT 'COMPLETED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bill_id) REFERENCES bills(id),
    INDEX idx_bill_id (bill_id),
    INDEX idx_created_at (created_at)
);

-- Audit Log Table
CREATE TABLE audit_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id BIGINT,
    old_value TEXT,
    new_value TEXT,
    ip_address VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
);

-- Insert default admin user
INSERT INTO users (username, password, email, role) VALUES
('admin', '$2a$10$slYQmyNdGzin7olVN3eq2OPST9/PgBkqquzi.Ss8KIUgO2t0jKMm6', 'admin@grocery.com', 'ADMIN');
-- Password: admin123 (BCrypt hashed)

-- Insert sample categories
INSERT INTO categories (name, description) VALUES
('Fruits', 'Fresh fruits'),
('Vegetables', 'Fresh vegetables'),
('Dairy', 'Milk and dairy products'),
('Bakery', 'Bread and bakery items'),
('Groceries', 'General groceries');

-- Insert sample products
INSERT INTO products (name, category_id, price, stock, barcode) VALUES
('Apple', 1, 50.00, 20, '1001'),
('Banana', 1, 30.00, 15, '1002'),
('Orange', 1, 45.00, 18, '1003'),
('Milk 1L', 3, 65.00, 12, '2001'),
('Bread', 4, 40.00, 25, '3001'),
('Eggs (Dozen)', 3, 80.00, 10, '2002');
```

#### Option B: Using Spring Boot JPA (Automatic)
Spring Boot will create tables automatically if you set:
```properties
# application.properties
spring.jpa.hibernate.ddl-auto=create-drop  # For first setup only!
```

### Step 5: Verify Database

```bash
# Login to MySQL
mysql -u billing_user -p grocery_billing

# List tables
SHOW TABLES;

# Check users table
SELECT * FROM users;

# Check products
SELECT COUNT(*) FROM products;

# Exit
EXIT;
```

---

## ☕ Part 2: Spring Boot Backend Deployment

### Step 1: Install Java

#### Windows
```bash
# Download from https://www.oracle.com/java/technologies/downloads/

# Or use Chocolatey
choco install openjdk17

# Verify
java -version
javac -version
```

#### macOS
```bash
brew install openjdk@17
sudo ln -sfn /usr/local/opt/openjdk@17/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk-17.jdk
java -version
```

#### Linux
```bash
sudo apt install openjdk-17-jdk
java -version
```

### Step 2: Install Maven

#### Windows
```bash
# Download from https://maven.apache.org/download.cgi
# Extract to C:\Program Files\apache-maven-3.8.x

# Add to environment variables:
# MAVEN_HOME = C:\Program Files\apache-maven-3.8.x
# Add to PATH: %MAVEN_HOME%\bin

# Verify
mvn -version
```

#### macOS
```bash
brew install maven
mvn -version
```

#### Linux
```bash
sudo apt install maven
mvn -version
```

### Step 3: Configure Spring Boot Application

Edit `application.properties`:

```properties
# ==================== Server ====================
server.port=8080
server.servlet.context-path=/

# ==================== Database ====================
spring.datasource.url=jdbc:mysql://localhost:3306/grocery_billing
spring.datasource.username=billing_user
spring.datasource.password=secure_password_123
spring.datasource.driver-class-name=com.mysql.cj.jdbc.Driver

# ==================== JPA/Hibernate ====================
spring.jpa.database-platform=org.hibernate.dialect.MySQL8Dialect
spring.jpa.hibernate.ddl-auto=validate
spring.jpa.show-sql=false
spring.jpa.properties.hibernate.format_sql=true
spring.jpa.properties.hibernate.use_sql_comments=true

# ==================== JWT ====================
app.jwt.secret=your-secret-key-must-be-at-least-32-characters-long-for-HS256
app.jwt.expiration=86400000

# ==================== Logging ====================
logging.level.root=INFO
logging.level.com.grocerystore.billing=DEBUG
logging.file.name=logs/application.log
logging.file.max-size=10MB
logging.file.max-history=10

# ==================== Application ====================
spring.application.name=grocery-billing-system
app.name=Grocery Billing System
app.version=1.0.0

# ==================== CORS ====================
app.cors.allowed-origins=http://localhost:3000,http://localhost:8000,http://localhost:8080
app.cors.allowed-methods=GET,POST,PUT,DELETE,OPTIONS
app.cors.allowed-headers=*
app.cors.allow-credentials=true
app.cors.max-age=3600
```

### Step 4: Build Backend

```bash
# Navigate to backend directory
cd backend

# Clean and build
mvn clean package -DskipTests

# Or with tests (if you have them)
mvn clean package

# Check for successful build
# Output: BUILD SUCCESS
```

### Step 5: Configure Environment Variables (Optional but Recommended)

Create `.env` file in backend root:
```properties
DB_URL=jdbc:mysql://localhost:3306/grocery_billing
DB_USERNAME=billing_user
DB_PASSWORD=secure_password_123
JWT_SECRET=your-secret-key-must-be-at-least-32-characters-long
JWT_EXPIRATION=86400000
SERVER_PORT=8080
```

### Step 6: Run Spring Boot Application

```bash
# Option 1: Using Maven
mvn spring-boot:run

# Option 2: Using JAR file
java -jar target/grocery-billing-system-1.0.0.jar

# Option 3: Using environment variables
java -jar target/grocery-billing-system-1.0.0.jar \
  --spring.datasource.url=$DB_URL \
  --spring.datasource.username=$DB_USERNAME \
  --spring.datasource.password=$DB_PASSWORD

# Verify startup
# Look for: "Tomcat started on port(s): 8080 with context path ''"
```

### Step 7: Test Backend API

```bash
# Login endpoint
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Expected Response:
# {
#   "success": true,
#   "message": "Login successful",
#   "data": {
#     "token": "eyJhbGciOiJIUzI1NiIs...",
#     "userId": 1,
#     "username": "admin",
#     "role": "ADMIN"
#   }
# }

# Get products (using token)
curl -X GET http://localhost:8080/api/v1/products \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 🐍 Part 3: Django Frontend Deployment

### Step 1: Install Python

#### Windows
```bash
# Download from https://www.python.org/downloads/

# Or use Chocolatey
choco install python

# Verify
python --version
pip --version
```

#### macOS
```bash
brew install python@3.11
python3 --version
pip3 --version
```

#### Linux
```bash
sudo apt install python3 python3-pip python3-venv
python3 --version
pip3 --version
```

### Step 2: Setup Python Virtual Environment

```bash
# Navigate to frontend directory
cd frontend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate

# Verify activation (should show (venv) prefix)
```

### Step 3: Install Python Dependencies

```bash
# Make sure you're in virtual environment (venv activated)

# Install from requirements.txt
pip install -r requirements.txt

# Verify installations
pip list

# Expected packages:
# Django 4.2.8
# djangorestframework 3.14.0
# django-cors-headers 4.3.1
# requests 2.31.0
# python-dotenv 1.0.0
# gunicorn 21.2.0
```

### Step 4: Configure Django Settings

Create or update `.env` file in frontend root:

```properties
# Django Settings
DEBUG=False
SECRET_KEY=your-secret-key-change-this-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
ENVIRONMENT=production

# Database (optional - default uses SQLite)
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=grocery_billing_django
DATABASE_USER=django_user
DATABASE_PASSWORD=secure_password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Backend API Configuration
BACKEND_API_URL=http://localhost:8080
BACKEND_API_TIMEOUT=10

# Session Configuration
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
SESSION_COOKIE_AGE=86400

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# Cache Configuration (optional)
CACHE_LOCATION=127.0.0.1:6379

# Email Configuration (optional)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Step 5: Configure Django Settings File

Update `config/settings.py`:

```python
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Security Settings
DEBUG = os.getenv('DEBUG', 'False') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-your-secret-key')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Backend API
BACKEND_API_URL = os.getenv('BACKEND_API_URL', 'http://localhost:8080')
BACKEND_API_TIMEOUT = int(os.getenv('BACKEND_API_TIMEOUT', 10))

# Session Configuration
SESSION_COOKIE_AGE = int(os.getenv('SESSION_COOKIE_AGE', 86400))
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False') == 'True'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# CORS
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:8080').split(',')

# Database
if os.getenv('DATABASE_ENGINE'):
    DATABASES = {
        'default': {
            'ENGINE': os.getenv('DATABASE_ENGINE'),
            'NAME': os.getenv('DATABASE_NAME'),
            'USER': os.getenv('DATABASE_USER'),
            'PASSWORD': os.getenv('DATABASE_PASSWORD'),
            'HOST': os.getenv('DATABASE_HOST'),
            'PORT': os.getenv('DATABASE_PORT'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
```

### Step 6: Run Django Migrations

```bash
# Make sure virtual environment is activated

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Verify setup
python manage.py check
```

### Step 7: Collect Static Files

```bash
# For production
python manage.py collectstatic --noinput

# Verify CSS, JS, images are in static/ directory
```

### Step 8: Test Django Development Server

```bash
# Run development server
python manage.py runserver 0.0.0.0:8000

# Access at http://localhost:8000/
# You should see the dashboard

# Verify API integration
# Try logging in with admin/admin123
```

### Step 9: Deploy with Gunicorn (Production)

```bash
# Make sure virtual environment is activated

# Install Gunicorn (if not in requirements.txt)
pip install gunicorn

# Run with Gunicorn
gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --worker-class sync \
  --timeout 120 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log \
  --log-level info

# Or create a service file (see systemd section)
```

---

## 🔗 Part 4: Connecting All Services

### Architecture Diagram
```
┌─────────────────────────────────────────────────────────┐
│                    USER BROWSER                          │
│              http://localhost:8000                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         DJANGO FRONTEND (Port 8000)                      │
│  - Serves HTML/CSS/JavaScript                          │
│  - Handles user authentication                         │
│  - Calls backend API for data                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ HTTP Requests (with JWT token)
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│      SPRING BOOT BACKEND (Port 8080)                    │
│  - REST API endpoints                                  │
│  - Business logic                                      │
│  - Data validation                                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ JDBC/MySQL Driver
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│        MYSQL DATABASE (Port 3306)                       │
│  - Users, Products, Bills, Payments, etc.             │
└─────────────────────────────────────────────────────────┘
```

### Configuration for Service Communication

#### Django → Java Backend Connection

File: `frontend/config/settings.py`
```python
# Backend API URL
BACKEND_API_URL = os.getenv('BACKEND_API_URL', 'http://localhost:8080')

# API Client uses this for all requests
# Example: http://localhost:8080/api/v1/auth/login
```

File: `frontend/apps/core/api_client.py`
```python
def __init__(self, base_url, timeout=10):
    self.base_url = base_url.rstrip('/')
    self.timeout = timeout
    # base_url will be: http://localhost:8080
```

#### Java Backend → MySQL Connection

File: `backend/application.properties`
```properties
spring.datasource.url=jdbc:mysql://localhost:3306/grocery_billing
spring.datasource.username=billing_user
spring.datasource.password=secure_password_123
```

### Service Startup Order

```bash
# Terminal 1: Start MySQL
# (Usually starts automatically as a service)
mysql -u root -p

# Terminal 2: Start Java Backend
cd backend
mvn spring-boot:run
# Verify: http://localhost:8080/api/v1/products (should return 401 - needs auth)

# Terminal 3: Start Django Frontend
cd frontend
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
# Verify: http://localhost:8000/ (should show login page)
```

### Test Service Integration

#### Test 1: Login via Django
```bash
curl -X POST http://localhost:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Should redirect to dashboard if successful
```

#### Test 2: Direct Backend API Call
```bash
# Get JWT token first
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Use token to access protected endpoint
curl -X GET http://localhost:8080/api/v1/products \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

#### Test 3: Create Bill via Django
```bash
# Login to Django first
curl -c cookies.txt -X POST http://localhost:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Create bill (Django will forward to Java backend)
curl -b cookies.txt -X POST http://localhost:8000/api/bills/ \
  -H "Content-Type: application/json" \
  -d '{
    "items": [{"productId": 1, "quantity": 2}],
    "discountAmount": 10,
    "taxRate": 5,
    "paymentMethod": "CASH"
  }'
```

---

## 🖥️ Part 5: Production Deployment

### Using systemd (Linux/Unix)

#### Create Backend Service File

File: `/etc/systemd/system/grocery-billing-backend.service`
```ini
[Unit]
Description=Grocery Billing System - Backend
After=network.target mysql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/home/billing/backend
Environment="JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64"
Environment="DB_URL=jdbc:mysql://localhost:3306/grocery_billing"
Environment="DB_USERNAME=billing_user"
Environment="DB_PASSWORD=secure_password_123"
Environment="JWT_SECRET=your-production-secret-key"
ExecStart=/usr/bin/java -jar /home/billing/backend/target/grocery-billing-system-1.0.0.jar
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable grocery-billing-backend
sudo systemctl start grocery-billing-backend
sudo systemctl status grocery-billing-backend
```

#### Create Frontend Service File

File: `/etc/systemd/system/grocery-billing-frontend.service`
```ini
[Unit]
Description=Grocery Billing System - Frontend
After=network.target grocery-billing-backend.service

[Service]
Type=notify
User=www-data
WorkingDirectory=/home/billing/frontend
Environment="PYTHONUNBUFFERED=1"
Environment="DEBUG=False"
Environment="SECRET_KEY=your-production-secret-key"
Environment="BACKEND_API_URL=http://localhost:8080"
Environment="ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com"
ExecStart=/home/billing/frontend/venv/bin/gunicorn \
    config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class sync \
    --timeout 120
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable grocery-billing-frontend
sudo systemctl start grocery-billing-frontend
sudo systemctl status grocery-billing-frontend
```

### Using Nginx as Reverse Proxy

File: `/etc/nginx/sites-available/grocery-billing`
```nginx
# Backend API
upstream backend_api {
    server 127.0.0.1:8080;
}

# Frontend
upstream frontend {
    server 127.0.0.1:8000;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# Main HTTPS Server
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Certificates (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/grocery-billing-access.log;
    error_log /var/log/nginx/grocery-billing-error.log;

    # Frontend (Root)
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS Headers
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization' always;
        
        # Handle OPTIONS requests
        if ($request_method = 'OPTIONS') {
            return 204;
        }
    }

    # Static files
    location /static/ {
        alias /home/billing/frontend/static/;
        expires 30d;
    }

    # Media files
    location /media/ {
        alias /home/billing/frontend/media/;
        expires 30d;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/grocery-billing /etc/nginx/sites-enabled/

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx

# Install SSL certificate (Let's Encrypt)
sudo apt install certbot python3-certbot-nginx
sudo certbot certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com
```

### Using Docker (Optional)

File: `Dockerfile.backend`
```dockerfile
# Java Backend
FROM openjdk:17-jdk-slim

WORKDIR /app

# Copy built JAR
COPY target/grocery-billing-system-1.0.0.jar .

# Expose port
EXPOSE 8080

# Run application
CMD ["java", "-jar", "grocery-billing-system-1.0.0.jar"]
```

File: `Dockerfile.frontend`
```dockerfile
# Django Frontend
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run with Gunicorn
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

File: `docker-compose.yml`
```yaml
version: '3.8'

services:
  # MySQL Database
  mysql:
    image: mysql:8.0
    container_name: grocery-mysql
    environment:
      MYSQL_DATABASE: grocery_billing
      MYSQL_USER: billing_user
      MYSQL_PASSWORD: secure_password_123
      MYSQL_ROOT_PASSWORD: root_password_123
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    networks:
      - grocery-network

  # Java Backend
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.backend
    container_name: grocery-backend
    ports:
      - "8080:8080"
    environment:
      SPRING_DATASOURCE_URL: jdbc:mysql://mysql:3306/grocery_billing
      SPRING_DATASOURCE_USERNAME: billing_user
      SPRING_DATASOURCE_PASSWORD: secure_password_123
    depends_on:
      - mysql
    networks:
      - grocery-network

  # Django Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.frontend
    container_name: grocery-frontend
    ports:
      - "8000:8000"
    environment:
      BACKEND_API_URL: http://backend:8080
      DEBUG: "False"
      SECRET_KEY: your-secret-key
    depends_on:
      - backend
    networks:
      - grocery-network

volumes:
  mysql_data:

networks:
  grocery-network:
    driver: bridge
```

```bash
# Deploy with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## 🧪 Part 6: Testing & Verification

### Checklist

```bash
# 1. Database
[ ] MySQL is running
[ ] Database 'grocery_billing' exists
[ ] All tables are created
[ ] Admin user exists in users table

# 2. Backend
[ ] Java 17 is installed
[ ] Backend builds without errors (mvn clean package)
[ ] Backend starts successfully
[ ] API is accessible at http://localhost:8080
[ ] Login endpoint works (/api/v1/auth/login)
[ ] JWT token is generated

# 3. Frontend
[ ] Python 3.8+ is installed
[ ] Virtual environment is created and activated
[ ] Dependencies are installed
[ ] Django checks pass (python manage.py check)
[ ] Frontend starts successfully
[ ] Frontend is accessible at http://localhost:8000

# 4. Integration
[ ] Frontend can login via Django
[ ] Frontend can fetch products from backend
[ ] Frontend can create bills
[ ] Invoices can be printed
[ ] All calculations are correct

# 5. Production
[ ] Nginx is configured
[ ] SSL certificates are installed
[ ] Services are running as systemd services
[ ] Logs are being generated
[ ] Performance is acceptable
```

### Test Commands

```bash
# Check MySQL
mysql -u billing_user -p -e "SELECT COUNT(*) as user_count FROM grocery_billing.users;"

# Check Backend
curl http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Check Frontend
curl http://localhost:8000/
```

---

## 🔧 Part 7: Troubleshooting

### MySQL Connection Issues

```
Error: "Communications link failure"

Solution:
1. Verify MySQL is running: mysql -u root -p
2. Check database exists: SHOW DATABASES;
3. Check user exists: SELECT User FROM mysql.user;
4. Check connection credentials in application.properties
5. Try connecting directly: mysql -h 127.0.0.1 -u billing_user -p grocery_billing
```

### Backend Startup Issues

```
Error: "Port 8080 already in use"

Solution:
# Windows
netstat -ano | findstr :8080
taskkill /PID <PID> /F

# Linux/macOS
lsof -i :8080
kill -9 <PID>

# Or use different port
java -Dserver.port=8081 -jar grocery-billing-system.jar
```

### Django Import Errors

```
Error: "ModuleNotFoundError: No module named 'django'"

Solution:
1. Verify virtual environment is activated: (venv) should appear in prompt
2. Install requirements: pip install -r requirements.txt
3. Verify installation: pip list | grep Django
```

### CORS Issues

```
Error: "Access to XMLHttpRequest blocked by CORS policy"

Solution:
1. Update CORS settings in backend (SecurityConfig)
2. Update CORS settings in Django (settings.py)
3. Check ALLOWED_HOSTS in Django settings.py
4. Verify frontend is accessing correct backend URL

# Example CORS config (backend)
add_allowed_origin("http://localhost:8000")
add_allowed_origin("http://localhost:3000")
```

---

## 📋 Deployment Checklist (Production)

```
PRE-DEPLOYMENT:
[ ] Code is tested and reviewed
[ ] All credentials are in environment variables
[ ] Database backups are configured
[ ] SSL certificates are obtained (Let's Encrypt)
[ ] Firewall rules are configured
[ ] Domain name is registered and DNS is configured
[ ] Server resources are sufficient (RAM, disk, CPU)

DURING DEPLOYMENT:
[ ] Database is initialized with schema
[ ] Backend JAR is built and deployed
[ ] Frontend is deployed to virtual environment
[ ] Nginx is configured as reverse proxy
[ ] Systemd services are created and started
[ ] SSL certificates are installed
[ ] Logs are being generated
[ ] Monitoring is enabled

POST-DEPLOYMENT:
[ ] Test login functionality
[ ] Test all major features (products, bills, reports)
[ ] Check error logs for issues
[ ] Monitor resource usage
[ ] Verify backups are working
[ ] Document deployment for team
[ ] Set up automated backups
[ ] Set up monitoring and alerts
[ ] Create disaster recovery plan
```

---

## 📊 Monitoring & Maintenance

### Check Service Status

```bash
# Backend service
sudo systemctl status grocery-billing-backend
sudo journalctl -u grocery-billing-backend -f

# Frontend service
sudo systemctl status grocery-billing-frontend
sudo journalctl -u grocery-billing-frontend -f

# Nginx
sudo systemctl status nginx
sudo tail -f /var/log/nginx/error.log
```

### Database Backups

```bash
# Manual backup
mysqldump -u billing_user -p grocery_billing > backup_$(date +%Y%m%d_%H%M%S).sql

# Automated daily backup (cron)
# Add to crontab: crontab -e
0 2 * * * mysqldump -u billing_user -ppassword grocery_billing > /backups/grocery_billing_$(date +\%Y\%m\%d).sql
```

### Log Rotation

File: `/etc/logrotate.d/grocery-billing`
```
/var/log/grocery-billing/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
}
```

---

## 🎯 Summary

| Service | Port | Status Check |
|---------|------|--------------|
| MySQL | 3306 | `mysql -u root -p` |
| Java Backend | 8080 | `curl http://localhost:8080/api/v1/products` |
| Django Frontend | 8000 | `http://localhost:8000/` |
| Nginx | 80/443 | `curl https://yourdomain.com/` |

**All services deployed and connected successfully!** 🚀
