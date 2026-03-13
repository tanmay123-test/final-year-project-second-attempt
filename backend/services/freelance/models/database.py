import sqlite3
import os
from datetime import datetime
from config import FREELANCE_DB

class FreelanceDatabase:
    def __init__(self, db_path=FREELANCE_DB):
        self.db_path = db_path
        self._create_tables()

    def get_conn(self):
        return sqlite3.connect(self.db_path)

    def _create_tables(self):
        conn = self.get_conn()
        cursor = conn.cursor()

        # Projects Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS freelance_projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            budget_type TEXT NOT NULL, -- 'FIXED' or 'HOURLY'
            budget_amount REAL NOT NULL,
            deadline TEXT,
            required_skills TEXT,
            experience_level TEXT,
            status TEXT DEFAULT 'OPEN', -- 'OPEN', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Project Milestones Table (Proposed by client)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS freelance_project_milestones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            status TEXT DEFAULT 'PENDING',
            FOREIGN KEY (project_id) REFERENCES freelance_projects (id)
        )
        """)

        # Proposals Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS freelance_proposals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            freelancer_id INTEGER NOT NULL,
            proposed_price REAL NOT NULL,
            delivery_time TEXT,
            cover_message TEXT,
            status TEXT DEFAULT 'PENDING', -- 'PENDING', 'ACCEPTED', 'REJECTED'
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES freelance_projects (id)
        )
        """)

        # Contracts Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS freelance_contracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            client_id INTEGER NOT NULL,
            freelancer_id INTEGER NOT NULL,
            status TEXT DEFAULT 'ACTIVE', -- 'ACTIVE', 'COMPLETED', 'TERMINATED', 'DISPUTED'
            start_date TEXT DEFAULT CURRENT_TIMESTAMP,
            end_date TEXT,
            FOREIGN KEY (project_id) REFERENCES freelance_projects (id)
        )
        """)

        # Milestones Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS freelance_milestones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            status TEXT DEFAULT 'PENDING', -- 'PENDING', 'SUBMITTED', 'APPROVED', 'PAID'
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            approved_at TEXT,
            FOREIGN KEY (contract_id) REFERENCES freelance_contracts (id)
        )
        """)

        # Payments Table (Escrow)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS freelance_payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_id INTEGER NOT NULL,
            milestone_id INTEGER,
            amount REAL NOT NULL,
            escrow_status TEXT DEFAULT 'HELD', -- 'HELD', 'RELEASED', 'REFUNDED'
            payment_status TEXT DEFAULT 'PENDING', -- 'PENDING', 'COMPLETED', 'FAILED'
            released_at TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contract_id) REFERENCES freelance_contracts (id),
            FOREIGN KEY (milestone_id) REFERENCES freelance_milestones (id)
        )
        """)

        # Reviews Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS freelance_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            reviewer_id INTEGER NOT NULL,
            reviewed_user_id INTEGER NOT NULL,
            rating INTEGER CHECK(rating >= 1 AND rating <= 5),
            comment TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES freelance_projects (id)
        )
        """)

        # Portfolios Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS freelance_portfolios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            freelancer_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            image_url TEXT,
            project_link TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Messages Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS freelance_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_id INTEGER NOT NULL,
            sender_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            file_attachment TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contract_id) REFERENCES freelance_contracts (id)
        )
        """)

        # Notifications Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS freelance_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            message TEXT NOT NULL,
            is_read INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Disputes Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS freelance_disputes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_id INTEGER NOT NULL,
            raised_by_id INTEGER NOT NULL,
            reason TEXT NOT NULL,
            status TEXT DEFAULT 'OPEN', -- 'OPEN', 'RESOLVED', 'CLOSED'
            resolution TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contract_id) REFERENCES freelance_contracts (id)
        )
        """)

        # Direct Bookings Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS freelance_bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            freelancer_id INTEGER NOT NULL,
            project_title TEXT NOT NULL,
            project_description TEXT,
            amount REAL NOT NULL,
            status TEXT DEFAULT 'PENDING', -- 'PENDING', 'ACCEPTED', 'DECLINED', 'CANCELLED'
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        conn.close()

    def _row_to_dict(self, row, cursor):
        return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

freelance_db = FreelanceDatabase()
