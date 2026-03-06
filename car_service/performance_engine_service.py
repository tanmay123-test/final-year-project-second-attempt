"""
Fuel Delivery Agent Performance & Reputation Engine - Phase 4 Implementation
"""

import sqlite3
from datetime import datetime, timedelta
from .fuel_delivery_db import fuel_delivery_db

class PerformanceEngineService:
    def __init__(self):
        self.db = fuel_delivery_db
    
    def get_agent_performance(self, agent_id):
        """Get comprehensive agent performance metrics"""
        try:
            cursor = self.db.conn.cursor()
            
            # Get agent basic info
            cursor.execute('''
                SELECT total_deliveries, rating, online_status, created_at
                FROM fuel_delivery_agents
                WHERE id = ?
            ''', (agent_id,))
            
            agent = cursor.fetchone()
            if not agent:
                return {}
            
            # Get delivery statistics
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_deliveries,
                    SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) as completed_deliveries,
                    SUM(CASE WHEN status = 'CANCELLED' THEN 1 ELSE 0 END) as cancelled_deliveries,
                    AVG(rating) as average_rating
                    SUM(agent_earning) as total_earnings
                    COUNT(CASE WHEN created_at >= DATE('now', '-30 days') THEN 1 ELSE 0 END) as recent_deliveries
                FROM fuel_delivery_history
                WHERE agent_id = ?
            ''', (agent_id,))
            
            delivery_stats = cursor.fetchone()
            
            # Get online hours (simplified calculation)
            cursor.execute('''
                SELECT COUNT(*) as online_sessions
                FROM fuel_agent_activity_logs
                WHERE agent_id = ? 
                AND activity_type = 'DELIVERY_STARTED'
                AND created_at >= DATE('now', '-30 days')
            ''', (agent_id,))
            
            online_sessions = cursor.fetchone()
            online_hours = online_sessions[0] * 8 if online_sessions else 0  # 8 hours per session
            
            # Calculate completion rate
            total_deliveries = agent[1] if agent[1] else 0
            completed_deliveries = delivery_stats[1] if delivery_stats[1] else 0
            completion_rate = (completed_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0
            
            # Calculate fair assignment score
            fair_assignment_score = self._calculate_fairness_score(agent_id)
            
            # Determine level
            level = self._calculate_agent_level(total_deliveries, completion_rate, agent[2] if agent[2] else 0)
            
            # Get badges
            badges = self._get_agent_badges(agent_id)
            
            performance_data = {
                'agent_id': agent_id,
                'total_deliveries': total_deliveries,
                'completed_deliveries': completed_deliveries,
                'cancelled_deliveries': delivery_stats[2] if delivery_stats[2] else 0,
                'completion_rate': completion_rate,
                'average_rating': round(delivery_stats[2] if delivery_stats[2] else 0, 2) if delivery_stats[2] else 0,
                'total_earnings': delivery_stats[3] if delivery_stats[3] else 0,
                'online_hours': online_hours,
                'recent_deliveries': online_sessions[0] if online_sessions else 0,
                'fair_assignment_score': fair_assignment_score,
                'level': level,
                'badges': badges,
                'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Update performance table
            self._update_agent_performance(agent_id, performance_data)
            
            self.db.conn.commit()
            cursor.close()
            
            return performance_data
            
        except Exception as e:
            return {}
    
    def get_agent_earnings_summary(self, agent_id, period='daily'):
        """Get earnings summary for agent"""
        try:
            cursor = self.db.conn.cursor()
            
            if period == 'daily':
                cursor.execute('''
                    SELECT DATE(completed_at) as date, SUM(agent_earning) as earnings
                    FROM fuel_delivery_history
                    WHERE agent_id = ? 
                    AND DATE(completed_at) = CURRENT_DATE
                    GROUP BY DATE(completed_at)
                ''', (agent_id,))
            elif period == 'weekly':
                cursor.execute('''
                    SELECT strftime('%Y-%W', completed_at) as week, SUM(agent_earning) as earnings
                    FROM fuel_delivery_history
                    WHERE agent_id = ? 
                    AND completed_at >= DATE('now', '-7 days')
                    GROUP BY strftime('%Y-%W', completed_at)
                ''', (agent_id,))
            elif period == 'monthly':
                cursor.execute('''
                    SELECT strftime('%Y-%m', completed_at) as month, SUM(agent_earning) as earnings
                    FROM fuel_delivery_history
                    WHERE agent_id = ? 
                    AND completed_at >= DATE('now', '-30 days')
                    GROUP BY strftime('%Y-%m', completed_at)
                ''', (agent_id,))
            
            earnings_data = cursor.fetchall()
            
            # Format response
            if period == 'daily':
                today_earnings = 0
                for row in earnings_data:
                    if row[0] == datetime.now().strftime('%Y-%m-%d'):
                        today_earnings = row[1]
                
                return {
                    'today_earnings': today_earnings,
                    'weekly_earnings': sum(row[1] for row in earnings_data),
                    'monthly_earnings': sum(row[1] for row in earnings_data),
                    'total_earnings': sum(row[1] for row in earnings_data)
                }
            else:
                return {
                    f'{period}_earnings': [row[1] for row in earnings_data],
                    'total_earnings': sum(row[1] for row in earnings_data)
                }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_agent_level(self, total_deliveries, completion_rate, rating):
        """Calculate agent level based on performance"""
        if total_deliveries >= 500:
            return 'PLATINUM'
        elif total_deliveries >= 200:
            return 'GOLD'
        elif total_deliveries >= 50:
            return 'SILVER'
        else:
            return 'BRONZE'
    
    def _calculate_fairness_score(self, agent_id):
        """Calculate fairness score for dispatch priority"""
        try:
            cursor = self.db.conn.cursor()
            
            # Count recent assignments (last 7 days)
            cursor.execute('''
                SELECT COUNT(*) as recent_assignments
                FROM fuel_agent_activity_logs
                WHERE agent_id = ? 
                AND activity_type = 'DELIVERY_ASSIGNED'
                AND created_at >= DATE('now', '-7 days')
            ''', (agent_id,))
            
            recent_assignments = cursor.fetchone()
            recent_count = recent_assignments[0] if recent_assignments else 0
            
            # Fewer recent assignments = higher fairness score
            fairness_score = max(0, 100 - (recent_count * 10))  # Inverse of recent assignments
            
            self.db.conn.commit()
            cursor.close()
            
            return fairness_score
            
        except Exception:
            return 50  # Default score
    
    def _get_agent_badges(self, agent_id):
        """Get agent badges"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                SELECT badge_name, earned_at
                FROM fuel_agent_badges
                WHERE agent_id = ?
                ORDER BY earned_at DESC
            ''', (agent_id,))
            
            badges = cursor.fetchall()
            
            # Check for automatic badges
            cursor.execute('''
                SELECT total_deliveries, completion_rate, average_rating
                FROM fuel_delivery_performance
                WHERE agent_id = ?
            ''', (agent_id,))
            
            performance = cursor.fetchone()
            
            auto_badges = []
            if performance:
                total_deliveries = performance[0] or 0
                completion_rate = performance[1] or 0
                average_rating = performance[2] or 0
                
                if completion_rate >= 95:
                    auto_badges.append('Safe Fuel Handler')
                if average_rating >= 4.7:
                    auto_badges.append('Top Rated Agent')
                if total_deliveries >= 100:
                    auto_badges.append('Reliable Partner')
            
            # Combine earned and automatic badges
            all_badges = []
            for badge in badges:
                all_badges.append({
                    'badge_name': badge[0],
                    'earned_at': badge[1],
                    'type': 'earned'
                })
            
            for auto_badge in auto_badges:
                if auto_badge not in [b['badge_name'] for b in all_badges]:
                    all_badges.append({
                        'badge_name': auto_badge,
                        'earned_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'type': 'automatic'
                    })
            
            self.db.conn.commit()
            cursor.close()
            
            return all_badges
            
        except Exception:
            return []
    
    def _update_agent_performance(self, agent_id, performance_data):
        """Update agent performance record"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO fuel_agent_performance
                (agent_id, total_deliveries, completed_deliveries, cancelled_deliveries, 
                 completion_rate, average_rating, total_earnings, online_hours, 
                 recent_deliveries, fair_assignment_score, level, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                agent_id,
                performance_data['total_deliveries'],
                performance_data['completed_deliveries'],
                performance_data['cancelled_deliveries'],
                performance_data['completion_rate'],
                performance_data['average_rating'],
                performance_data['total_earnings'],
                performance_data['online_hours'],
                performance_data['recent_deliveries'],
                performance_data['fair_assignment_score'],
                performance_data['level'],
                performance_data['updated_at']
            ))
            
            self.db.conn.commit()
            cursor.close()
            
        except Exception:
            pass  # Don't fail main flow due to logging errors
    
    def award_badge(self, agent_id, badge_name):
        """Award a badge to an agent"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                INSERT INTO fuel_agent_badges
                (agent_id, badge_name, earned_at)
                VALUES (?, ?, ?)
            ''', (agent_id, badge_name, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            self.db.conn.commit()
            cursor.close()
            
            return {'success': True, 'message': f'Badge {badge_name} awarded'}
            
        except Exception:
            return {'success': False, 'error': 'Failed to award badge'}
    
    def flag_agent_for_review(self, agent_id, reason):
        """Flag agent for admin review"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                UPDATE fuel_delivery_agents
                SET flagged_for_review = 1, review_reason = ?
                WHERE id = ?
            ''', (reason, agent_id))
            
            self.db.conn.commit()
            cursor.close()
            
            return {'success': True, 'message': 'Agent flagged for review'}
            
        except Exception:
            return {'success': False, 'error': 'Failed to flag agent'}

# Create service instance
performance_engine_service = PerformanceEngineService()
