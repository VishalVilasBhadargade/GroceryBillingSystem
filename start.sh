#!/bin/bash
# ============================================
# Grocery Billing Software - Startup Script
# ============================================
# This script starts all services automatically
# Works on macOS and Linux

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# ============================================
# 1. VERIFY PREREQUISITES
# ============================================
print_header "Checking Prerequisites"

# Check Java
if ! command -v java &> /dev/null; then
    print_error "Java is not installed"
    echo "Download from: https://www.oracle.com/java/technologies/downloads/"
    exit 1
fi
java_version=$(java -version 2>&1 | grep -oP '(?<=")\d+' | head -1)
if [ "$java_version" -lt 17 ]; then
    print_error "Java 17+ is required (found: $java_version)"
    exit 1
fi
print_success "Java $java_version is installed"

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    echo "Download from: https://www.python.org/downloads/"
    exit 1
fi
python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
print_success "Python $python_version is installed"

# Check Maven
if ! command -v mvn &> /dev/null; then
    print_error "Maven is not installed"
    echo "Download from: https://maven.apache.org/download.cgi"
    exit 1
fi
print_success "Maven is installed"

# Check MySQL
if ! command -v mysql &> /dev/null; then
    print_error "MySQL is not installed"
    echo "Download from: https://dev.mysql.com/downloads/mysql/"
    exit 1
fi
print_success "MySQL is installed"

# ============================================
# 2. SETUP MySQL
# ============================================
print_header "Setting up MySQL Database"

# Start MySQL service
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    print_info "Starting MySQL on macOS..."
    brew services start mysql 2>/dev/null || print_warning "MySQL may already be running"
else
    # Linux
    print_info "Starting MySQL on Linux..."
    sudo systemctl start mysql 2>/dev/null || print_warning "Could not start MySQL (may need sudo password)"
fi

# Wait for MySQL to start
sleep 2

# Check if database exists
if mysql -u billing_user -psecure_password_123 -e "USE grocery_billing" 2>/dev/null; then
    print_success "Database already exists"
else
    print_info "Creating database and user..."
    
    mysql -u root -p -e "
        CREATE DATABASE IF NOT EXISTS grocery_billing CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        CREATE USER IF NOT EXISTS 'billing_user'@'localhost' IDENTIFIED BY 'secure_password_123';
        GRANT ALL PRIVILEGES ON grocery_billing.* TO 'billing_user'@'localhost';
        FLUSH PRIVILEGES;
    " 2>/dev/null || {
        print_error "Could not create database. Please run MySQL setup manually."
        echo "Run: mysql -u root -p < schema.sql"
        exit 1
    }
    
    print_success "Database created"
fi

# ============================================
# 3. BUILD BACKEND
# ============================================
print_header "Building Java Spring Boot Backend"

if [ ! -d "backend" ]; then
    print_error "Backend directory not found!"
    exit 1
fi

cd backend

if [ ! -f "pom.xml" ]; then
    print_error "pom.xml not found in backend directory"
    exit 1
fi

print_info "Running Maven build (this may take 2-3 minutes)..."
if mvn clean package -DskipTests -q; then
    print_success "Backend built successfully"
else
    print_error "Maven build failed"
    echo "Try running: mvn clean package -DskipTests -X"
    exit 1
fi

# Verify JAR file exists
if [ ! -f "target/grocery-billing-system-1.0.0.jar" ]; then
    print_error "JAR file not created"
    exit 1
fi

print_success "JAR file created: target/grocery-billing-system-1.0.0.jar"

cd ..

# ============================================
# 4. SETUP FRONTEND
# ============================================
print_header "Setting up Django Frontend"

if [ ! -d "frontend" ]; then
    print_error "Frontend directory not found!"
    exit 1
fi

cd frontend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_info "Creating Python virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
print_info "Installing Python dependencies..."
pip install -q -r requirements.txt
print_success "Dependencies installed"

cd ..

# ============================================
# 5. START SERVICES
# ============================================
print_header "Starting Services"

print_info "In 5 seconds, three terminals will open..."
print_info "Close any terminal to stop all services"

sleep 5

# Start Backend
print_info "Starting Backend on port 8080..."
open -a Terminal "$(pwd)/backend" 2>/dev/null || {
    cd backend
    java -jar target/grocery-billing-system-1.0.0.jar &
    BACKEND_PID=$!
    cd ..
}

sleep 3

# Start Frontend
print_info "Starting Frontend on port 8000..."
cd frontend
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000 &
FRONTEND_PID=$!
cd ..

# ============================================
# 6. ACCESS APPLICATION
# ============================================
print_header "✨ All Services Started!"

print_success "Backend: http://localhost:8080"
print_success "Frontend: http://localhost:8000"
print_success "Database: localhost:3306"

echo ""
print_info "Credentials:"
echo "  Username: admin"
echo "  Password: admin123"

echo ""
print_info "Opening application in browser..."
sleep 2

# Open in browser
if [[ "$OSTYPE" == "darwin"* ]]; then
    open http://localhost:8000
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open http://localhost:8000
fi

# ============================================
# 7. KEEP RUNNING
# ============================================
print_info "Services are running..."
print_warning "Press Ctrl+C to stop all services"

wait
