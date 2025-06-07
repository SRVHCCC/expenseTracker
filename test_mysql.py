import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

try:
    conn = mysql.connector.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        user=os.getenv('MYSQL_USER', 'himanshu123'),
        password=os.getenv('MYSQL_PASSWORD', 'Himanshu@123'),
        database=os.getenv('MYSQL_DB', 'expense_tracker')
    )
    print('MySQL Connection successful!')
    
    # Create database if it doesn't exist
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS expense_tracker")
    print('Database created or already exists!')
    
    # Use the database
    cursor.execute("USE expense_tracker")
    
    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            password_hash VARCHAR(128)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expense (
            id INT AUTO_INCREMENT PRIMARY KEY,
            amount FLOAT NOT NULL,
            description VARCHAR(200),
            date DATETIME NOT NULL,
            user_id INT,
            FOREIGN KEY (user_id) REFERENCES user(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS earning (
            id INT AUTO_INCREMENT PRIMARY KEY,
            amount FLOAT NOT NULL,
            description VARCHAR(200),
            date DATETIME NOT NULL,
            user_id INT,
            FOREIGN KEY (user_id) REFERENCES user(id)
        )
    """)
    
    print('Tables created successfully!')
    conn.commit()
    cursor.close()
    conn.close()
    
except Exception as e:
    print('Error:', str(e)) 