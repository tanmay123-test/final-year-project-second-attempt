import psycopg2
import psycopg2.extras
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

class UserDB:
    def __init__(self):
        # Initial table creation
        self.create_table()

    def get_conn(self):
        db_url = os.environ.get('DATABASE_URL', '')
        return psycopg2.connect(db_url, sslmode='require')

    def create_table(self):
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT,
                username TEXT UNIQUE,
                email TEXT UNIQUE,
                password BYTEA,
                is_verified INTEGER DEFAULT 0
            )
            """)
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def user_exists(self, username, email):
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id FROM users WHERE username=%s OR email=%s",
                (username, email)
            )
            result = cursor.fetchone() is not None
            return result
        except Exception as e:
            print(f"DB Error: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def create_user(self, name, username, password, email):
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            cursor.execute("""
            INSERT INTO users (name, username, email, password)
            VALUES (%s, %s, %s, %s) RETURNING id
            """, (name, username, email, hashed))
            new_id = cursor.fetchone()[0]
            conn.commit()
            return new_id
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def mark_verified(self, email):
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE users SET is_verified=1 WHERE email=%s",
                (email,)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def verify_user(self, username, password):
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT password, is_verified FROM users WHERE username=%s", (username,))
            row = cursor.fetchone()
            if not row:
                return False, "User not found"
            
            hashed_pw, is_verified = row
            
            # Handle different password formats
            try:
                if isinstance(hashed_pw, memoryview):
                    hashed_pw = hashed_pw.tobytes()
                elif isinstance(hashed_pw, str):
                    hashed_pw = hashed_pw.encode('utf-8')
                
                # Try bcrypt verification
                if bcrypt.checkpw(password.encode('utf-8'), hashed_pw):
                    if not is_verified:
                        return False, "Email not verified"
                    return True, "Login successful"
                else:
                    return False, "Invalid password"
            except Exception as bcrypt_error:
                print(f"Bcrypt error: {bcrypt_error}")
                # Fallback for old password formats - try simple string comparison for testing
                if isinstance(hashed_pw, bytes):
                    try:
                        decoded_pw = hashed_pw.decode('utf-8')
                        if decoded_pw == password:
                            if not is_verified:
                                return False, "Email not verified"
                            return True, "Login successful"
                    except:
                        pass
                return False, "Invalid password"

        except Exception as e:
            print(f"DB Error: {e}")
            return False, str(e)
        finally:
            cursor.close()
            conn.close()

    def get_user_by_email(self, email):
        conn = self.get_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT id, email, is_verified FROM users WHERE email=%s", (email,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            print(f"DB Error: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def get_user_count(self):
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM users")
            return cursor.fetchone()[0]
        except Exception as e:
            print(f"DB Error: {e}")
            return 0
        finally:
            cursor.close()
            conn.close()

    def get_user_by_username(self, username):
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM users WHERE username=%s", (username,))
            row = cursor.fetchone()
            return row[0] if row else None
        except Exception as e:
            print(f"DB Error: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def get_user_by_id(self, user_id):
        conn = self.get_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT id, name, username, email, is_verified FROM users WHERE id=%s", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            print(f"DB Error: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
