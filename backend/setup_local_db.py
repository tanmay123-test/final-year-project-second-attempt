#!/usr/bin/env python3
"""
Local Database Setup Script
Sets up PostgreSQL database for local development
"""
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()

def setup_local_database():
    """Create local PostgreSQL database and tables"""
    
    # Connection to PostgreSQL server (without database)
    conn_params = {
        'host': 'localhost',
        'port': 5432,
        'user': 'postgres',
        'password': 'password'
    }
    
    try:
        # Connect to PostgreSQL server
        print("🔌 Connecting to PostgreSQL server...")
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        print("📊 Creating 'vedant_db' database...")
        cursor.execute("CREATE DATABASE vedant_db;")
        print("✅ Database created successfully")
        
        # Close connection to server
        cursor.close()
        conn.close()
        
        # Connect to the new database
        print("🔌 Connecting to 'vedant_db' database...")
        db_url = 'postgresql://postgres:password@localhost:5432/vedant_db'
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Create basic tables
        print("📋 Creating tables...")
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(100),
                phone VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Workers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workers (
                id SERIAL PRIMARY KEY,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(100),
                phone VARCHAR(20),
                service VARCHAR(50),
                is_online BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Services table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS services (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                price DECIMAL(10,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Bookings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                worker_id INTEGER REFERENCES workers(id),
                service_type VARCHAR(100),
                address TEXT,
                booking_date DATE,
                time_slot VARCHAR(20),
                status VARCHAR(20) DEFAULT 'PENDING',
                price DECIMAL(10,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        print("✅ Tables created successfully")
        
        # Insert sample data
        print("📝 Inserting sample data...")
        
        # Sample services
        cursor.execute("""
            INSERT INTO services (name, description, price) VALUES
            ('General Cleaning', 'Complete home cleaning service', 500.00),
            ('Deep Cleaning', 'Thorough deep cleaning service', 800.00),
            ('Kitchen Cleaning', 'Kitchen specialized cleaning', 400.00),
            ('Bathroom Cleaning', 'Bathroom specialized cleaning', 300.00)
            ON CONFLICT DO NOTHING;
        """)
        
        # Sample worker
        cursor.execute("""
            INSERT INTO workers (email, password_hash, full_name, phone, service) VALUES
            ('worker@example.com', '$2b$12$hashedpassword', 'John Worker', '1234567890', 'housekeeping')
            ON CONFLICT DO NOTHING;
        """)
        
        print("✅ Sample data inserted")
        
        # Commit and close
        conn.commit()
        cursor.close()
        conn.close()
        
        print("🎉 Local database setup complete!")
        print("📊 Database URL: postgresql://postgres:password@localhost:5432/vedant_db")
        print("🚀 You can now run: python app.py")
        
    except psycopg2.OperationalError as e:
        if "connection" in str(e).lower():
            print("❌ Cannot connect to PostgreSQL server")
            print("💡 Make sure PostgreSQL is installed and running:")
            print("   1. Install PostgreSQL: https://www.postgresql.org/download/")
            print("   2. Start PostgreSQL service")
            print("   3. Verify connection: psql -h localhost -U postgres")
        else:
            print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Setup error: {e}")

if __name__ == "__main__":
    setup_local_database()
