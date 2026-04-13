import os
import psycopg2

try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='prefer')
    cursor = conn.cursor()
    cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'workers' ORDER BY ordinal_position")
    columns = cursor.fetchall()
    print('Actual workers table columns:')
    for col in columns:
        print(f'  {col[0]}: {col[1]}')
    conn.close()
except Exception as e:
    print(f'Error: {e}')
