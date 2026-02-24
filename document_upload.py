"""
Document upload system for healthcare worker verification
"""
import os
import uuid
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import sqlite3
from datetime import datetime
from config import UPLOAD_DIR, HEALTHCARE_UPLOAD_DIR

# Ensure upload directories exist
os.makedirs(HEALTHCARE_UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(HEALTHCARE_UPLOAD_DIR, "pending"), exist_ok=True)
os.makedirs(os.path.join(HEALTHCARE_UPLOAD_DIR, "approved"), exist_ok=True)

# Required documents for healthcare workers
REQUIRED_DOCUMENTS = {
    "aadhar_card": "Aadhar Card",
    "live_selfie": "Live Selfie", 
    "medical_certificate": "Medical Certificate",
    "doctor_license": "Doctor License",
    "clinic_registration": "Clinic Registration Certificate"
}

ALLOWED_EXTENSIONS = {
    'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'
}

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_document_db():
    """Create document tracking database"""
    conn = sqlite3.connect('data/documents.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS worker_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            worker_id INTEGER NOT NULL,
            document_type TEXT NOT NULL,
            filename TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size INTEGER,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending',
            admin_notes TEXT,
            FOREIGN KEY (worker_id) REFERENCES workers (id)
        )
    """)
    
    conn.commit()
    conn.close()

def upload_document(worker_id, document_type, file):
    """Upload a document for a worker"""
    
    if document_type not in REQUIRED_DOCUMENTS:
        return {"success": False, "error": "Invalid document type"}
    
    if file and allowed_file(file.filename):
        # Generate unique filename
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{worker_id}_{document_type}_{uuid.uuid4().hex[:8]}.{file_ext}"
        
        # Create worker directory
        worker_dir = os.path.join(HEALTHCARE_UPLOAD_DIR, "pending", f"worker_{worker_id}")
        os.makedirs(worker_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(worker_dir, unique_filename)
        file.save(file_path)
        
        # Save to database
        conn = sqlite3.connect('data/documents.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO worker_documents 
            (worker_id, document_type, filename, original_filename, file_path, file_size)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            worker_id,
            document_type,
            unique_filename,
            file.filename,
            file_path,
            len(file.read()) if hasattr(file, 'read') else os.path.getsize(file_path)
        ))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "document_id": cursor.lastrowid,
            "filename": unique_filename,
            "document_type": document_type
        }
    
    return {"success": False, "error": "Invalid file or file type not allowed"}

def get_worker_documents(worker_id):
    """Get all documents for a worker"""
    conn = sqlite3.connect('data/documents.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, document_type, filename, original_filename, 
               upload_time, status, admin_notes
        FROM worker_documents 
        WHERE worker_id = ?
        ORDER BY upload_time DESC
    """, (worker_id,))
    
    documents = []
    for row in cursor.fetchall():
        documents.append({
            "id": row[0],
            "document_type": row[1],
            "filename": row[2],
            "original_filename": row[3],
            "upload_time": row[4],
            "status": row[5],
            "admin_notes": row[6],
            "display_name": REQUIRED_DOCUMENTS.get(row[1], row[1])
        })
    
    conn.close()
    return documents

def check_documents_complete(worker_id):
    """Check if all required documents are uploaded"""
    documents = get_worker_documents(worker_id)
    uploaded_types = {doc['document_type'] for doc in documents}
    required_types = set(REQUIRED_DOCUMENTS.keys())
    
    return {
        "complete": required_types.issubset(uploaded_types),
        "missing": list(required_types - uploaded_types),
        "uploaded": list(uploaded_types)
    }

def get_pending_documents_for_admin():
    """Get all pending documents for admin review"""
    conn = sqlite3.connect('data/documents.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT wd.*, w.full_name, w.email, w.specialization
        FROM worker_documents wd
        JOIN workers w ON wd.worker_id = w.id
        WHERE wd.status = 'pending'
        ORDER BY wd.upload_time DESC
    """)
    
    documents = []
    for row in cursor.fetchall():
        documents.append({
            "id": row[0],
            "worker_id": row[1],
            "document_type": row[2],
            "filename": row[3],
            "original_filename": row[4],
            "file_path": row[5],
            "file_size": row[6],
            "upload_time": row[7],
            "status": row[8],
            "admin_notes": row[9],
            "worker_name": row[10],
            "worker_email": row[11],
            "worker_specialization": row[12],
            "display_name": REQUIRED_DOCUMENTS.get(row[2], row[2])
        })
    
    conn.close()
    return documents

# Initialize database on import
create_document_db()
