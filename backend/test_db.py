import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Test database connection
try:
    DATABASE_URL = "postgresql://postgres.hfilbrunntrfpvxrbazy:Tan12may34567890@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"
    
    print("🔍 Testing database connection...")
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    
    # Test query
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"✅ Database connected successfully!")
    print(f"📊 PostgreSQL version: {version[0]}")
    
    # Check if users table exists
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'users'
    """)
    
    if cursor.fetchone():
        print("✅ Users table exists")
        
        # Check users table structure
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        print("📋 Users table columns:")
        for col in columns:
            print(f"  • {col[0]} ({col[1]})")
    else:
        print("❌ Users table not found")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Database connection failed: {e}")
