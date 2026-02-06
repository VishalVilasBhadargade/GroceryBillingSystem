# 🎯 Quick Start - Run Your Project NOW

## Choose Your Operating System

### Windows Users

```bash
# 1. Open Command Prompt
# 2. Navigate to project folder
cd d:\grocery billing system

# 3. Run the startup script
start.bat

# The script will:
# ✓ Check Java, Python, MySQL
# ✓ Create database
# ✓ Build backend
# ✓ Setup frontend
# ✓ Start all services in separate windows
# ✓ Open browser to http://localhost:8000
```

**Expected**: 3 new windows open (Backend, Frontend, and Main)

---

### macOS/Linux Users

```bash
# 1. Open Terminal
# 2. Navigate to project folder
cd /path/to/grocery\ billing\ system

# 3. Make script executable
chmod +x start.sh

# 4. Run the startup script
./start.sh

# The script will:
# ✓ Check Java, Python, Maven, MySQL
# ✓ Start MySQL service
# ✓ Create database
# ✓ Build backend with Maven
# ✓ Setup Python virtual environment
# ✓ Install dependencies
# ✓ Start Backend (port 8080)
# ✓ Start Frontend (port 8000)
# ✓ Open browser
```

---

## Manual Setup (If Scripts Don't Work)

### Step-by-Step Instructions

#### Step 1: Start MySQL
```bash
# Windows
net start MySQL80

# macOS
brew services start mysql

# Linux
sudo systemctl start mysql
```

#### Step 2: Create Database
```bash
mysql -u root -p
# Enter your root password

# Paste this in MySQL:
CREATE DATABASE grocery_billing CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'billing_user'@'localhost' IDENTIFIED BY 'secure_password_123';
GRANT ALL PRIVILEGES ON grocery_billing.* TO 'billing_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### Step 3: Start Backend (Terminal 1)
```bash
cd backend
mvn spring-boot:run

# Wait until you see:
# Tomcat started on port(s): 8080
```

#### Step 4: Start Frontend (Terminal 2)
```bash
cd frontend

# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# All platforms
pip install -r requirements.txt
python manage.py runserver 0.0.0.0:8000

# Wait until you see:
# Starting development server at http://127.0.0.1:8000/
```

#### Step 5: Open Browser
```
http://localhost:8000
Username: admin
Password: admin123
```

---

## ✅ Verify Everything Works

### Test 1: Login
- Open http://localhost:8000/
- Enter: `admin` / `admin123`
- You should see the Dashboard ✓

### Test 2: Products
- Click "Products" in menu
- Should display: Apple, Banana, Orange, Milk, etc. ✓

### Test 3: Create Bill
- Click "Billing"
- Add products with quantities
- See automatic price calculation ✓

### Test 4: API
```bash
# Get token
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Should return:
# {"success":true,"data":{"token":"eyJhb...",...}}
```

---

## 🔍 Troubleshooting Quick Fixes

### "Port 8080 already in use"
```bash
# Kill process using port 8080
# Windows
netstat -ano | findstr :8080
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :8080
kill -9 <PID>
```

### "Can't connect to MySQL"
```bash
# Check MySQL is running
mysql -u root -p

# If it fails, start MySQL:
# Windows: net start MySQL80
# macOS: brew services start mysql
# Linux: sudo systemctl start mysql
```

### "ModuleNotFoundError: No module named 'django'"
```bash
# Activate virtual environment
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Then install
pip install -r requirements.txt
```

### "Maven build fails"
```bash
# Try clean build
mvn clean package -DskipTests -U

# Check Java version (should be 17+)
java -version
```

---

## 📊 Service Status

Once running, check services:

```bash
# Backend is running (port 8080)
curl http://localhost:8080/api/v1/auth/login

# Frontend is running (port 8000)
curl http://localhost:8000/

# Database is running
mysql -u billing_user -p -e "SELECT COUNT(*) FROM grocery_billing.users;"
# Password: secure_password_123
```

---

## 🎮 What You Can Do Now

Once logged in (`admin` / `admin123`):

1. **Dashboard** - View sales metrics and low stock alerts
2. **Products** - Browse, search, add, edit products
3. **Billing** - Create bills with automatic calculations
4. **Customers** - Manage customer profiles and loyalty points
5. **Payments** - Process payments and refunds
6. **Reports** - View daily sales, inventory, and product reports
7. **Settings** - Manage user profile

---

## 📁 Project Files

```
grocery billing system/
├── backend/                    # Java Spring Boot
├── frontend/                   # Django
├── start.bat                   # Windows startup (double-click)
├── start.sh                    # macOS/Linux startup (run ./start.sh)
├── RUN_PROJECT.md             # Detailed instructions
├── DEPLOYMENT_GUIDE.md         # Production setup
├── REST_API_SPECIFICATION.md   # API endpoints
└── ... (other documentation)
```

---

## 🆘 Need Help?

1. **Check RUN_PROJECT.md** - Comprehensive setup guide
2. **Check DEPLOYMENT_GUIDE.md** - Detailed configuration
3. **Check REST_API_SPECIFICATION.md** - API documentation
4. **Backend logs** - Check console output for errors
5. **Frontend logs** - Check Django console output

---

## 🚀 You're All Set!

Everything is configured and ready. Just run:

**Windows:**
```
Double-click start.bat
OR
cmd → start.bat
```

**macOS/Linux:**
```bash
./start.sh
```

The application will be available at: **http://localhost:8000**

---

## 📞 Default Credentials

| Service | URL | Username | Password |
|---------|-----|----------|----------|
| **Frontend** | http://localhost:8000 | admin | admin123 |
| **Backend API** | http://localhost:8080/api/v1 | (JWT required) | - |
| **Database** | localhost:3306 | billing_user | secure_password_123 |

---

**Happy Testing! 🎉**

If you encounter any issues, see "Troubleshooting Quick Fixes" above or check the detailed guides.
