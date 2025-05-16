import csv
import uuid
import mysql.connector
from mysql.connector import Error

def connect_db():
    """Connect to the MySQL server"""
    try:
        return mysql.connector.connect(
            host='localhost',
            user='root',                  # MySQL username
            password='',      # MySQL password
        )
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def create_database(connection):
    """Create ALX_prodev database if not exists"""
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
        connection.commit()
    except Error as e:
        print(f"Error creating database: {e}")

def connect_to_prodev():
    """Connect to ALX_prodev database"""
    try:
        return mysql.connector.connect(
            host='localhost',
            user='root',                    # MySQL username
            password='',        # MySQL password
            database='ALX_prodev'
        )
    except Error as e:
        print(f"Error connecting to ALX_prodev: {e}")
        return None

def create_table(connection):
    """Create user_data table if not exists"""
    try:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_data (
                user_id BINARY(16) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                age DECIMAL(5,2) NOT NULL
            )
        """)
        connection.commit()
    except Error as e:
        print(f"Error creating table: {e}")

def insert_data(connection, csv_file):
    """Insert data from CSV file if table is empty"""
    try:
        cursor = connection.cursor()
        
        # Check if table is empty
        cursor.execute("SELECT COUNT(*) FROM user_data")
        if cursor.fetchone()[0] > 0:
            print("Table already contains data - skipping import")
            return

        # Read CSV file
        with open(csv_file, 'r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                cursor.execute("""
                    INSERT INTO user_data (user_id, name, email, age)
                    VALUES (%s, %s, %s, %s)
                """, (
                    uuid.uuid4().bytes,
                    row['name'],
                    row['email'],
                    float(row['age'])
                ))
        
        connection.commit()
        print(f"Successfully imported data from {csv_file}")
        
    except Error as e:
        print(f"Database error: {e}")
        connection.rollback()
    except Exception as e:
        print(f"Error processing CSV file: {e}")
