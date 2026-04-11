import psycopg2
import bcrypt

# Create test user
conn = psycopg2.connect('postgresql://postgres.hfilbrunntrfpvxrbazy:Tan12may34567890@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres', sslmode='require')
cursor = conn.cursor()

# Hash the password
hashed_password = bcrypt.hashpw('password123'.encode(), bcrypt.gensalt())

# Insert test user
cursor.execute('INSERT INTO users (username, email, password, is_verified, name) VALUES (%s, %s, %s, %s, %s)', 
               ('testuser', 'test@test.com', hashed_password, 1, 'Test User'))

conn.commit()
cursor.close()
conn.close()

print('✅ Created test user:')
print('   Username: testuser')
print('   Password: password123')
print('   Email: test@test.com')
print('   Verified: Yes')
