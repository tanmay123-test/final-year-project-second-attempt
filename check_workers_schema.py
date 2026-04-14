import os
import psycopg2
from dotenv import load_dotenv

# Try to load .env from backend directory
load_dotenv(os.path.join('backend', '.env'))

def check_schema():
    try:
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            print("Error: DATABASE_URL not found in environment")
            return
            
        conn = psycopg2.connect(db_url, sslmode='prefer')
        cur = conn.cursor()
        
        # Get column info
        cur.execute("SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'workers'")
        print("Columns:")
        for row in cur.fetchall():
            print(f"  {row[0]} ({row[1]}, Nullable: {row[2]})")
            
        # Get all indexes including their expressions
        cur.execute("""
            SELECT
                t.relname as table_name,
                i.relname as index_name,
                a.attname as column_name,
                ix.indisunique as is_unique
            FROM
                pg_class t,
                pg_class i,
                pg_index ix,
                pg_attribute a
            WHERE
                t.oid = ix.indrelid
                AND i.oid = ix.indexrelid
                AND a.attrelid = t.oid
                AND a.attnum = ANY(ix.indkey)
                AND t.relkind = 'r'
                AND t.relname = 'workers'
            ORDER BY
                t.relname,
                i.relname;
        """)
        print("\nIndexes and Unique Constraints:")
        for row in cur.fetchall():
            print(f"  Table: {row[0]}, Index: {row[1]}, Column: {row[2]}, Unique: {row[3]}")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_schema()
