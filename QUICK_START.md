# Grocery Billing System - Quick Start Guide

## 📋 Prerequisites

### System Requirements
- Windows 10/11, macOS, or Linux
- 4GB RAM minimum (8GB recommended)
- 500MB disk space minimum
- Internet connection for package installation

### Software Requirements
1. **Java Development Kit (JDK) 17 LTS**
   - Download: https://www.oracle.com/java/technologies/downloads/
   - Verify: `java -version`

2. **Python 3.8+**
   - Download: https://www.python.org/downloads/
   - Verify: `python --version`

3. **MySQL 8.0+**
   - Download: https://www.mysql.com/downloads/
   - Verify: `mysql --version`

4. **Maven 3.8+** (for Java builds)
   - Download: https://maven.apache.org/download.cgi
   - Verify: `mvn --version`

5. **Git** (optional, for version control)
   - Download: https://git-scm.com/

---

## 🚀 Installation Steps

### Step 1: Prepare the Environment

#### Create Project Directory
```bash
mkdir grocery-billing-system
cd grocery-billing-system
```

#### Create Virtual Environment (Frontend)
```bash
# Windows
python -m venv frontend/venv
frontend\venv\Scripts\activate

# macOS/Linux
python3 -m venv frontend/venv
source frontend/venv/bin/activate
```

#### Set JAVA_HOME (if needed)
```bash
# Windows (PowerShell)
[Environment]::SetEnvironmentVariable('JAVA_HOME', 'C:\Program Files\Java\jdk-17.0.0', 'User')

# macOS/Linux
export JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk-17.0.0.jdk/Contents/Home
```

---

### Step 2: Configure Database

#### 1. Create MySQL Database
```bash
mysql -u root -p
```

```sql
-- Create main database
CREATE DATABASE grocery_billing_db CHARACTER SET utf8mb4;

-- Create user (optional)
CREATE USER 'grocery_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON grocery_billing_db.* TO 'grocery_user'@'localhost';
FLUSH PRIVILEGES;

EXIT;
```

#### 2. Verify Connection
```bash
mysql -u root -p grocery_billing_db -e "SELECT DATABASE();"
```

---

### Step 3: Set Up Backend (Java)

#### 1. Navigate to Backend
```bash
cd backend
```

#### 2. Configure Application Properties
Edit `src/main/resources/application.properties`:
```properties
# Database Configuration
spring.datasource.url=jdbc:mysql://localhost:3306/grocery_billing_db?useSSL=false&serverTimezone=UTC
spring.datasource.username=root
spring.datasource.password=your_mysql_password

# Server Configuration
server.port=8080

# JWT Configuration
jwt.secret=your-secure-secret-key-change-in-production
jwt.expiration=86400000
```

#### 3. Build Backend
```bash
mvn clean install
```

#### 4. Start Backend Server
```bash
mvn spring-boot:run
```

✅ **Backend running on:** http://localhost:8080

Wait until you see: `Tomcat started on port(s): 8080`

---

### Step 4: Set Up Frontend (Django)

#### 1. Navigate to Frontend
```bash
cd ../frontend
```

#### 2. Activate Virtual Environment
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Configure Environment
Create `.env` file:
```
DEBUG=True
SECRET_KEY=django-insecure-change-in-production
BACKEND_API_URL=http://localhost:8080/api/v1
DB_NAME=grocery_billing_frontend
DB_USER=postgres
DB_PASSWORD=password
```

#### 5. Create Database Tables
```bash
python manage.py migrate
```

#### 6. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

#### 7. Create Superuser (Optional)
```bash
python manage.py createsuperuser
# Follow prompts
```

#### 8. Start Frontend Server
```bash
python manage.py runserver
```

✅ **Frontend running on:** http://localhost:8000

---

## 🔑 Access the Application

### Login Page
```
URL: http://localhost:8000/auth/login/
```

### Demo Credentials

#### Admin User
```
Username: admin
Password: admin123
Role: ADMIN
```

#### Cashier User
```
Username: cashier
Password: password123
Role: CASHIER
```

#### Manager User
```
Username: manager
Password: password123
Role: MANAGER
```

### Dashboard
After login:
```
URL: http://localhost:8000/
```

---

## 📱 Main Features to Try

### 1. **Product Management**
```
Navigation: Products → View Products
- View all products
- Search by name/SKU/barcode
- Add new product (Inventory Manager/Admin)
- Edit product details
- Delete product
```

### 2. **Customer Management**
```
Navigation: Customers → View Customers
- View all customers
- Search customers
- Add new customer (Manager/Admin)
- View customer details
- Loyalty points tracking
```

### 3. **Billing (POS)**
```
Navigation: Billing → Create Bill
- Search products by name or barcode
- Add items to cart
- Adjust quantities
- Apply discount
- Calculate tax
- Complete sale
```

### 4. **Reporting**
```
Navigation: Reports
- Daily sales report (select date)
- Sales by date range
- Inventory status report
- Product sales analysis
```

---

## 🛠️ Troubleshooting

### Backend Issues

#### Port 8080 Already in Use
```bash
# Windows
netstat -ano | findstr :8080
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :8080
kill -9 <PID>
```

#### Database Connection Error
```
Error: Could not connect to database

Solution:
1. Verify MySQL is running
2. Check username/password in application.properties
3. Verify database name is correct
4. Ensure grocery_billing_db exists
```

#### Maven Build Failures
```bash
# Clear cache and rebuild
mvn clean install -U
```

### Frontend Issues

#### ModuleNotFoundError
```bash
# Upgrade pip and reinstall
pip install --upgrade pip
pip install -r requirements.txt
```

#### Port 8000 Already in Use
```bash
# Use different port
python manage.py runserver 8001
```

#### Database Migration Error
```bash
# Reset migrations
python manage.py migrate zero
python manage.py migrate
```

#### Static Files Not Loading
```bash
python manage.py collectstatic --clear --noinput
```

### API Connection Issues

#### "Cannot connect to API"
1. Verify backend is running on port 8080
2. Check `BACKEND_API_URL` in Django settings
3. Verify no firewall blocking communication
4. Check browser console for CORS errors

```
Solution: Set correct BACKEND_API_URL=http://localhost:8080/api/v1
```

---

## 📊 Test the APIs

### Using Postman/Insomnia

#### 1. Login
```
POST http://localhost:8080/api/v1/auth/login
Content-Type: application/json

{
    "username": "admin",
    "password": "admin123"
}
```

#### 2. Get Products
```
GET http://localhost:8080/api/v1/products
Authorization: Bearer <token_from_login>
```

#### 3. Create Product
```
POST http://localhost:8080/api/v1/products
Authorization: Bearer <token>
Content-Type: application/json

{
    "productName": "Apple",
    "sku": "APPLE001",
    "barcode": "1234567890",
    "categoryId": 1,
    "supplierId": 1,
    "costPrice": 1.50,
    "sellingPrice": 2.99,
    "quantityOnHand": 100,
    "reorderLevel": 20,
    "description": "Fresh red apples"
}
```

---

## 🔐 Security Considerations

### Before Going to Production

1. **Change Default Credentials**
   ```
   Create new admin user with strong password
   Delete demo users
   ```

2. **Update JWT Secret**
   ```properties
   jwt.secret=your-very-long-secure-secret-key-min-32-chars
   ```

3. **Update Django Secret**
   ```python
   SECRET_KEY = 'your-new-secure-secret-key'
   ```

4. **Enable HTTPS**
   ```properties
   # In application.properties
   server.ssl.key-store=classpath:keystore.p12
   server.ssl.key-store-type=PKCS12
   ```

5. **Configure Database**
   - Use strong passwords
   - Restrict database user permissions
   - Enable MySQL SSL
   - Regular backups

6. **Set Up Firewall**
   - Close unnecessary ports
   - Allow only required traffic
   - Configure rate limiting

---

## 📈 Performance Optimization

### Backend
```bash
# Increase JVM memory
set JAVA_OPTS=-Xmx1024m -Xms512m

# Enable compression
spring.compression.enabled=true
```

### Frontend
```bash
# Use Gunicorn for production
pip install gunicorn
gunicorn config.wsgi:application --workers 4
```

### Database
```sql
-- Create indexes on frequently queried columns
CREATE INDEX idx_product_barcode ON products(barcode);
CREATE INDEX idx_bill_created_at ON bills(created_at);
```

---

## 📚 Additional Resources

### Documentation Files
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Complete project overview
- [backend/README.md](backend/README.md) - Backend documentation
- [frontend/README.md](frontend/README.md) - Frontend documentation
- [frontend/API_INTEGRATION_GUIDE.md](frontend/API_INTEGRATION_GUIDE.md) - API integration details

### API Documentation
- Swagger UI (Backend): http://localhost:8080/swagger-ui.html (requires dependency)
- Postman Collection: Import from `docs/postman_collection.json`

### Useful Commands

#### Backend
```bash
# Run tests
mvn test

# Generate jar
mvn package

# Clean build
mvn clean install
```

#### Frontend
```bash
# Run tests
python manage.py test

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Clear cache
python manage.py clear_cache
```

---

## ✅ Verification Checklist

After setup, verify everything is working:

- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Can access login page (http://localhost:8000)
- [ ] Can login with demo credentials
- [ ] Can view dashboard
- [ ] Can view products list
- [ ] Can view customers list
- [ ] Can create a bill
- [ ] Can process a payment
- [ ] Can view reports
- [ ] API responses show in browser console
- [ ] No 404 or 500 errors in logs

---

## 🚢 Deployment

### Local Network Access
```bash
# Backend accessible from other machines
# Change server.address in application.properties
server.address=0.0.0.0
server.port=8080

# Frontend accessible from other machines
python manage.py runserver 0.0.0.0:8000
```

### Docker (Optional)
```bash
# Build images
docker build -t grocery-backend backend/
docker build -t grocery-frontend frontend/

# Run with docker-compose
docker-compose up
```

### Cloud Deployment (AWS, Azure, Google Cloud)
See deployment guides in respective cloud provider documentation.

---

## 📞 Support

If you encounter any issues:

1. **Check logs** - Review server console and log files
2. **Verify configuration** - Ensure all credentials are correct
3. **Check ports** - Ensure ports 8000, 8080, 3306 are available
4. **Test API** - Use Postman to test backend directly
5. **Review documentation** - Check README files in backend and frontend

---

## 🎉 You're All Set!

Your Grocery Billing System is now ready to use. Start with the dashboard and explore all the features!

**Next Steps:**
1. Add some products
2. Create a few customers
3. Practice using the POS interface
4. Generate reports
5. Customize based on your needs

Happy coding! 🚀
