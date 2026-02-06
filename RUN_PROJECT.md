# 🚀 How to Run the Grocery Billing Software - Complete Guide

## Quick Start Summary

This project requires **3 main services**:
1. **MySQL Database** (Port 3306)
2. **Java Spring Boot Backend** (Port 8080)
3. **Django Frontend** (Port 8000)

**Estimated Time**: 15-30 minutes for first-time setup

---

## 📋 Prerequisites Check

Run these commands to verify you have everything installed:

```bash
# Check Java
java -version
# Should show: openjdk version "17" or higher

# Check Python
python --version
# Should show: Python 3.8 or higher

# Check MySQL
mysql --version
# Should show: mysql Ver 8.0 or higher

# Check Maven
mvn --version
# Should show: Apache Maven 3.8 or higher
```

**If any are missing**, install from:
- Java: https://www.oracle.com/java/technologies/downloads/
- Python: https://www.python.org/downloads/
- MySQL: https://dev.mysql.com/downloads/mysql/
- Maven: https://maven.apache.org/download.cgi

---

## 🗄️ Step 1: Setup MySQL Database

### Windows Users

```bash
# Start MySQL Service (should auto-start)
# If not running, start it manually:
net start MySQL80

# Or using Chocolatey:
choco install mysql
```

### macOS Users

```bash
# Start MySQL with Homebrew
brew services start mysql

# Or manually
mysql.server start
```

### Linux Users (Ubuntu/Debian)

```bash
# Start MySQL service
sudo systemctl start mysql

# Verify it's running
sudo systemctl status mysql
```

### Create Database and User

```bash
# Open MySQL command line
mysql -u root -p

# When prompted, enter your MySQL root password
# (If you haven't set one, just press Enter)
```

Then copy and paste these commands in MySQL:

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
EXIT;
```

### Initialize Database Schema

Download and run the SQL schema file:

```bash
# Save this file as schema.sql in your project root

mysql -u billing_user -p grocery_billing < schema.sql
# When prompted, enter: secure_password_123
```

Or manually execute the SQL (see DEPLOYMENT_GUIDE.md for full schema).

**Expected Output:**
```
Query OK, X rows affected
```

### Verify Database Setup

```bash
# Login as billing_user
mysql -u billing_user -p grocery_billing

# Inside MySQL, run:
SHOW TABLES;
# Should show: users, products, categories, bills, bill_items, payments, audit_logs, customers

SELECT COUNT(*) FROM users;
# Should show: 1 (admin user)

SELECT * FROM users;
# Should show admin user

EXIT;
```

---

## ☕ Step 2: Run Java Spring Boot Backend

### Open Terminal/Command Prompt and Navigate to Backend

```bash
# Windows
cd d:\grocery billing system\backend

# macOS/Linux
cd /path/to/grocery\ billing\ system/backend
```

### Configure Backend Settings (First Time Only)

Open `src/main/resources/application.properties` and verify:

```properties
server.port=8080
spring.datasource.url=jdbc:mysql://localhost:3306/grocery_billing
spring.datasource.username=billing_user
spring.datasource.password=secure_password_123
app.jwt.secret=your-secret-key-min-32-chars-long
app.jwt.expiration=86400000
```

### Build Backend

```bash
# Clean and build (takes 2-3 minutes first time)
mvn clean package -DskipTests

# Expected output:
# BUILD SUCCESS
# Total time: X.XXs
```

If you get an error, try:
```bash
# Clear Maven cache and rebuild
mvn clean package -U -DskipTests
```

### Run Backend

```bash
# Option 1: Using Maven (simplest)
mvn spring-boot:run

# Option 2: Using JAR file
java -jar target/grocery-billing-system-1.0.0.jar

# Option 3: On specific port if 8080 is busy
java -Dserver.port=8081 -jar target/grocery-billing-system-1.0.0.jar
```

### Verify Backend is Running

**Expected Output:**
```
Tomcat started on port(s): 8080 (http) with context path ''
Started GroceryBillingApplication in X.XXX seconds
```

**Test Backend in Another Terminal:**

```bash
# Test login endpoint
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"admin123\"}"

# Should return:
# {
#   "success": true,
#   "message": "Login successful",
#   "data": {
#     "token": "eyJhbGciOiJIUzI1NiIs...",
#     ...
#   }
# }
```

**If backend doesn't start:**
- Check port 8080 is not in use: `lsof -i :8080` (macOS/Linux) or `netstat -ano | findstr :8080` (Windows)
- Check database connection: verify MySQL is running and credentials are correct
- Check Java version: `java -version` should be 17 or higher

---

## 🐍 Step 3: Setup Django Frontend

### Open New Terminal/Command Prompt

```bash
# Windows
cd d:\grocery billing system\frontend

# macOS/Linux
cd /path/to/grocery\ billing\ system/frontend
```

### Create Python Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Expected: (venv) should appear at the start of your command line
```

### Install Python Dependencies

```bash
# This takes 1-2 minutes
pip install -r requirements.txt

# Verify installations
pip list | grep Django
# Should show: Django 4.2.8
```

### Configure Frontend Settings (First Time Only)

Create `.env` file in `frontend/` directory:

```properties
DEBUG=True
SECRET_KEY=your-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1
BACKEND_API_URL=http://localhost:8080
BACKEND_API_TIMEOUT=10
```

Or copy from example:
```bash
cp .env.example .env
```

### Run Django Frontend

```bash
# Make sure virtual environment is activated (should see (venv) prefix)

# Run development server
python manage.py runserver 0.0.0.0:8000

# Expected output:
# Starting development server at http://127.0.0.1:8000/
# Quit the server with CTRL-BREAK.
```

---

## ✅ Verification - Test Everything

### Test 1: Login to Frontend

Open your browser and navigate to:
```
http://localhost:8000/
```

You should see the **Login Page**:
- Username: `admin`
- Password: `admin123`

Click "Sign In" → Should redirect to **Dashboard**

### Test 2: View Products

Click **Products** in the navigation menu
- Should display products (Apple, Banana, Orange, Milk, etc.)
- Should show product names, prices, and stock

### Test 3: Create a Bill

Click **Billing** → **Create Bill** (or POS)
- Search for a product
- Select quantity
- See automatic price calculation
- Click "Create Bill"
- Should see bill confirmation

### Test 4: View Reports

Click **Reports** → **Daily Sales**
- Should show sales metrics
- Should display total sales

### Test 5: API Testing (Optional)

Using Postman or curl:

```bash
# 1. Login and get token
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Save the token from response (everything after "token": " and before the ")

# 2. Use token to get products
curl -X GET http://localhost:8080/api/v1/products \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# 3. Should return list of products
```

---

## 🎯 Accessing the Application

Once all services are running:

| Service | URL | Credentials |
|---------|-----|-------------|
| **Frontend** | http://localhost:8000 | admin / admin123 |
| **Backend API** | http://localhost:8080/api/v1 | Requires JWT token |
| **Database** | localhost:3306 | billing_user / secure_password_123 |

---

## 🛑 Stopping Services

### Stop Backend

In the terminal running the backend:
```
Ctrl + C
```

### Stop Frontend

In the terminal running Django:
```
Ctrl + C
```

### Stop MySQL

#### Windows
```bash
net stop MySQL80
```

#### macOS
```bash
brew services stop mysql
# Or
mysql.server stop
```

#### Linux
```bash
sudo systemctl stop mysql
```

---

## 🔄 Restarting Services

To restart the application later:

**Terminal 1 - Backend:**
```bash
cd backend
mvn spring-boot:run
```

**Terminal 2 - Frontend:**
```bash
cd frontend
source venv/bin/activate  # (venv\Scripts\activate on Windows)
python manage.py runserver 0.0.0.0:8000
```

**Database:** Restart MySQL service (usually auto-starts)

---

## ❌ Troubleshooting

### MySQL won't connect

```
Error: "Communications link failure"
```

**Solution:**
```bash
# Verify MySQL is running
# Windows: mysql -u root -p
# macOS: mysql -u root -p
# Linux: sudo systemctl status mysql

# Test connection
mysql -h 127.0.0.1 -u billing_user -p grocery_billing
```

### Port 8080 already in use

```
Error: "Port 8080 is in use"
```

**Solution:**
```bash
# Windows
netstat -ano | findstr :8080
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :8080
kill -9 <PID>

# Or use different port
java -Dserver.port=8081 -jar target/*.jar
```

### Port 8000 already in use

```bash
# Try different port
python manage.py runserver 0.0.0.0:8001
```

### ModuleNotFoundError: No module named 'django'

```
Error: "No module named 'django'"
```

**Solution:**
```bash
# Make sure virtual environment is activated (should see (venv) prefix)
# If not: source venv/bin/activate (or venv\Scripts\activate on Windows)

# Then install requirements
pip install -r requirements.txt
```

### BUILD FAILURE in Maven

```
Error: "BUILD FAILURE"
```

**Solution:**
```bash
# Clean and rebuild with verbose output
mvn clean package -DskipTests -X

# Or clear Maven cache
mvn clean
mvn package -DskipTests -U
```

### Can't login to frontend

```
Error: "Invalid username or password"
```

**Solution:**
1. Verify admin user exists in database:
   ```bash
   mysql -u billing_user -p grocery_billing
   SELECT * FROM users;
   EXIT;
   ```

2. Username is exactly: `admin`
3. Password is exactly: `admin123`

4. If user doesn't exist, add it:
   ```sql
   INSERT INTO users (username, password, email, role) VALUES
   ('admin', '$2a$10$slYQmyNdGzin7olVN3eq2OPST9/PgBkqquzi.Ss8KIUgO2t0jKMm6', 'admin@grocery.com', 'ADMIN');
   ```

### Frontend can't connect to backend

```
Error: "Cannot connect to server"
```

**Solution:**
1. Verify backend is running: `curl http://localhost:8080/api/v1/auth/login`

2. Check frontend configuration (.env):
   ```
   BACKEND_API_URL=http://localhost:8080
   ```

3. If backend is on different machine, update URL to:
   ```
   BACKEND_API_URL=http://your-server-ip:8080
   ```

4. Clear browser cache and refresh

---

## 📊 Default Test Data

### Admin User
```
Username: admin
Password: admin123
Role: ADMIN
```

### Sample Products (Auto-inserted)
```
1. Apple - ₹50
2. Banana - ₹30
3. Orange - ₹45
4. Milk (1L) - ₹65
5. Bread - ₹40
6. Eggs (Dozen) - ₹80
```

---

## 📈 Next Steps

After everything is running:

1. **Create a Bill**: Billing → Create Bill → Add products → Print invoice
2. **Generate Reports**: Reports → Daily Sales → View metrics
3. **Manage Products**: Products → Create new product → Set price and stock
4. **Manage Customers**: Customers → Add customer → Track loyalty points
5. **User Management**: Settings → Manage users and roles

---

## 🆘 Still Having Issues?

1. **Check Logs**:
   - Backend: Look at console output (error messages)
   - Frontend: `python manage.py runserver` shows errors
   - Database: `mysql -u billing_user -p` and check tables

2. **Read Documentation**:
   - Backend setup: [backend/README.md](backend/README.md)
   - Frontend setup: [frontend/README.md](frontend/README.md)
   - Deployment: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
   - API docs: [REST_API_SPECIFICATION.md](REST_API_SPECIFICATION.md)

3. **Verify Versions**:
   ```bash
   java -version          # Should be 17+
   python --version       # Should be 3.8+
   mysql --version        # Should be 8.0+
   mvn --version          # Should be 3.8+
   ```

4. **Reset Everything**:
   ```bash
   # Stop all services
   # Delete database
   mysql -u root -p
   DROP DATABASE grocery_billing;
   
   # Recreate database
   CREATE DATABASE grocery_billing CHARACTER SET utf8mb4;
   USE grocery_billing;
   # Run schema.sql
   
   # Rebuild backend
   cd backend
   mvn clean package -DskipTests
   
   # Start fresh
   ```

---

## ✨ Project Structure

```
grocery billing system/
├── backend/                          # Java Spring Boot
│   ├── pom.xml                      # Maven configuration
│   ├── src/
│   │   ├── main/java/...           # Java source code
│   │   └── main/resources/          # Configuration files
│   └── target/                      # Built JAR file
│
├── frontend/                         # Django application
│   ├── manage.py                    # Django management
│   ├── requirements.txt             # Python dependencies
│   ├── config/                      # Django settings
│   ├── apps/                        # Django apps
│   ├── templates/                   # HTML templates
│   └── static/                      # CSS, JavaScript
│
└── Documentation/
    ├── README.md
    ├── DEPLOYMENT_GUIDE.md
    ├── QUICK_START.md
    └── ... (other guides)
```

---

## 🎉 Success Checklist

After running the project, you should be able to:

- ✅ Login with admin/admin123
- ✅ View dashboard with sales metrics
- ✅ Browse products list
- ✅ Create a new bill/invoice
- ✅ Add items to bill with auto-calculation
- ✅ Print invoice
- ✅ View daily sales report
- ✅ See real-time clock in header
- ✅ Access backend API with JWT token
- ✅ All calculations working correctly

---

## 📞 Quick Commands Reference

### All-in-One Startup Script (macOS/Linux)

Save as `run.sh`:
```bash
#!/bin/bash

# Start MySQL
echo "Starting MySQL..."
brew services start mysql  # or: sudo systemctl start mysql

# Start Backend
echo "Starting Backend..."
cd backend
mvn spring-boot:run &
BACKEND_PID=$!

# Wait for backend to start
sleep 10

# Start Frontend
echo "Starting Frontend..."
cd ../frontend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py runserver 0.0.0.0:8000

# Stop script
trap "kill $BACKEND_PID" EXIT
```

Run with:
```bash
chmod +x run.sh
./run.sh
```

---

**Ready to start? Begin with Step 1 (MySQL Setup) and follow through all steps!**

Happy coding! 🚀
