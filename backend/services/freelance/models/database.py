import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class FreelanceDatabase:
    def __init__(self):
        self._create_tables()

    def get_conn(self):
        load_dotenv()
        return psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')

    def _create_tables(self):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            # Projects Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS freelance_projects (
                id SERIAL PRIMARY KEY,
                client_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                budget_type TEXT NOT NULL, -- 'FIXED' or 'HOURLY'
                budget_amount FLOAT NOT NULL,
                deadline TEXT,
                required_skills TEXT,
                experience_level TEXT,
                status TEXT DEFAULT 'OPEN', -- 'OPEN', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Project Milestones Table (Proposed by client)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS freelance_project_milestones (
                id SERIAL PRIMARY KEY,
                project_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                amount FLOAT NOT NULL,
                status TEXT DEFAULT 'PENDING',
                FOREIGN KEY (project_id) REFERENCES freelance_projects (id)
            )
            """)

            # Proposals Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS freelance_proposals (
                id SERIAL PRIMARY KEY,
                project_id INTEGER NOT NULL,
                freelancer_id INTEGER NOT NULL,
                proposed_price FLOAT NOT NULL,
                delivery_time TEXT,
                cover_message TEXT,
                status TEXT DEFAULT 'PENDING', -- 'PENDING', 'ACCEPTED', 'REJECTED'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES freelance_projects (id)
            )
            """)

            # Contracts Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS freelance_contracts (
                id SERIAL PRIMARY KEY,
                project_id INTEGER NOT NULL,
                client_id INTEGER NOT NULL,
                freelancer_id INTEGER NOT NULL,
                status TEXT DEFAULT 'ACTIVE', -- 'ACTIVE', 'COMPLETED', 'TERMINATED', 'DISPUTED'
                start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_date TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES freelance_projects (id)
            )
            """)

            # Milestones Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS freelance_milestones (
                id SERIAL PRIMARY KEY,
                contract_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                amount FLOAT NOT NULL,
                status TEXT DEFAULT 'PENDING', -- 'PENDING', 'SUBMITTED', 'APPROVED', 'PAID'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                approved_at TIMESTAMP,
                FOREIGN KEY (contract_id) REFERENCES freelance_contracts (id)
            )
            """)

            # Payments Table (Escrow)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS freelance_payments (
                id SERIAL PRIMARY KEY,
                contract_id INTEGER NOT NULL,
                milestone_id INTEGER,
                amount FLOAT NOT NULL,
                escrow_status TEXT DEFAULT 'HELD', -- 'HELD', 'RELEASED', 'REFUNDED'
                payment_status TEXT DEFAULT 'PENDING', -- 'PENDING', 'COMPLETED', 'FAILED'
                released_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (contract_id) REFERENCES freelance_contracts (id),
                FOREIGN KEY (milestone_id) REFERENCES freelance_milestones (id)
            )
            """)

            # Reviews Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS freelance_reviews (
                id SERIAL PRIMARY KEY,
                project_id INTEGER NOT NULL,
                reviewer_id INTEGER NOT NULL,
                reviewed_user_id INTEGER NOT NULL,
                rating INTEGER CHECK(rating >= 1 AND rating <= 5),
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES freelance_projects (id)
            )
            """)

            # Portfolios Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS freelance_portfolios (
                id SERIAL PRIMARY KEY,
                freelancer_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                image_url TEXT,
                project_link TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Messages Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS freelance_messages (
                id SERIAL PRIMARY KEY,
                project_id INTEGER NOT NULL,
                contract_id INTEGER,
                sender_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                file_attachment TEXT,
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES freelance_projects (id),
                FOREIGN KEY (contract_id) REFERENCES freelance_contracts (id)
            )
            """)

            # Notifications Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS freelance_notifications (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                message TEXT NOT NULL,
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Disputes Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS freelance_disputes (
                id SERIAL PRIMARY KEY,
                contract_id INTEGER NOT NULL,
                raised_by_id INTEGER NOT NULL,
                reason TEXT NOT NULL,
                status TEXT DEFAULT 'OPEN', -- 'OPEN', 'RESOLVED', 'CLOSED'
                resolution TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (contract_id) REFERENCES freelance_contracts (id)
            )
            """)

            # Audit Log Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS freelance_audit_logs (
                id SERIAL PRIMARY KEY,
                entity_type TEXT NOT NULL, -- 'BOOKING', 'PROJECT', 'CONTRACT'
                entity_id INTEGER NOT NULL,
                action TEXT NOT NULL, -- 'CREATED', 'UPDATED', 'DELETED', 'STATUS_CHANGE'
                old_value TEXT,
                new_value TEXT,
                performed_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Skills Master Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS freelance_skills (
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                category TEXT
            )
            """)

            # Provider Skills Junction Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS freelance_provider_skills (
                provider_id INTEGER NOT NULL,
                skill_id INTEGER NOT NULL,
                PRIMARY KEY (provider_id, skill_id),
                FOREIGN KEY (skill_id) REFERENCES freelance_skills (id)
            )
            """)

            # Deliverables Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS freelance_deliverables (
                id SERIAL PRIMARY KEY,
                project_id INTEGER NOT NULL,
                contract_id INTEGER,
                freelancer_id INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                filename TEXT NOT NULL,
                status TEXT DEFAULT 'SUBMITTED', -- 'SUBMITTED', 'APPROVED', 'REJECTED'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES freelance_projects (id),
                FOREIGN KEY (contract_id) REFERENCES freelance_contracts (id)
            )
            """)

            # Direct Bookings Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS freelance_bookings (
                id SERIAL PRIMARY KEY,
                client_id INTEGER NOT NULL,
                freelancer_id INTEGER NOT NULL,
                project_title TEXT NOT NULL,
                project_description TEXT,
                amount FLOAT NOT NULL,
                deadline TEXT,
                status TEXT DEFAULT 'AWAITING', -- 'AWAITING', 'ACCEPTED', 'DECLINED', 'CANCELLED'
                project_id INTEGER, -- Link to freelance_projects once accepted
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Seed initial skills if table is empty
            cursor.execute("SELECT COUNT(*) FROM freelance_skills")
            if cursor.fetchone()[0] == 0:
                initial_skills = [
                    ('React', 'Web Development'), ('Node.js', 'Web Development'), 
                    ('Python', 'Backend'), ('Django', 'Backend'),
                    ('Flutter', 'Mobile'), ('React Native', 'Mobile'),
                    ('UI Design', 'Design'), ('UX Design', 'Design'),
                    ('SEO', 'Marketing'), ('Content Writing', 'Writing'),
                    ('Graphic Design', 'Design'), ('Data Science', 'Data'),
                    ('Cybersecurity', 'IT'), ('Cloud Computing', 'IT')
                ]
                psycopg2.extras.execute_batch(cursor, "INSERT INTO freelance_skills (name, category) VALUES (%s, %s)", initial_skills)

            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def _row_to_dict(self, row, cursor):
        return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

freelance_db = FreelanceDatabase()
