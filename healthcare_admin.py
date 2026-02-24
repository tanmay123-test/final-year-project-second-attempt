"""
Healthcare Admin Module - Complete Document Management System
"""
import os
import sqlite3
from flask import Blueprint, request, jsonify, send_file
from document_upload import get_pending_documents_for_admin, get_worker_documents, check_documents_complete
from worker_db import WorkerDB
from email_service import send_email
from datetime import datetime

healthcare_admin_bp = Blueprint("healthcare_admin", __name__)
worker_db = WorkerDB()

# Document approval statuses
DOCUMENT_STATUSES = ['pending', 'approved', 'rejected', 'needs_revision']

def create_admin_db():
    """Create admin tracking database"""
    conn = sqlite3.connect('data/healthcare_admin.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_email TEXT,
            action_type TEXT,
            worker_id INTEGER,
            document_id INTEGER,
            action_details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS worker_approval_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            worker_id INTEGER UNIQUE,
            approval_status TEXT DEFAULT 'pending',
            approved_documents INTEGER DEFAULT 0,
            total_required INTEGER DEFAULT 5,
            last_review_date TIMESTAMP,
            reviewer_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def log_admin_action(admin_email, action_type, worker_id, document_id, action_details):
    """Log admin action for audit trail"""
    conn = sqlite3.connect('data/healthcare_admin.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO admin_actions 
        (admin_email, action_type, worker_id, document_id, action_details)
        VALUES (?, ?, ?, ?, ?)
    """, (admin_email, action_type, worker_id, document_id, action_details))
    
    conn.commit()
    conn.close()

def update_worker_approval_status(worker_id, status, reviewer_notes=None):
    """Update worker approval status"""
    conn = sqlite3.connect('data/healthcare_admin.db')
    cursor = conn.cursor()
    
    # Get current document count
    documents = get_worker_documents(worker_id)
    approved_count = len([doc for doc in documents if doc['status'] == 'approved'])
    
    cursor.execute("""
        INSERT OR REPLACE INTO worker_approval_status 
        (worker_id, approval_status, approved_documents, total_required, last_review_date, reviewer_notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (worker_id, status, approved_count, 5, datetime.now(), reviewer_notes))
    
    conn.commit()
    conn.close()
    
    return approved_count

def get_worker_approval_status(worker_id):
    """Get worker approval status"""
    conn = sqlite3.connect('data/healthcare_admin.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT approval_status, approved_documents, total_required, 
               last_review_date, reviewer_notes, created_at
        FROM worker_approval_status 
        WHERE worker_id = ?
    """, (worker_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'approval_status': result[0],
            'approved_documents': result[1],
            'total_required': result[2],
            'last_review_date': result[3],
            'reviewer_notes': result[4],
            'created_at': result[5]
        }
    else:
        return {
            'approval_status': 'pending',
            'approved_documents': 0,
            'total_required': 5,
            'last_review_date': None,
            'reviewer_notes': None,
            'created_at': None
        }

# ================= ADMIN ROUTES =================

@healthcare_admin_bp.route("/admin/healthcare/pending-documents", methods=["GET"])
def get_pending_healthcare_documents():
    """Get all pending healthcare documents with detailed info"""
    try:
        documents = get_pending_documents_for_admin()
        
        # Enhance with approval status
        enhanced_docs = []
        for doc in documents:
            approval_status = get_worker_approval_status(doc['worker_id'])
            doc['approval_status'] = approval_status['approval_status']
            doc['approved_documents'] = approval_status['approved_documents']
            doc['total_required'] = approval_status['total_required']
            enhanced_docs.append(doc)
        
        return jsonify({
            "success": True,
            "documents": enhanced_docs,
            "total": len(enhanced_docs)
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@healthcare_admin_bp.route("/admin/healthcare/worker/<int:worker_id>/documents", methods=["GET"])
def get_worker_documents_admin(worker_id):
    """Get all documents for a specific worker"""
    try:
        documents = get_worker_documents(worker_id)
        approval_status = get_worker_approval_status(worker_id)
        worker_info = worker_db.get_worker_by_id(worker_id)
        
        return jsonify({
            "success": True,
            "worker": worker_info,
            "documents": documents,
            "approval_status": approval_status
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@healthcare_admin_bp.route("/admin/healthcare/document/<int:document_id>/approve", methods=["POST"])
def approve_document(document_id):
    """Approve a specific document"""
    try:
        data = request.json
        admin_email = data.get('admin_email', 'admin@expertease.com')
        notes = data.get('notes', '')
        
        # Update document status in database
        conn = sqlite3.connect('data/documents.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE worker_documents 
            SET status = 'approved', admin_notes = ?
            WHERE id = ?
        """, (notes, document_id))
        
        conn.commit()
        
        # Get worker_id for logging
        cursor.execute("SELECT worker_id FROM worker_documents WHERE id = ?", (document_id,))
        worker_id = cursor.fetchone()[0]
        conn.close()
        
        # Log admin action
        log_admin_action(admin_email, 'approve_document', worker_id, document_id, f"Approved with notes: {notes}")
        
        # Update worker approval status
        approved_count = update_worker_approval_status(worker_id, 'pending', f"Document {document_id} approved")
        
        # Check if all documents are approved
        doc_status = check_documents_complete(worker_id)
        if doc_status['complete']:
            update_worker_approval_status(worker_id, 'approved', 'All documents approved')
            
            # Send approval email
            worker = worker_db.get_worker_by_id(worker_id)
            if worker:
                send_email(
                    to_email=worker['email'],
                    subject="✅ ExpertEase Healthcare - Documents Approved",
                    body=f"""
Dear Dr. {worker['full_name']},

Congratulations! 🎉

All your verification documents have been approved successfully.

📋 Approval Details:
- Worker ID: {worker_id}
- Approved Documents: {approved_count + 1}/5
- Status: APPROVED
- Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

You can now:
✅ Login to your healthcare worker dashboard
✅ Start accepting patient appointments
✅ Set up your consultation schedule
✅ Manage your profile

Login URL: http://localhost:5001/worker/healthcare/login

Welcome to ExpertEase Healthcare! 🏥

Best regards,
ExpertEase Healthcare Team
"""
                )
        
        return jsonify({
            "success": True,
            "message": "Document approved successfully",
            "approved_count": approved_count + 1
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@healthcare_admin_bp.route("/admin/healthcare/document/<int:document_id>/reject", methods=["POST"])
def reject_document(document_id):
    """Reject a specific document"""
    try:
        data = request.json
        admin_email = data.get('admin_email', 'admin@expertease.com')
        reason = data.get('reason', 'Document does not meet requirements')
        notes = data.get('notes', '')
        
        # Update document status in database
        conn = sqlite3.connect('data/documents.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE worker_documents 
            SET status = 'rejected', admin_notes = ?
            WHERE id = ?
        """, (f"Rejected: {reason}. {notes}", document_id))
        
        conn.commit()
        
        # Get worker_id for logging
        cursor.execute("SELECT worker_id, document_type FROM worker_documents WHERE id = ?", (document_id,))
        result = cursor.fetchone()
        worker_id = result[0]
        document_type = result[1]
        conn.close()
        
        # Log admin action
        log_admin_action(admin_email, 'reject_document', worker_id, document_id, f"Rejected: {reason}")
        
        # Update worker approval status
        update_worker_approval_status(worker_id, 'needs_revision', f"Document {document_type} rejected")
        
        # Send rejection email
        worker = worker_db.get_worker_by_id(worker_id)
        if worker:
            send_email(
                to_email=worker['email'],
                subject="❌ ExpertEase Healthcare - Document Review Required",
                body=f"""
Dear Dr. {worker['full_name']},

We have reviewed your submitted documents and found an issue that needs attention.

📋 Review Details:
- Worker ID: {worker_id}
- Document Type: {document_type}
- Status: REQUIRES REVISION
- Reason: {reason}
- Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

📝 Notes: {notes}

🔄 Next Steps:
1. Please review the rejection reason carefully
2. Upload a corrected version of the document
3. Ensure the document meets all requirements
4. Submit for review again

Required Documents:
- Aadhar Card
- Live Selfie
- Medical Certificate
- Doctor License
- Clinic Registration Certificate

Upload Portal: http://localhost:5001/worker/healthcare/documents

If you have questions, please contact our support team.

Best regards,
ExpertEase Healthcare Review Team
"""
                )
        
        return jsonify({
            "success": True,
            "message": "Document rejected successfully",
            "rejection_reason": reason
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@healthcare_admin_bp.route("/admin/healthcare/worker/<int:worker_id>/approve", methods=["POST"])
def approve_worker_all_documents(worker_id):
    """Approve worker and all their documents"""
    try:
        data = request.json
        admin_email = data.get('admin_email', 'admin@expertease.com')
        notes = data.get('notes', 'All documents verified and approved')
        
        # Get all worker documents
        documents = get_worker_documents(worker_id)
        
        # Approve all pending documents
        conn = sqlite3.connect('data/documents.db')
        cursor = conn.cursor()
        
        for doc in documents:
            if doc['status'] == 'pending':
                cursor.execute("""
                    UPDATE worker_documents 
                    SET status = 'approved', admin_notes = ?
                    WHERE id = ?
                """, (notes, doc['id']))
        
        conn.commit()
        conn.close()
        
        # Update worker status in main database
        worker_db.approve_worker(worker_id)
        
        # Update approval status
        update_worker_approval_status(worker_id, 'approved', notes)
        
        # Log admin action
        log_admin_action(admin_email, 'approve_worker', worker_id, None, f"Approved all documents: {notes}")
        
        # Send approval email
        worker = worker_db.get_worker_by_id(worker_id)
        if worker:
            send_email(
                to_email=worker['email'],
                subject="🎉 ExpertEase Healthcare - Account Approved!",
                body=f"""
Dear Dr. {worker['full_name']},

Congratulations! 🎉🎉

Your healthcare worker account has been fully approved and verified!

📋 Approval Details:
- Worker ID: {worker_id}
- Full Name: Dr. {worker['full_name']}
- Specialization: {worker['specialization']}
- Status: APPROVED ✅
- Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

🚀 You Can Now:
✅ Accept patient appointments
✅ Conduct video consultations
✅ Set your consultation fees
✅ Manage your schedule
✅ Access healthcare dashboard

🔗 Quick Links:
- Worker Login: http://localhost:5001/worker/healthcare/login
- Dashboard: http://localhost:5001/worker/healthcare/dashboard
- Profile: http://localhost:5001/worker/healthcare/profile

💡 Getting Started:
1. Login with your email: {worker['email']}
2. Complete your profile setup
3. Set your availability schedule
4. Start accepting patients

Welcome to the ExpertEase Healthcare Network! 🏥

Best regards,
ExpertEase Healthcare Team
"""
            )
        
        return jsonify({
            "success": True,
            "message": "Worker approved successfully",
            "worker_id": worker_id
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@healthcare_admin_bp.route("/admin/healthcare/worker/<int:worker_id>/reject", methods=["POST"])
def reject_worker_application(worker_id):
    """Reject worker application entirely"""
    try:
        data = request.json
        admin_email = data.get('admin_email', 'admin@expertease.com')
        reason = data.get('reason', 'Application does not meet requirements')
        notes = data.get('notes', '')
        
        # Get worker info before rejection
        worker = worker_db.get_worker_by_id(worker_id)
        
        # Update worker status in main database
        worker_db.reject_worker(worker_id)
        
        # Update approval status
        update_worker_approval_status(worker_id, 'rejected', f"Application rejected: {reason}")
        
        # Log admin action
        log_admin_action(admin_email, 'reject_worker', worker_id, None, f"Rejected application: {reason}")
        
        # Send rejection email
        if worker:
            send_email(
                to_email=worker['email'],
                subject="❌ ExpertEase Healthcare - Application Status",
                body=f"""
Dear Dr. {worker['full_name']},

We have carefully reviewed your healthcare worker application.

📋 Review Details:
- Worker ID: {worker_id}
- Application Status: NOT APPROVED
- Reason: {reason}
- Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

📝 Additional Notes: {notes}

❌ Unfortunately, your application does not meet our current requirements.

🔄 Next Steps:
1. Review the rejection reasons carefully
2. Address any issues with your documents
3. Consider reapplying in the future (minimum 30 days)

If you believe this is an error, please contact our support team with your Worker ID: {worker_id}

Thank you for your interest in ExpertEase Healthcare.

Best regards,
ExpertEase Healthcare Review Team
"""
            )
        
        return jsonify({
            "success": True,
            "message": "Worker application rejected",
            "worker_id": worker_id
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@healthcare_admin_bp.route("/admin/healthcare/analytics", methods=["GET"])
def get_admin_analytics():
    """Get admin analytics and statistics"""
    try:
        conn = sqlite3.connect('data/healthcare_admin.db')
        cursor = conn.cursor()
        
        # Get approval statistics
        cursor.execute("""
            SELECT approval_status, COUNT(*) 
            FROM worker_approval_status 
            GROUP BY approval_status
        """)
        approval_stats = dict(cursor.fetchall())
        
        # Get recent actions
        cursor.execute("""
            SELECT action_type, worker_id, action_details, timestamp
            FROM admin_actions 
            ORDER BY timestamp DESC 
            LIMIT 10
        """)
        recent_actions = [
            {
                'action_type': row[0],
                'worker_id': row[1], 
                'action_details': row[2],
                'timestamp': row[3]
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        # Get document statistics
        conn = sqlite3.connect('data/documents.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT status, COUNT(*) 
            FROM worker_documents 
            GROUP BY status
        """)
        document_stats = dict(cursor.fetchall())
        
        conn.close()
        
        return jsonify({
            "success": True,
            "analytics": {
                "approval_statistics": approval_stats,
                "document_statistics": document_stats,
                "recent_actions": recent_actions,
                "total_pending_workers": approval_stats.get('pending', 0),
                "total_approved_workers": approval_stats.get('approved', 0),
                "total_rejected_workers": approval_stats.get('rejected', 0)
            }
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Initialize database on import
create_admin_db()
