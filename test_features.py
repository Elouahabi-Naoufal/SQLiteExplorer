#!/usr/bin/env python3
"""
Test script to demonstrate the new features
"""

import sys
import os
import sqlite3

def create_sample_database():
    """Create a sample database for testing"""
    db_path = "sample_data.db"
    
    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create sample tables
    cursor.execute("""
        CREATE TABLE sales (
            id INTEGER PRIMARY KEY,
            product TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            sale_date DATE NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            city TEXT,
            age INTEGER
        )
    """)
    
    # Insert sample data
    sales_data = [
        (1, 'Laptop', 'Electronics', 5, 999.99, '2024-01-15'),
        (2, 'Mouse', 'Electronics', 20, 29.99, '2024-01-16'),
        (3, 'Keyboard', 'Electronics', 15, 79.99, '2024-01-17'),
        (4, 'Monitor', 'Electronics', 8, 299.99, '2024-01-18'),
        (5, 'Desk', 'Furniture', 3, 199.99, '2024-01-19'),
        (6, 'Chair', 'Furniture', 7, 149.99, '2024-01-20'),
        (7, 'Notebook', 'Stationery', 50, 4.99, '2024-01-21'),
        (8, 'Pen', 'Stationery', 100, 1.99, '2024-01-22'),
    ]
    
    cursor.executemany("""
        INSERT INTO sales (id, product, category, quantity, price, sale_date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, sales_data)
    
    customers_data = [
        (1, 'John Doe', 'john@email.com', 'New York', 30),
        (2, 'Jane Smith', 'jane@email.com', 'Los Angeles', 25),
        (3, 'Bob Johnson', 'bob@email.com', 'Chicago', 35),
        (4, 'Alice Brown', 'alice@email.com', 'Houston', 28),
        (5, 'Charlie Wilson', 'charlie@email.com', 'Phoenix', 42),
    ]
    
    cursor.executemany("""
        INSERT INTO customers (id, name, email, city, age)
        VALUES (?, ?, ?, ?, ?)
    """, customers_data)
    
    conn.commit()
    conn.close()
    
    print(f"Sample database created: {db_path}")
    return db_path

def main():
    """Main function to test the features"""
    print("SQLite Manager - Testing New Features")
    print("=====================================")
    
    # Create sample database
    db_path = create_sample_database()
    
    print("\nNew Features Added:")
    print("1. Data Visualization")
    print("   - Bar charts, line charts, pie charts, histograms, scatter plots")
    print("   - Access via 'Visualize' button in table view")
    print("   - Right-click context menu also includes visualization option")
    
    print("\n2. Query History and Favorites")
    print("   - Automatic query history tracking")
    print("   - Save favorite queries with names and descriptions")
    print("   - Access via 'Query Manager' button in SQL executor")
    print("   - Also available in Edit menu (Ctrl+H)")
    
    print(f"\nSample database created at: {os.path.abspath(db_path)}")
    print("\nTo test the features:")
    print("1. Run: python main.py")
    print("2. Connect to the sample database")
    print("3. Open a table and click 'Visualize' to see charts")
    print("4. Use SQL executor and 'Query Manager' to manage queries")
    
    print("\nSample queries to try:")
    print("- SELECT category, SUM(quantity * price) as revenue FROM sales GROUP BY category")
    print("- SELECT * FROM customers WHERE age > 30")
    print("- SELECT product, quantity, price FROM sales ORDER BY price DESC")

if __name__ == "__main__":
    main()