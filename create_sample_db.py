#!/usr/bin/env python3
"""Create a comprehensive sample SQLite database for testing"""

import sqlite3
import random
from datetime import datetime, timedelta

def create_sample_database():
    """Create sample_db.sqlite with comprehensive test data"""
    
    conn = sqlite3.connect('sample_db.sqlite')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            city TEXT,
            age INTEGER,
            registration_date DATE,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER,
            price REAL NOT NULL,
            stock_quantity INTEGER DEFAULT 0,
            description TEXT,
            created_date DATE,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            order_date DATE,
            total_amount REAL,
            status TEXT DEFAULT 'pending',
            shipping_address TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            unit_price REAL,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            position TEXT,
            department TEXT,
            salary REAL,
            hire_date DATE,
            manager_id INTEGER,
            FOREIGN KEY (manager_id) REFERENCES employees (id)
        )
    ''')
    
    # Insert sample data
    
    # Categories
    categories = [
        ('Electronics', 'Electronic devices and gadgets'),
        ('Clothing', 'Fashion and apparel'),
        ('Books', 'Books and educational materials'),
        ('Home & Garden', 'Home improvement and gardening'),
        ('Sports', 'Sports equipment and accessories'),
        ('Toys', 'Toys and games for children'),
        ('Food & Beverages', 'Food items and drinks'),
        ('Health & Beauty', 'Health and beauty products')
    ]
    
    cursor.executemany('INSERT INTO categories (name, description) VALUES (?, ?)', categories)
    
    # Customers
    moroccan_names = [
        'Naoufal Elouahabi', 'Lina Haddad', 'Karim Benali', 'Sofia Rahimi', 'Amine Mansouri',
        'Yasmine Khatib', 'Omar Idrissi', 'Nour Zahra', 'Hakim Belkacem', 'Lamia Chafai',
        'Samir Akil', 'Hiba Ouarda', 'Mehdi Skalli', 'Salma Idriss', 'Rachid Bensaid',
        'Kawtar Lahlou', 'Anas Toumi', 'Soukaina Chami', 'Walid Naciri', 'Meriem Othmani',
        'Youssef Alami', 'Fatima Bennani', 'Ahmed Tazi', 'Khadija Fassi', 'Mohamed Berrada',
        'Aicha Semlali', 'Hassan Kettani', 'Zineb Chraibi', 'Abdellatif Hajji', 'Rajae Squalli'
    ]
    
    cities = ['Casablanca', 'Rabat', 'Marrakech', 'Fes', 'Tangier', 'Agadir', 'Meknes', 'Oujda', 'Tetouan', 'Kenitra']
    
    customers_data = []
    for i, name in enumerate(moroccan_names, 1):
        email = name.lower().replace(' ', '.') + '@example.com'
        phone = f'+212{random.randint(600000000, 799999999)}'
        city = random.choice(cities)
        age = random.randint(18, 65)
        reg_date = datetime.now() - timedelta(days=random.randint(1, 1000))
        is_active = random.choice([True, False])
        
        customers_data.append((name, email, phone, city, age, reg_date.date(), is_active))
    
    cursor.executemany('''
        INSERT INTO customers (name, email, phone, city, age, registration_date, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', customers_data)
    
    # Products
    products_data = [
        ('iPhone 15', 1, 999.99, 50, 'Latest Apple smartphone'),
        ('Samsung Galaxy S24', 1, 899.99, 30, 'Android flagship phone'),
        ('MacBook Pro', 1, 1999.99, 15, 'Professional laptop'),
        ('Dell XPS 13', 1, 1299.99, 20, 'Ultrabook laptop'),
        ('Sony Headphones', 1, 299.99, 100, 'Noise-canceling headphones'),
        
        ('Jeans', 2, 79.99, 200, 'Classic blue jeans'),
        ('T-Shirt', 2, 19.99, 500, 'Cotton t-shirt'),
        ('Sneakers', 2, 129.99, 80, 'Running sneakers'),
        ('Jacket', 2, 199.99, 40, 'Winter jacket'),
        
        ('Python Programming', 3, 49.99, 60, 'Learn Python programming'),
        ('Data Science Handbook', 3, 59.99, 35, 'Data science guide'),
        ('Fiction Novel', 3, 14.99, 150, 'Bestselling fiction'),
        
        ('Coffee Maker', 4, 89.99, 25, 'Automatic coffee maker'),
        ('Garden Tools Set', 4, 149.99, 15, 'Complete gardening kit'),
        ('LED Light Bulbs', 4, 12.99, 300, 'Energy efficient bulbs'),
        
        ('Football', 5, 29.99, 100, 'Professional football'),
        ('Tennis Racket', 5, 199.99, 20, 'Carbon fiber racket'),
        ('Yoga Mat', 5, 39.99, 75, 'Non-slip yoga mat'),
        
        ('LEGO Set', 6, 79.99, 40, 'Building blocks set'),
        ('Board Game', 6, 34.99, 60, 'Family board game'),
        
        ('Organic Coffee', 7, 24.99, 200, 'Premium organic coffee beans'),
        ('Green Tea', 7, 15.99, 150, 'Organic green tea'),
        
        ('Vitamin C', 8, 19.99, 100, 'Vitamin C supplements'),
        ('Face Cream', 8, 45.99, 80, 'Anti-aging face cream')
    ]
    
    for product in products_data:
        created_date = datetime.now() - timedelta(days=random.randint(1, 365))
        cursor.execute('''
            INSERT INTO products (name, category_id, price, stock_quantity, description, created_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', product + (created_date.date(),))
    
    # Employees
    employees_data = [
        ('Ahmed Benali', 'CEO', 'Management', 150000.00, '2020-01-15', None),
        ('Fatima Alami', 'CTO', 'Technology', 120000.00, '2020-02-01', 1),
        ('Omar Tazi', 'Sales Manager', 'Sales', 80000.00, '2021-03-10', 1),
        ('Khadija Fassi', 'Developer', 'Technology', 70000.00, '2021-06-15', 2),
        ('Youssef Berrada', 'Developer', 'Technology', 65000.00, '2022-01-20', 2),
        ('Aicha Semlali', 'Sales Rep', 'Sales', 45000.00, '2022-04-01', 3),
        ('Hassan Kettani', 'Sales Rep', 'Sales', 47000.00, '2022-05-15', 3),
        ('Zineb Chraibi', 'HR Manager', 'Human Resources', 75000.00, '2021-08-01', 1),
        ('Abdellatif Hajji', 'Accountant', 'Finance', 55000.00, '2022-02-10', 1),
        ('Rajae Squalli', 'Marketing Manager', 'Marketing', 70000.00, '2021-11-01', 1)
    ]
    
    cursor.executemany('''
        INSERT INTO employees (name, position, department, salary, hire_date, manager_id)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', employees_data)
    
    # Orders
    statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
    
    for i in range(100):  # 100 orders
        customer_id = random.randint(1, 30)
        order_date = datetime.now() - timedelta(days=random.randint(1, 180))
        status = random.choice(statuses)
        
        cursor.execute('''
            INSERT INTO orders (customer_id, order_date, total_amount, status, shipping_address)
            VALUES (?, ?, ?, ?, ?)
        ''', (customer_id, order_date.date(), 0, status, f'Address {i+1}, Morocco'))
        
        order_id = cursor.lastrowid
        
        # Order items
        num_items = random.randint(1, 5)
        total_amount = 0
        
        for _ in range(num_items):
            product_id = random.randint(1, 24)
            quantity = random.randint(1, 3)
            
            # Get product price
            cursor.execute('SELECT price FROM products WHERE id = ?', (product_id,))
            unit_price = cursor.fetchone()[0]
            
            cursor.execute('''
                INSERT INTO order_items (order_id, product_id, quantity, unit_price)
                VALUES (?, ?, ?, ?)
            ''', (order_id, product_id, quantity, unit_price))
            
            total_amount += quantity * unit_price
        
        # Update order total
        cursor.execute('UPDATE orders SET total_amount = ? WHERE id = ?', (total_amount, order_id))
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX idx_customers_city ON customers(city)')
    cursor.execute('CREATE INDEX idx_products_category ON products(category_id)')
    cursor.execute('CREATE INDEX idx_orders_customer ON orders(customer_id)')
    cursor.execute('CREATE INDEX idx_orders_date ON orders(order_date)')
    
    # Create a view
    cursor.execute('''
        CREATE VIEW customer_orders AS
        SELECT 
            c.name as customer_name,
            c.city,
            o.order_date,
            o.total_amount,
            o.status
        FROM customers c
        JOIN orders o ON c.id = o.customer_id
    ''')
    
    conn.commit()
    conn.close()
    
    print("✅ Sample database 'sample_db.sqlite' created successfully!")
    print("📊 Database contains:")
    print("   - 30 customers")
    print("   - 8 categories")
    print("   - 24 products")
    print("   - 10 employees")
    print("   - 100 orders with items")
    print("   - Indexes and views")
    print("   - Foreign key relationships")

if __name__ == "__main__":
    create_sample_database()