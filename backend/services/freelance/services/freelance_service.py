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

freelance_service = FreelanceService()
