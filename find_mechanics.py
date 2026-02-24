import sqlite3

# Connect to database
conn = sqlite3.connect('car_service.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print('📊 ALL TABLES IN DATABASE:')
for i, table in enumerate(tables, 1):
    print(f'{i:2d}. 📋 {table[0]}')

# Search for any table containing 'mechanic' or 'worker'
print('\n🔍 SEARCHING FOR MECHANICS/WORKERS:')
found_tables = []

for table in tables:
    table_name = table[0].lower()
    if 'mechanic' in table_name or 'worker' in table_name:
        found_tables.append(table[0])
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f'✅ {table[0]}: {count} records')
        
        if count > 0:
            # Show sample records
            cursor.execute(f"SELECT * FROM {table[0]} LIMIT 5")
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            print(f'   📊 Columns: {columns}')
            for j, row in enumerate(rows, 1):
                print(f'   {j}. {row}')

if not found_tables:
    print('❌ No mechanic/worker tables found')
    print('💡 Checking for other possible tables...')
    
    # Check for common mechanic table names
    possible_names = ['mechanics', 'workers', 'car_mechanics', 'service_workers', 'users']
    for name in possible_names:
        if name in [t[0] for t in tables]:
            cursor.execute(f"SELECT COUNT(*) FROM {name}")
            count = cursor.fetchone()[0]
            print(f'🔍 {name}: {count} records')
            
            if count > 0:
                cursor.execute(f"SELECT * FROM {name} LIMIT 3")
                rows = cursor.fetchall()
                for row in rows:
                    print(f'   📄 {row}')

# Search specifically for "raju mechanic"
print('\n🔍 SEARCHING FOR "RAJU MECHANIC":')
for table in tables:
    table_name = table[0]
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        for row in rows:
            row_str = str(row).lower()
            if 'raju' in row_str:
                print(f'✅ Found in table {table_name}:')
                print(f'   📊 Columns: {columns}')
                print(f'   📄 Data: {row}')
    except:
        pass

conn.close()

print('\n💡 TO ADD MECHANICS LIKE "RAJU":')
print('   1. Use CLI: User → Worker → Signup')
print('   2. Enter name: "Raju Mechanic"')
print('   3. Select worker type: MECHANIC')
print('   4. Fill in details and submit')
