from ..models.database import freelance_db

class FreelanceService:
    # --- Project Management ---
    def create_project(self, client_id, title, description, category, budget_type, budget_amount, deadline, skills, exp_level, milestones=None):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO freelance_projects 
                (client_id, title, description, category, budget_type, budget_amount, deadline, required_skills, experience_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (client_id, title, description, category, budget_type, budget_amount, deadline, skills, exp_level))
            project_id = cursor.lastrowid
            
            # Insert initial project milestones if provided
            if milestones and isinstance(milestones, list):
                for m in milestones:
                    cursor.execute("""
                        INSERT INTO freelance_project_milestones (project_id, title, amount)
                        VALUES (?, ?, ?)
                    """, (project_id, m.get('title'), m.get('amount')))
            
            conn.commit()
            return project_id
        finally:
            conn.close()

    def get_projects(self, status='OPEN', category=None):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            query = "SELECT * FROM freelance_projects WHERE status = ?"
            params = [status]
            if category:
                query += " AND category = ?"
                params.append(category)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [freelance_db._row_to_dict(row, cursor) for row in rows]
        finally:
            conn.close()

    def get_projects_by_client(self, client_id, status=None):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            query = """
                SELECT p.*, (SELECT COUNT(*) FROM freelance_proposals WHERE project_id = p.id) as proposals_count
                FROM freelance_projects p 
                WHERE p.client_id = ?
            """
            params = [client_id]
            if status:
                query += " AND p.status = ?"
                params.append(status)
            
            query += " ORDER BY p.created_at DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            projects = [freelance_db._row_to_dict(row, cursor) for row in rows]
            
            # Fetch milestones for each project
            for p in projects:
                cursor.execute("SELECT * FROM freelance_project_milestones WHERE project_id = ?", (p['id'],))
                milestone_rows = cursor.fetchall()
                p['milestones'] = [freelance_db._row_to_dict(mr, cursor) for mr in milestone_rows]
                
            return projects
        finally:
            conn.close()

    def get_project_by_id(self, project_id):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM freelance_projects WHERE id = ?", (project_id,))
            row = cursor.fetchone()
            return freelance_db._row_to_dict(row, cursor) if row else None
        finally:
            conn.close()

    # --- Proposal Management ---
    def submit_proposal(self, project_id, freelancer_id, price, delivery_time, message):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO freelance_proposals (project_id, freelancer_id, proposed_price, delivery_time, cover_message)
                VALUES (?, ?, ?, ?, ?)
            """, (project_id, freelancer_id, price, delivery_time, message))
            proposal_id = cursor.lastrowid
            conn.commit()
            return proposal_id
        finally:
            conn.close()

    def get_proposals_by_project(self, project_id):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM freelance_proposals WHERE project_id = ?", (project_id,))
            rows = cursor.fetchall()
            return [freelance_db._row_to_dict(row, cursor) for row in rows]
        finally:
            conn.close()

    def get_proposals_by_freelancer(self, freelancer_id):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT p.*, pr.title as project_title, pr.budget_amount as project_budget
                FROM freelance_proposals p
                JOIN freelance_projects pr ON p.project_id = pr.id
                WHERE p.freelancer_id = ?
                ORDER BY p.created_at DESC
            """, (freelancer_id,))
            rows = cursor.fetchall()
            return [freelance_db._row_to_dict(row, cursor) for row in rows]
        finally:
            conn.close()

    def get_contracts_by_freelancer(self, freelancer_id, status='ACTIVE'):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT c.*, p.title as project_title, p.description as project_description
                FROM freelance_contracts c
                JOIN freelance_projects p ON c.project_id = p.id
                WHERE c.freelancer_id = ? AND c.status = ?
                ORDER BY c.start_date DESC
            """, (freelancer_id, status))
            rows = cursor.fetchall()
            contracts = [freelance_db._row_to_dict(row, cursor) for row in rows]
            
            # Fetch milestones and messages for each contract
            for c in contracts:
                cursor.execute("SELECT * FROM freelance_milestones WHERE contract_id = ?", (c['id'],))
                m_rows = cursor.fetchall()
                c['milestones'] = [freelance_db._row_to_dict(mr, cursor) for mr in m_rows]
                
                cursor.execute("SELECT * FROM freelance_messages WHERE contract_id = ? ORDER BY created_at ASC", (c['id'],))
                msg_rows = cursor.fetchall()
                c['messages'] = [freelance_db._row_to_dict(mgr, cursor) for mgr in msg_rows]
                
            return contracts
        finally:
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
                WHERE c.freelancer_id = ? AND p.escrow_status = 'RELEASED'
            """, (freelancer_id,))
            stats['total_earnings'] = cursor.fetchone()[0] or 0
            
            # Active Projects
            cursor.execute("SELECT COUNT(*) FROM freelance_contracts WHERE freelancer_id = ? AND status = 'ACTIVE'", (freelancer_id,))
            stats['active_projects'] = cursor.fetchone()[0]
            
            # Proposals Sent
            cursor.execute("SELECT COUNT(*) FROM freelance_proposals WHERE freelancer_id = ?", (freelancer_id,))
            stats['proposals_sent'] = cursor.fetchone()[0]
            
            # Average Rating
            cursor.execute("SELECT AVG(rating) FROM freelance_reviews WHERE reviewed_user_id = ?", (freelancer_id,))
            stats['rating'] = round(cursor.fetchone()[0] or 0, 1)
            
            return stats
        finally:
            conn.close()

    def get_notifications(self, user_id, limit=5):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT * FROM freelance_notifications 
                WHERE user_id = ? 
                ORDER BY created_at DESC LIMIT ?
            """, (user_id, limit))
            rows = cursor.fetchall()
            return [freelance_db._row_to_dict(row, cursor) for row in rows]
        finally:
            conn.close()

    def add_notification(self, user_id, type, message):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO freelance_notifications (user_id, type, message) VALUES (?, ?, ?)", (user_id, type, message))
            conn.commit()
        finally:
            conn.close()

    def accept_proposal(self, proposal_id):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            # Get proposal details
            cursor.execute("SELECT * FROM freelance_proposals WHERE id = ?", (proposal_id,))
            proposal = cursor.fetchone()
            if not proposal: return False
            
            proposal_dict = freelance_db._row_to_dict(proposal, cursor)
            project_id = proposal_dict['project_id']
            freelancer_id = proposal_dict['freelancer_id']

            # Update proposal status
            cursor.execute("UPDATE freelance_proposals SET status = 'ACCEPTED' WHERE id = ?", (proposal_id,))
            
            # Update other proposals to REJECTED
            cursor.execute("UPDATE freelance_proposals SET status = 'REJECTED' WHERE project_id = ? AND id != ?", (project_id, proposal_id))
            
            # Update project status
            cursor.execute("UPDATE freelance_projects SET status = 'IN_PROGRESS' WHERE id = ?", (project_id,))
            
            # Create contract
            cursor.execute("SELECT client_id FROM freelance_projects WHERE id = ?", (project_id,))
            client_id = cursor.fetchone()[0]
            
            cursor.execute("""
                INSERT INTO freelance_contracts (project_id, client_id, freelancer_id, status)
                VALUES (?, ?, ?, 'ACTIVE')
            """, (project_id, client_id, freelancer_id))
            contract_id = cursor.lastrowid
            
            # Create milestones for the contract (copy from project milestones)
            cursor.execute("SELECT title, amount FROM freelance_project_milestones WHERE project_id = ?", (project_id,))
            project_milestones = cursor.fetchall()
            for m in project_milestones:
                cursor.execute("""
                    INSERT INTO freelance_milestones (contract_id, title, amount, status)
                    VALUES (?, ?, ?, 'PENDING')
                """, (contract_id, m[0], m[1]))
            
            # Notify freelancer
            self.add_notification(freelancer_id, 'PROPOSAL_ACCEPTED', f"Your proposal for project {project_id} has been accepted!")
            
            conn.commit()
            return True
        finally:
            conn.close()

    def submit_milestone(self, milestone_id):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE freelance_milestones SET status = 'SUBMITTED' WHERE id = ?", (milestone_id,))
            
            # Notify client
            cursor.execute("""
                SELECT c.client_id, m.title FROM freelance_milestones m
                JOIN freelance_contracts c ON m.contract_id = c.id
                WHERE m.id = ?
            """, (milestone_id,))
            row = cursor.fetchone()
            if row:
                self.add_notification(row[0], 'MILESTONE_SUBMITTED', f"Milestone '{row[1]}' has been submitted for review.")
                
            conn.commit()
            return True
        finally:
            conn.close()

    def send_message(self, contract_id, sender_id, message, file_attachment=None):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO freelance_messages (contract_id, sender_id, message, file_attachment)
                VALUES (?, ?, ?, ?)
            """, (contract_id, sender_id, message, file_attachment))
            
            # Notify recipient
            cursor.execute("SELECT client_id, freelancer_id FROM freelance_contracts WHERE id = ?", (contract_id,))
            row = cursor.fetchone()
            if row:
                recipient_id = row[1] if sender_id == row[0] else row[0]
                self.add_notification(recipient_id, 'NEW_MESSAGE', f"New message in project chat.")
                
            conn.commit()
            return True
        finally:
            conn.close()

    # --- Wallet & Payment Logic ---
    # This will be integrated with existing wallet system later
    def release_milestone(self, milestone_id):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE freelance_milestones SET status = 'PAID', approved_at = CURRENT_TIMESTAMP WHERE id = ?", (milestone_id,))
            cursor.execute("UPDATE freelance_payments SET escrow_status = 'RELEASED', released_at = CURRENT_TIMESTAMP WHERE milestone_id = ?", (milestone_id,))
            conn.commit()
            return True
        finally:
            conn.close()

    # --- Direct Booking Management ---
    def create_booking_request(self, client_id, freelancer_id, title, description, amount):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO freelance_bookings (client_id, freelancer_id, project_title, project_description, amount)
                VALUES (?, ?, ?, ?, ?)
            """, (client_id, freelancer_id, title, description, amount))
            booking_id = cursor.lastrowid
            
            # Notify freelancer
            self.add_notification(freelancer_id, 'NEW_BOOKING_REQUEST', f"New direct booking request: {title}")
            
            conn.commit()
            return booking_id
        finally:
            conn.close()

    def get_booking_requests_by_freelancer(self, freelancer_id, status='PENDING'):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT b.*, u.user_name as client_name 
                FROM freelance_bookings b
                JOIN users u ON b.client_id = u.id
                WHERE b.freelancer_id = ? AND b.status = ?
                ORDER BY b.created_at DESC
            """, (freelancer_id, status))
            rows = cursor.fetchall()
            return [freelance_db._row_to_dict(row, cursor) for row in rows]
        finally:
            conn.close()

    def update_booking_status(self, booking_id, status):
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        try:
            # Check current status
            cursor.execute("SELECT status, client_id, project_title, freelancer_id, amount FROM freelance_bookings WHERE id = ?", (booking_id,))
            row = cursor.fetchone()
            if not row or row[0] != 'PENDING':
                return False
                
            client_id, title, freelancer_id, amount = row[1:]
            
            cursor.execute("UPDATE freelance_bookings SET status = ? WHERE id = ?", (status, booking_id))
            
            if status == 'ACCEPTED':
                # Create a project and contract automatically
                cursor.execute("""
                    INSERT INTO freelance_projects 
                    (client_id, title, description, category, budget_type, budget_amount, status)
                    VALUES (?, ?, ?, 'General', 'FIXED', ?, 'IN_PROGRESS')
                """, (client_id, title, "Direct booking project", amount))
                project_id = cursor.lastrowid
                
                # Create contract
                cursor.execute("""
                    INSERT INTO freelance_contracts (project_id, client_id, freelancer_id, status)
                    VALUES (?, ?, ?, 'ACTIVE')
                """, (project_id, client_id, freelancer_id))
                
                self.add_notification(client_id, 'BOOKING_ACCEPTED', f"Your booking request '{title}' was accepted!")
            elif status == 'DECLINED':
                self.add_notification(client_id, 'BOOKING_DECLINED', f"Your booking request '{title}' was declined.")
            
            conn.commit()
            return True
        finally:
            conn.close()

freelance_service = FreelanceService()
