import sqlite3

conn = sqlite3.connect('car_service.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print('📊 ALL TABLES IN DATABASE:')
for i, table in enumerate(tables, 1):
    print(f'{i:2d}. 📋 {table[0]}')

# Check for mechanics specifically
print('\n🔍 SEARCHING FOR MECHANICS:')
mechanic_found = False
for table in tables:
    table_name = table[0].lower()
    if 'mechanic' in table_name:
        cursor.execute(f'SELECT COUNT(*) FROM {table[0]}')
        count = cursor.fetchone()[0]
        print(f'✅ {table[0]}: {count} records')
        if count > 0:
            cursor.execute(f'SELECT * FROM {table[0]} LIMIT 3')
            rows = cursor.fetchall()
            for row in rows:
                print(f'   📄 {row}')
        mechanic_found = True

if not mechanic_found:
    print('❌ No mechanic tables found')
    print('💡 Mechanics might be in: mechanics, workers, or car_mechanics tables')

conn.close()
