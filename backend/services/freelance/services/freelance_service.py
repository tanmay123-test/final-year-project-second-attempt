from ..models.database import freelance_db
import logging
from email_service import send_email

class FreelanceService:
    # --- Project Management ---
    def create_project(self, client_id, title, description, category, budget_type, budget_amount, deadline, skills, exp_level, milestones=None):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO freelance_projects 
                (client_id, title, description, category, budget_type, budget_amount, deadline, required_skills, experience_level)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (client_id, title, description, category, budget_type, budget_amount, deadline, skills, exp_level))
            project_id = cursor.fetchone()[0]
            
            # Insert initial project milestones if provided
            if milestones and isinstance(milestones, list):
                for m in milestones:
                    cursor.execute("""
                        INSERT INTO freelance_project_milestones (project_id, title, amount)
                        VALUES (%s, %s, %s)
                    """, (project_id, m.get('title'), m.get('amount')))
            
            conn.commit()
            return project_id
        finally:
            cursor.close()
            conn.close()

    def get_projects(self, status='OPEN', category=None):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            query = """
                SELECT p.*, u.name as client_name 
                FROM freelance_projects p
                LEFT JOIN users u ON p.client_id = u.id
                WHERE p.status = %s
            """
            params = [status]
            if category:
                query += " AND p.category = %s"
                params.append(category)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [freelance_db._row_to_dict(row, cursor) for row in rows]
        finally:
            cursor.close()
            conn.close()

    def get_projects_by_client(self, client_id, status=None):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            query = """
                SELECT p.*, 
                       (SELECT COUNT(*) FROM freelance_proposals WHERE project_id = p.id) as proposals_count,
                       c.freelancer_id,
                       w.full_name as freelancer_name
                FROM freelance_projects p 
                LEFT JOIN freelance_contracts c ON p.id = c.project_id
                LEFT JOIN workers w ON c.freelancer_id = w.id
                WHERE p.client_id = %s
            """
            params = [client_id]
            if status:
                query += " AND p.status = %s"
                params.append(status)
            
            query += " ORDER BY p.created_at DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            projects = [freelance_db._row_to_dict(row, cursor) for row in rows]
            
            # Fetch milestones for each project
            for p in projects:
                cursor.execute("SELECT * FROM freelance_project_milestones WHERE project_id = %s", (p['id'],))
                milestone_rows = cursor.fetchall()
                p['milestones'] = [freelance_db._row_to_dict(mr, cursor) for mr in milestone_rows]
                
            return projects
        finally:
            cursor.close()
            conn.close()

    def get_project_by_id(self, project_id):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM freelance_projects WHERE id = %s", (project_id,))
            row = cursor.fetchone()
            return freelance_db._row_to_dict(row, cursor) if row else None
        finally:
            cursor.close()
            conn.close()

    # --- Proposal Management ---
    def submit_proposal(self, project_id, freelancer_id, price, delivery_time, message):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO freelance_proposals (project_id, freelancer_id, proposed_price, delivery_time, cover_message)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (project_id, freelancer_id, price, delivery_time, message))
            proposal_id = cursor.fetchone()[0]
            conn.commit()
            return proposal_id
        finally:
            cursor.close()
            conn.close()

    def get_proposals_by_project(self, project_id):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT p.*, w.full_name as freelancer_name, w.rating as freelancer_rating
                FROM freelance_proposals p
                LEFT JOIN workers w ON p.freelancer_id = w.id
                WHERE p.project_id = %s
            """, (project_id,))
            rows = cursor.fetchall()
            return [freelance_db._row_to_dict(row, cursor) for row in rows]
        finally:
            cursor.close()
            conn.close()

    def get_proposals_by_freelancer(self, freelancer_id):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT p.*, pr.title as project_title, pr.budget_amount as project_budget
                FROM freelance_proposals p
                JOIN freelance_projects pr ON p.project_id = pr.id
                WHERE p.freelancer_id = %s
                ORDER BY p.created_at DESC
            """, (freelancer_id,))
            rows = cursor.fetchall()
            return [freelance_db._row_to_dict(row, cursor) for row in rows]
        finally:
            cursor.close()
            conn.close()

    def get_contracts_by_freelancer(self, freelancer_id, status='ACTIVE'):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT c.*, p.title as project_title, p.description as project_description, u.name as client_name
                FROM freelance_contracts c
                JOIN freelance_projects p ON c.project_id = p.id
                LEFT JOIN users u ON c.client_id = u.id
                WHERE c.freelancer_id = %s AND c.status = %s
                ORDER BY c.start_date DESC
            """, (freelancer_id, status))
            rows = cursor.fetchall()
            contracts = [freelance_db._row_to_dict(row, cursor) for row in rows]
            
            # Fetch milestones and messages for each contract
            for c in contracts:
                cursor.execute("SELECT * FROM freelance_milestones WHERE contract_id = %s", (c['id'],))
                m_rows = cursor.fetchall()
                c['milestones'] = [freelance_db._row_to_dict(mr, cursor) for mr in m_rows]
                
                cursor.execute("SELECT * FROM freelance_messages WHERE contract_id = %s ORDER BY created_at ASC", (c['id'],))
                msg_rows = cursor.fetchall()
                c['messages'] = [freelance_db._row_to_dict(mgr, cursor) for mgr in msg_rows]
                
            return contracts
        finally:
            cursor.close()
            conn.close()

    def get_freelancer_stats(self, freelancer_id):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            stats = {}
            # Total Earnings
            cursor.execute("""
                SELECT SUM(amount) FROM freelance_payments p
                JOIN freelance_contracts c ON p.contract_id = c.id
                WHERE c.freelancer_id = %s AND p.escrow_status = 'RELEASED'
            """, (freelancer_id,))
            stats['total_earnings'] = cursor.fetchone()[0] or 0
            
            # Active Projects
            cursor.execute("SELECT COUNT(*) FROM freelance_contracts WHERE freelancer_id = %s AND status = 'ACTIVE'", (freelancer_id,))
            stats['active_projects'] = cursor.fetchone()[0]
            
            # Proposals Sent
            cursor.execute("SELECT COUNT(*) FROM freelance_proposals WHERE freelancer_id = %s", (freelancer_id,))
            stats['proposals_sent'] = cursor.fetchone()[0]
            
            # Average Rating
            cursor.execute("SELECT AVG(rating) FROM freelance_reviews WHERE reviewed_user_id = %s", (freelancer_id,))
            stats['rating'] = round(cursor.fetchone()[0] or 0, 1)
            
            return stats
        finally:
            cursor.close()
            conn.close()

    def get_freelancer_dashboard_data(self, freelancer_id):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            # 1. Basic Info
            cursor.execute("SELECT full_name, specialization, skills, bio, rating, photo_url FROM workers WHERE id = %s", (freelancer_id,))
            worker_row = cursor.fetchone()
            if not worker_row:
                return None
            
            worker = freelance_db._row_to_dict(worker_row, cursor)
            name = worker['full_name']
            role = worker['specialization'] or "Freelancer"
            skills = worker['skills'] or ""
            
            # Avatar initials
            name_parts = name.split()
            initials = "".join([p[0].upper() for p in name_parts[:2]]) if name_parts else "F"
            
            # 2. Stats
            stats = self.get_freelancer_stats(freelancer_id)
            
            # 3. Profile Completion
            completion_score = 0
            if worker['full_name']: completion_score += 20
            if worker['specialization']: completion_score += 20
            if worker['skills']: completion_score += 20
            if worker['bio']: completion_score += 20
            if worker['photo_url']: completion_score += 20
            
            # 4. Active Projects
            cursor.execute("""
                SELECT c.*, p.title as project_title, u.name as client_name, p.deadline
                FROM freelance_contracts c
                JOIN freelance_projects p ON c.project_id = p.id
                LEFT JOIN users u ON c.client_id = u.id
                WHERE c.freelancer_id = %s AND c.status = 'ACTIVE'
                ORDER BY c.start_date DESC
            """, (freelancer_id,))
            active_projects = [freelance_db._row_to_dict(row, cursor) for row in cursor.fetchall()]
            
            # 5. Recent Proposals
            cursor.execute("""
                SELECT p.*, pr.title as project_title, pr.budget_amount as budget, pr.deadline
                FROM freelance_proposals p
                JOIN freelance_projects pr ON p.project_id = pr.id
                WHERE p.freelancer_id = %s
                ORDER BY p.created_at DESC LIMIT 5
            """, (freelancer_id,))
            recent_proposals = [freelance_db._row_to_dict(row, cursor) for row in cursor.fetchall()]
            
            # 5b. Pending Direct Bookings
            cursor.execute("""
                SELECT b.*, u.name as client_name
                FROM freelance_bookings b
                JOIN users u ON b.client_id = u.id
                WHERE b.freelancer_id = %s AND b.status = 'AWAITING'
                ORDER BY b.created_at DESC
            """, (freelancer_id,))
            pending_bookings = [freelance_db._row_to_dict(row, cursor) for row in cursor.fetchall()]
            
            # 6. Recommended Projects (Matching Skills)
            # Simple matching: projects with at least one matching skill
            recommended_projects = []
            if skills:
                skill_list = [s.strip().lower() for s in skills.split(',')]
                # Get all open projects
                all_open_projects = self.get_projects(status='OPEN')
                for p in all_open_projects:
                    proj_skills = (p.get('required_skills') or "").lower()
                    if any(s in proj_skills for s in skill_list):
                        recommended_projects.append(p)
            
            # If no recommendations, just show latest open projects
            if not recommended_projects:
                recommended_projects = self.get_projects(status='OPEN')[:3]
            else:
                recommended_projects = recommended_projects[:3]

            return {
                "name": name,
                "role": role,
                "avatarInitials": initials,
                "stats": stats,
                "profileCompletion": completion_score,
                "activeProjects": active_projects,
                "recentProposals": recent_proposals,
                "pendingBookings": pending_bookings,
                "recommendedProjects": recommended_projects
            }
        finally:
            cursor.close()
            conn.close()

    def get_notifications(self, user_id, limit=5):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT * FROM freelance_notifications 
                WHERE user_id = %s 
                ORDER BY created_at DESC LIMIT %s
            """, (user_id, limit))
            rows = cursor.fetchall()
            return [freelance_db._row_to_dict(row, cursor) for row in rows]
        finally:
            cursor.close()
            conn.close()

    def add_notification(self, user_id, type, message, conn=None):
        if conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO freelance_notifications (user_id, type, message) VALUES (%s, %s, %s)", (user_id, type, message))
            return

        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO freelance_notifications (user_id, type, message) VALUES (%s, %s, %s)", (user_id, type, message))
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def accept_proposal(self, proposal_id):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            # Get proposal details
            cursor.execute("SELECT * FROM freelance_proposals WHERE id = %s", (proposal_id,))
            proposal = cursor.fetchone()
            if not proposal:
                print(f"Error: Proposal {proposal_id} not found")
                return False, "Proposal not found"
            
            proposal_dict = freelance_db._row_to_dict(proposal, cursor)
            project_id = proposal_dict['project_id']
            freelancer_id = proposal_dict['freelancer_id']

            # Check if project exists and get client_id
            cursor.execute("SELECT client_id, status FROM freelance_projects WHERE id = %s", (project_id,))
            project_row = cursor.fetchone()
            if not project_row:
                print(f"Error: Project {project_id} not found")
                return False, "Project not found"
            
            client_id, project_status = project_row
            if project_status != 'OPEN':
                return False, f"Project is already {project_status}"

            # Update proposal status
            cursor.execute("UPDATE freelance_proposals SET status = 'ACCEPTED' WHERE id = %s", (proposal_id,))
            
            # Update other proposals to REJECTED
            cursor.execute("UPDATE freelance_proposals SET status = 'REJECTED' WHERE project_id = %s AND id != %s", (project_id, proposal_id))
            
            # Update project status
            cursor.execute("UPDATE freelance_projects SET status = 'IN_PROGRESS' WHERE id = %s", (project_id,))
            
            # Create contract
            cursor.execute("""
                INSERT INTO freelance_contracts (project_id, client_id, freelancer_id, status)
                VALUES (%s, %s, %s, 'ACTIVE')
                RETURNING id
            """, (project_id, client_id, freelancer_id))
            contract_id = cursor.fetchone()[0]
            
            # Create milestones for the contract (copy from project milestones)
            cursor.execute("SELECT title, amount FROM freelance_project_milestones WHERE project_id = %s", (project_id,))
            project_milestones = cursor.fetchall()
            for m in project_milestones:
                cursor.execute("""
                    INSERT INTO freelance_milestones (contract_id, title, amount, status)
                    VALUES (%s, %s, %s, 'PENDING')
                """, (contract_id, m[0], m[1]))
            
            # Notify freelancer
            self.add_notification(freelancer_id, 'PROPOSAL_ACCEPTED', f"Your proposal for project {project_id} has been accepted!", conn=conn)
            
            conn.commit()
            return True, "Success"
        except Exception as e:
            conn.rollback()
            print(f"Exception in accept_proposal: {str(e)}")
            return False, str(e)
        finally:
            cursor.close()
            conn.close()

    def reject_proposal(self, proposal_id):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE freelance_proposals SET status = 'REJECTED' WHERE id = %s", (proposal_id,))
            conn.commit()
            return True, "Proposal rejected"
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            cursor.close()
            conn.close()

    def get_project_count_by_user(self, user_id):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM freelance_projects WHERE client_id = %s", (user_id,))
            return cursor.fetchone()[0]
        finally:
            cursor.close()
            conn.close()

    def get_proposals_by_freelancer(self, freelancer_id, status=None):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            query = """
                SELECT p.*, pr.title as project_title, pr.budget_amount as budget, pr.deadline
                FROM freelance_proposals p
                JOIN freelance_projects pr ON p.project_id = pr.id
                WHERE p.freelancer_id = %s
            """
            params = [freelancer_id]
            if status and status.lower() != 'all':
                query += " AND p.status = %s"
                params.append(status.upper())
            
            query += " ORDER BY p.created_at DESC"
            cursor.execute(query, tuple(params))
            return [freelance_db._row_to_dict(row, cursor) for row in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()

    def withdraw_proposal(self, proposal_id, freelancer_id):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            # Only allow withdrawing if pending
            cursor.execute("SELECT status FROM freelance_proposals WHERE id = %s AND freelancer_id = %s", (proposal_id, freelancer_id))
            row = cursor.fetchone()
            if not row:
                return False, "Proposal not found"
            if row[0] != 'PENDING':
                return False, "Only pending proposals can be withdrawn"
            
            cursor.execute("DELETE FROM freelance_proposals WHERE id = %s", (proposal_id,))
            conn.commit()
            return True, "Withdrawn"
        finally:
            cursor.close()
            conn.close()

    def get_direct_bookings_by_freelancer(self, freelancer_id):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT b.*, b.amount as budget, u.name as client_name
                FROM freelance_bookings b
                LEFT JOIN users u ON b.client_id = u.id
                WHERE b.freelancer_id = %s
                ORDER BY b.created_at DESC
            """, (freelancer_id,))
            return [freelance_db._row_to_dict(row, cursor) for row in cursor.fetchall()]
        finally:
             cursor.close()
             conn.close()

    def get_freelancer_active_work(self, freelancer_id):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT c.*, p.title, p.description, u.name as client_name
                FROM freelance_contracts c
                JOIN freelance_projects p ON c.project_id = p.id
                LEFT JOIN users u ON c.client_id = u.id
                WHERE c.freelancer_id = %s AND c.status = 'ACTIVE'
                ORDER BY c.start_date DESC
            """, (freelancer_id,))
            contracts = [freelance_db._row_to_dict(row, cursor) for row in cursor.fetchall()]
            
            for contract in contracts:
                cursor.execute("SELECT * FROM freelance_milestones WHERE contract_id = %s ORDER BY id ASC", (contract['id'],))
                contract['milestones'] = [freelance_db._row_to_dict(row, cursor) for row in cursor.fetchall()]
            
            return contracts
        finally:
            cursor.close()
            conn.close()

    def get_project_messages(self, project_id):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM freelance_messages WHERE project_id = %s ORDER BY created_at ASC", (project_id,))
            return [freelance_db._row_to_dict(row, cursor) for row in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()

    def submit_milestone(self, milestone_id, project_id=None):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE freelance_milestones SET status = 'SUBMITTED' WHERE id = %s", (milestone_id,))
            
            # Notify client
            cursor.execute("""
                SELECT c.client_id, m.title FROM freelance_milestones m
                JOIN freelance_contracts c ON m.contract_id = c.id
                WHERE m.id = %s
            """, (milestone_id,))
            row = cursor.fetchone()
            if row:
                self.add_notification(row[0], 'MILESTONE_SUBMITTED', f"Milestone '{row[1]}' has been submitted for review.", conn=conn)
                
            conn.commit()
            return True, "Milestone submitted"
        finally:
            cursor.close()
            conn.close()

    def send_message(self, project_id=None, contract_id=None, sender_id=None, message=None, file_attachment=None):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            if project_id and not contract_id:
                cursor.execute("SELECT id FROM freelance_contracts WHERE project_id = %s", (project_id,))
                row = cursor.fetchone()
                contract_id = row[0] if row else None
            
            if not project_id and contract_id:
                cursor.execute("SELECT project_id FROM freelance_contracts WHERE id = %s", (contract_id,))
                row = cursor.fetchone()
                project_id = row[0] if row else None

            cursor.execute("""
                INSERT INTO freelance_messages (project_id, contract_id, sender_id, message, file_attachment) 
                VALUES (%s, %s, %s, %s, %s)
            """, (project_id, contract_id, sender_id, message, file_attachment))
            
            # Notify recipient
            cursor.execute("SELECT client_id, freelancer_id FROM freelance_contracts WHERE project_id = %s", (project_id,))
            row = cursor.fetchone()
            if row:
                recipient_id = row[1] if sender_id == row[0] else row[0]
                self.add_notification(recipient_id, 'NEW_MESSAGE', f"New message in project chat.", conn=conn)
                
            conn.commit()
            return True, "Message sent"
        finally:
            cursor.close()
            conn.close()

    # --- Wallet & Payment Logic ---
    # This will be integrated with existing wallet system later
    def release_milestone(self, milestone_id):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE freelance_milestones SET status = 'PAID', approved_at = CURRENT_TIMESTAMP WHERE id = %s", (milestone_id,))
            cursor.execute("UPDATE freelance_payments SET escrow_status = 'RELEASED', released_at = CURRENT_TIMESTAMP WHERE milestone_id = %s", (milestone_id,))
            conn.commit()
            return True
        finally:
            cursor.close()
            conn.close()

    # --- Direct Booking Management ---
    def create_booking_request(self, client_id, freelancer_id, title, description, amount, deadline=None):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO freelance_bookings (client_id, freelancer_id, project_title, project_description, amount, deadline)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (client_id, freelancer_id, title, description, amount, deadline))
            booking_id = cursor.fetchone()[0]
            
            # Notify freelancer via in-app notification
            self.add_notification(freelancer_id, 'NEW_BOOKING_REQUEST', f"New direct booking request: {title}", conn=conn)
            
            # Notify freelancer via email
            try:
                cursor.execute("SELECT full_name, email FROM workers WHERE id = %s", (freelancer_id,))
                worker = cursor.fetchone()
                cursor.execute("SELECT name FROM users WHERE id = %s", (client_id,))
                client = cursor.fetchone()
                
                if worker and client:
                    worker_name, worker_email = worker
                    client_name = client[0]
                    
                    subject = f"Action Required: New Direct Booking Request - {title}"
                    body = f"""
Hello {worker_name},

You have received a new direct booking request on ExpertEase! A client is interested in working with you specifically.

PROJECT DETAILS
---------------
Title: {title}
Client: {client_name}
Budget: ₹{amount}
Deadline: {deadline or 'Flexible'}

DESCRIPTION
-----------
{description}

NEXT STEPS
----------
1. Log in to your ExpertEase Freelancer Dashboard.
2. Review the request in the 'New Booking Requests' section.
3. Choose to 'Accept' or 'Decline' the request.

Prompt responses help you maintain a high rating and build trust with clients.

Best regards,
The ExpertEase Team
                    """
                    send_email(worker_email, subject, body)
            except Exception as e:
                logging.error(f"Failed to send booking email: {e}")

            conn.commit()
            return booking_id
        finally:
            cursor.close()
            conn.close()

    def get_booking_requests_by_freelancer(self, freelancer_id, status='AWAITING'):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT b.*, u.name as client_name 
                FROM freelance_bookings b
                JOIN users u ON b.client_id = u.id
                WHERE b.freelancer_id = %s AND b.status = %s
                ORDER BY b.created_at DESC
            """, (freelancer_id, status))
            rows = cursor.fetchall()
            return [freelance_db._row_to_dict(row, cursor) for row in rows]
        finally:
            cursor.close()
            conn.close()

    def add_audit_log(self, entity_type, entity_id, action, old_val=None, new_val=None, user_id=None, conn=None):
        should_close = False
        if not conn:
            conn = freelance_db.get_conn()
            should_close = True
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO freelance_audit_logs (entity_type, entity_id, action, old_value, new_value, performed_by)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (entity_type, entity_id, action, str(old_val) if old_val else None, str(new_val) if new_val else None, user_id))
            if should_close:
                conn.commit()
        finally:
            if should_close:
                cursor.close()
                conn.close()

    def update_booking_status(self, booking_id, status, performer_id=None):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            # Get current status for audit
            cursor.execute("SELECT status, client_id, freelancer_id, project_title, amount, deadline FROM freelance_bookings WHERE id = %s", (booking_id,))
            booking = cursor.fetchone()
            if not booking:
                return False
            old_status, client_id, freelancer_id, title, amount, deadline = booking

            # Update status
            cursor.execute("UPDATE freelance_bookings SET status = %s WHERE id = %s", (status, booking_id))
            
            # Audit log
            self.add_audit_log('BOOKING', booking_id, 'STATUS_CHANGE', old_status, status, performer_id, conn=conn)

            # Email notification to client
            try:
                cursor.execute("SELECT name, email FROM users WHERE id = %s", (client_id,))
                client = cursor.fetchone()
                cursor.execute("SELECT full_name, email FROM workers WHERE id = %s", (freelancer_id,))
                worker = cursor.fetchone()
                
                if client and worker:
                    client_name, client_email = client
                    worker_name, worker_email = worker[0], worker[1] if len(worker) > 1 else None
                    
                    # 1. Email to Client
                    subject_client = f"Booking Update: {worker_name} has {status.lower()} your request"
                    body_client = f"""
Hello {client_name},

This is an update regarding your direct booking request for '{title}'.

STATUS: {status}
FREELANCER: {worker_name}
BUDGET: ₹{amount}

{f"EXCITING NEWS! {worker_name} has ACCEPTED your request. You can now manage this project in your 'My Projects' tab." if status == 'ACCEPTED' else f"Unfortunately, {worker_name} has DECLINED this request. You can browse other talented freelancers to find the perfect match for your project."}

Thank you for using ExpertEase.

Best regards,
The ExpertEase Team
                    """
                    send_email(client_email, subject_client, body_client)

                    # 2. Confirmation Email to Freelancer
                    if worker_email:
                        subject_worker = f"Confirmation: You {status.lower()} the booking request for {title}"
                        body_worker = f"""
Hello {worker_name},

This email confirms that you have {status.lower()} the direct booking request from {client_name}.

PROJECT: {title}
BUDGET: ₹{amount}

{f"You can now find this project in your 'My Work' dashboard. Good luck!" if status == 'ACCEPTED' else "The client has been notified of your decision. Your availability status remains unchanged."}

Best regards,
The ExpertEase Team
                        """
                        send_email(worker_email, subject_worker, body_worker)
            except Exception as e:
                logging.error(f"Failed to send booking update email: {e}")

            if status == 'ACCEPTED':
                # Create project for tracking
                cursor.execute("""
                    INSERT INTO freelance_projects 
                    (client_id, title, description, category, budget_type, budget_amount, deadline, status)
                    VALUES (%s, %s, %s, 'General', 'FIXED', %s, %s, 'IN_PROGRESS')
                    RETURNING id
                """, (client_id, title, "Direct booking project", amount, deadline))
                project_id = cursor.fetchone()[0]
                
                # Create contract
                cursor.execute("""
                    INSERT INTO freelance_contracts (project_id, client_id, freelancer_id, status)
                    VALUES (%s, %s, %s, 'ACTIVE')
                """, (project_id, client_id, freelancer_id))
                
                # Link project_id back to booking
                cursor.execute("UPDATE freelance_bookings SET project_id = %s WHERE id = %s", (project_id, booking_id))
                
                self.add_notification(client_id, 'BOOKING_ACCEPTED', f"Your booking request '{title}' was accepted!", conn=conn)
            elif status == 'DECLINED':
                self.add_notification(client_id, 'BOOKING_DECLINED', f"Your booking request '{title}' was declined.", conn=conn)
            
            conn.commit()
            return True
        finally:
            cursor.close()
            conn.close()

    def save_deliverable(self, project_id, freelancer_id, file_path, filename):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            # Get contract_id if it exists
            cursor.execute("SELECT id, client_id FROM freelance_contracts WHERE project_id = %s", (project_id,))
            contract = cursor.fetchone()
            contract_id = contract[0] if contract else None
            
            cursor.execute("""
                INSERT INTO freelance_deliverables (project_id, contract_id, freelancer_id, file_path, filename)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (project_id, contract_id, freelancer_id, file_path, filename))
            deliverable_id = cursor.fetchone()[0]
            
            # Notify client
            if contract:
                client_id = contract[1]
                self.add_notification(client_id, 'NEW_DELIVERABLE', f"A new deliverable has been uploaded for your project.", conn=conn)
                
            conn.commit()
            return deliverable_id
        finally:
            cursor.close()
            conn.close()

    def get_project_deliverables(self, project_id):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM freelance_deliverables WHERE project_id = %s ORDER BY created_at DESC", (project_id,))
            return [freelance_db._row_to_dict(row, cursor) for row in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()

    def complete_project(self, project_id, performer_id=None):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            # Get project and contract details
            cursor.execute("SELECT client_id, title FROM freelance_projects WHERE id = %s", (project_id,))
            project = cursor.fetchone()
            if not project:
                return False, "Project not found"
            client_id, title = project

            # Update project status
            cursor.execute("UPDATE freelance_projects SET status = 'COMPLETED' WHERE id = %s", (project_id,))
            
            # Update contract status
            cursor.execute("UPDATE freelance_contracts SET status = 'COMPLETED', end_date = CURRENT_TIMESTAMP WHERE project_id = %s", (project_id,))
            
            # Audit log
            self.add_audit_log('PROJECT', project_id, 'STATUS_CHANGE', 'IN_PROGRESS', 'COMPLETED', performer_id, conn=conn)
            
            # Notify client
            self.add_notification(client_id, 'PROJECT_COMPLETED', f"Project '{title}' has been marked as completed.", conn=conn)
            
            conn.commit()
            return True, "Project marked as completed"
        finally:
            cursor.close()
            conn.close()

    def get_featured_freelancers(self, limit=3):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            # Fetch workers with 'freelance' in their services
            # Assuming 'service' column contains comma-separated values like 'healthcare,freelance'
            cursor.execute("""
                SELECT id, full_name, specialization, rating, hourly_rate, skills, status, created_at
                FROM workers
                WHERE (',' || service || ',') LIKE '%%,freelance,%%'
                AND status = 'approved'
                ORDER BY rating DESC, created_at DESC
                LIMIT %s
            """, (limit,))
            rows = cursor.fetchall()
            return [freelance_db._row_to_dict(row, cursor) for row in rows]
        finally:
            cursor.close()
            conn.close()

    def get_all_skills(self):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM freelance_skills ORDER BY category, name")
            rows = cursor.fetchall()
            return [freelance_db._row_to_dict(row, cursor) for row in rows]
        finally:
            cursor.close()
            conn.close()

    def update_provider_skills(self, provider_id, skill_ids):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            # Clear existing skills
            cursor.execute("DELETE FROM freelance_provider_skills WHERE provider_id = %s", (provider_id,))
            
            # Insert new skills
            if skill_ids:
                skill_data = [(provider_id, sid) for sid in skill_ids]
                import psycopg2.extras
                psycopg2.extras.execute_batch(cursor, "INSERT INTO freelance_provider_skills (provider_id, skill_id) VALUES (%s, %s)", skill_data)
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error updating provider skills: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def get_provider_skills(self, provider_id):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT s.* FROM freelance_skills s
                JOIN freelance_provider_skills ps ON s.id = ps.skill_id
                WHERE ps.provider_id = %s
            """, (provider_id,))
            rows = cursor.fetchall()
            return [freelance_db._row_to_dict(row, cursor) for row in rows]
        finally:
            cursor.close()
            conn.close()

    def get_workers_by_skills(self, skill_ids=None):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            if skill_ids:
                # Get workers matching all specified skills
                placeholders = ','.join(['%s'] * len(skill_ids))
                cursor.execute(f"""
                    SELECT w.* FROM workers w
                    WHERE w.id IN (
                        SELECT provider_id FROM freelance_provider_skills
                        WHERE skill_id IN ({placeholders})
                        GROUP BY provider_id
                        HAVING COUNT(DISTINCT skill_id) = %s
                    )
                """, skill_ids + [len(skill_ids)])
            else:
                cursor.execute("SELECT * FROM workers WHERE status = 'approved'")
            
            rows = cursor.fetchall()
            workers = [freelance_db._row_to_dict(row, cursor) for row in rows]
            
            # Attach skills to each worker
            for w in workers:
                cursor.execute("""
                    SELECT s.name FROM freelance_skills s
                    JOIN freelance_provider_skills ps ON s.id = ps.skill_id
                    WHERE ps.provider_id = %s
                """, (w['id'],))
                w['skills_list'] = [row[0] for row in cursor.fetchall()]
                
            return workers
        finally:
            cursor.close()
            conn.close()

    def get_bookings_by_client(self, client_id):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT b.*, w.full_name as freelancer_name
                FROM freelance_bookings b
                JOIN workers w ON b.freelancer_id = w.id
                WHERE b.client_id = %s
                ORDER BY b.created_at DESC
            """, (client_id,))
            rows = cursor.fetchall()
            return [freelance_db._row_to_dict(row, cursor) for row in rows]
        finally:
            cursor.close()
            conn.close()

    def get_booking_by_id(self, booking_id):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM freelance_bookings WHERE id = %s", (booking_id,))
            row = cursor.fetchone()
            return freelance_db._row_to_dict(row, cursor) if row else None
        finally:
            cursor.close()
            conn.close()

freelance_service = FreelanceService()
