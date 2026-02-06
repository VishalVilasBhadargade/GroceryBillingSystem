# 🚀 EASY SETUP - Just Follow These Steps!

## ⚠️ You Need To Install These First:

### 1. Install MySQL (Database)
- Download: https://dev.mysql.com/downloads/installer/
- Choose: "MySQL Installer for Windows"
- Install with default settings
- **Remember the root password you set!**
- After installation, MySQL should start automatically

### 2. Install Maven (Build Tool)
- Download: https://maven.apache.org/download.cgi
- Click: "apache-maven-3.9.6-bin.zip"
- Extract the ZIP file to: `C:\maven`
- Add to Windows PATH:
  1. Press `Windows Key`, type "environment"
  2. Click "Edit system environment variables"
  3. Click "Environment Variables"
  4. Under "System Variables", find "Path", click "Edit"
  5. Click "New"
  6. Add: `C:\maven\bin`
  7. Click "OK" on all windows
  8. **Close and reopen Command Prompt**

## ✅ After Installing Everything:

### Option 1: Automatic Setup (Easiest!)
1. Double-click: `SIMPLE_SETUP.bat`
2. Follow the prompts
3. Wait 2-3 minutes for build
4. Website opens automatically!

### Option 2: Manual Setup (Step by Step)

**Step 1: Open Command Prompt**
- Press `Windows Key + R`
- Type: `cmd`
- Press Enter

**Step 2: Go to project folder**
```bash
cd "d:\grocery billing system"
```

**Step 3: Create database**
```bash
mysql -u root -p
```
(Enter your MySQL root password)

Then copy-paste this:
```sql
CREATE DATABASE IF NOT EXISTS grocery_billing CHARACTER SET utf8mb4;
USE grocery_billing;
CREATE TABLE users (id BIGINT PRIMARY KEY AUTO_INCREMENT, username VARCHAR(50) UNIQUE, password VARCHAR(255), email VARCHAR(100), full_name VARCHAR(100), role VARCHAR(20));
INSERT INTO users VALUES (1, 'admin', '$2a$10$N9qo8UQOEtWpAjR8RVLzvuIKCqCr8lfKkEkWqHlRLqqM8qEYJNHn2', 'admin@grocery.com', 'Administrator', 'ADMIN');
EXIT;
```

**Step 4: Build Backend**
```bash
cd backend
mvn clean package -DskipTests
```
(Wait 2-3 minutes...)

**Step 5: Start Backend (Don't close this window!)**
```bash
mvn spring-boot:run
```
Wait until you see: "Started GroceryBillingApplication"

**Step 6: Open NEW Command Prompt window**
```bash
cd "d:\grocery billing system\frontend"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver 0.0.0.0:8000
```

**Step 7: Open Browser**
```
http://localhost:8000
```

## 🎉 Login:
```
Username: admin
Password: admin123
```

---

## 🆘 Problems?

### "MySQL not found"
- Make sure MySQL is installed
- Check if MySQL service is running:
  - Press `Windows Key`, type "services"
  - Find "MySQL80" or "MySQL"
  - Right-click → Start

### "Maven not found"
- Make sure you added `C:\maven\bin` to PATH
- Close and reopen Command Prompt
- Test: `mvn --version`

### "Port 8080 already in use"
```bash
netstat -ano | findstr :8080
taskkill /PID <number> /F
```

### "Can't connect to MySQL"
- Check MySQL is running in Services
- Try connecting: `mysql -u root -p`
- If password wrong, reset MySQL password

---

## 📞 Quick Check:
1. ✓ MySQL installed and running?
2. ✓ Maven installed and in PATH?
3. ✓ Java installed? (You have this ✓)
4. ✓ Python installed? (You have this ✓)

**Once all ✓, double-click: `SIMPLE_SETUP.bat`**
