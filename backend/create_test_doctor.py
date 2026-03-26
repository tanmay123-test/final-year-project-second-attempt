"""
Create Test Doctor for Healthcare Provider Login
Run this script to create a test doctor account
"""
import os
import psycopg2
import bcrypt
from dotenv import load_dotenv

load_dotenv()

def create_test_doctor():
    try:
        # Connect to database
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        
        # Test doctor data
        test_doctor = {
            'full_name': 'Dr. Test Healthcare',
            'email': 'doctor@expertease.com',
            'phone': '+1234567890',
            'service': 'healthcare',
            'specialization': 'General Medicine',
            'experience': 5,
            'clinic_location': 'Test Hospital',
            'license_number': 'TEST123456',
            'status': 'approved',
            'password': 'doctor123'
        }
        
        # Hash password
        hashed_password = bcrypt.hashpw(test_doctor['password'].encode('utf-8'), bcrypt.gensalt())
        
        # Check if doctor already exists
        cursor.execute("SELECT id FROM workers WHERE email = %s", (test_doctor['email'],))
        existing = cursor.fetchone()
        
        if existing:
            print(f"✅ Test doctor already exists: {test_doctor['email']}")
            print(f"🔑 Login with: Email: {test_doctor['email']}, Password: {test_doctor['password']}")
        else:
            # Insert test doctor
            cursor.execute("""
                INSERT INTO workers (
                    full_name, email, phone, service, specialization, 
                    experience, clinic_location, license_number, 
                    status, password, rating
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                test_doctor['full_name'], test_doctor['email'], test_doctor['phone'],
                test_doctor['service'], test_doctor['specialization'], test_doctor['experience'],
                test_doctor['clinic_location'], test_doctor['license_number'], 
                test_doctor['status'], hashed_password.decode('utf-8'), 4.5
            ))
            
            conn.commit()
            print(f"✅ Test doctor created successfully!")
            print(f"📧 Email: {test_doctor['email']}")
            print(f"🔑 Password: {test_doctor['password']}")
            print(f"🏥 Name: {test_doctor['full_name']}")
            print(f"🩺 Specialization: {test_doctor['specialization']}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creating test doctor: {e}")

if __name__ == "__main__":
    create_test_doctor()
