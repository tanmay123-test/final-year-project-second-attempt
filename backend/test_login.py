import psycopg2
import bcrypt
from dotenv import load_dotenv

load_dotenv()

# Test database connection and check users
try:
    DATABASE_URL = "postgresql://postgres.hfilbrunntrfpvxrbazy:Tan12may34567890@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"
    
    print("🔍 Testing login system...")
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    
    # Check all users in database
    cursor.execute("SELECT username, email, is_verified FROM users WHERE username IS NOT NULL")
    users = cursor.fetchall()
    
    print(f"📊 Found {len(users)} users in database:")
    for user in users:
        username, email, is_verified = user
        print(f"  • Username: {username}, Email: {email}, Verified: {is_verified}")
    
    if not users:
        print("❌ No users found! You need to create a user first.")
        print("\n📝 Creating a test user...")
        
        # Create a test user
        test_username = "testuser"
        test_email = "test@example.com"
        test_password = "password123"
        
        # Hash the password
        hashed_password = bcrypt.hashpw(test_password.encode(), bcrypt.gensalt())
        
        cursor.execute("""
            INSERT INTO users (username, email, password, is_verified, name)
            VALUES (%s, %s, %s, %s, %s)
        """, (test_username, test_email, hashed_password, 1, "Test User"))
        
        conn.commit()
        print(f"✅ Created test user:")
        print(f"  Username: {test_username}")
        print(f"  Password: {test_password}")
        print(f"  Email: {test_email}")
        
        # Test login verification
        cursor.execute("SELECT password, is_verified FROM users WHERE username = %s", (test_username,))
        result = cursor.fetchone()
        
        if result:
            stored_password, is_verified = result
            if isinstance(stored_password, memoryview):
                stored_password = stored_password.tobytes()
            
            if bcrypt.checkpw(test_password.encode(), stored_password):
                print("✅ Password verification test PASSED")
            else:
                print("❌ Password verification test FAILED")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
