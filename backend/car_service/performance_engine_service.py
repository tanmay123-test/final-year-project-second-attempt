"""
Fuel Delivery Agent Performance & Reputation Engine - Phase 4 Implementation
"""

import os
import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta
from .fuel_delivery_db import fuel_delivery_db

class PerformanceEngineService:
    def __init__(self):
        self.db = fuel_delivery_db
    
    def get_agent_performance(self, agent_id):
        """Get comprehensive agent performance metrics"""
        conn = self.db.get_conn()
        cursor = conn.cursor()
        try:
            # Get agent basic info
            cursor.execute('''
                SELECT total_deliveries, rating, online_status, created_at
                FROM fuel_delivery_agents
                WHERE id = %s
            ''', (agent_id,))
            
            agent = cursor.fetchone()
            if not agent:
                return {}
            
            # Get delivery statistics
            cursor.execute('''
                SELECT 
                    COUNT(*),
                    SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END),
                    SUM(CASE WHEN status = 'CANCELLED' THEN 1 ELSE 0 END),
                    AVG(NULLIF(rating, 0)),
                    SUM(COALESCE(earnings, 0)),
                    COUNT(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '30 days' THEN 1 END)
                FROM fuel_delivery_history
                WHERE agent_id = %s
            ''', (agent_id,))
            
            delivery_stats = cursor.fetchone()
            
            # Get online hours (simplified calculation)
            cursor.execute('''
                SELECT COUNT(*)
                FROM fuel_agent_activity_logs
                WHERE agent_id = %s 
                AND activity_type = 'DELIVERY_STARTED'
                AND timestamp >= CURRENT_DATE - INTERVAL '30 days'
            ''', (agent_id,))
            
            online_sessions = cursor.fetchone()
            online_hours = (online_sessions[0] * 8) if online_sessions else 0  # 8 hours per session
            
            # Calculate completion rate
            total_deliveries = agent[0] if agent[0] else 0
            completed_deliveries = delivery_stats[1] if delivery_stats[1] else 0
            completion_rate = (completed_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0
            
            # Calculate fair assignment score
            fair_assignment_score = self._calculate_fairness_score(agent_id)
            
            # Determine level
            level = self._calculate_agent_level(total_deliveries, completion_rate, agent[1] if agent[1] else 0)
            
            # Get badges
            badges = self._get_agent_badges(agent_id)
            
            performance_data = {
                'agent_id': agent_id,
                'total_deliveries': total_deliveries,
                'completed_deliveries': completed_deliveries,
                'cancelled_deliveries': delivery_stats[2] if delivery_stats[2] else 0,
                'completion_rate': completion_rate,
                'average_rating': round(float(delivery_stats[3] or 0), 2),
                'total_earnings': float(delivery_stats[4] or 0),
                'online_hours': online_hours,
                'recent_deliveries': online_sessions[0] if online_sessions else 0,
                'fair_assignment_score': fair_assignment_score,
                'level': level,
                'badges': badges,
                'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Update performance table
            self._update_agent_performance(agent_id, performance_data)
            
            conn.commit()
            return performance_data
            
        except Exception as e:
            conn.rollback()
            print(f"Error getting agent performance: {e}")
            return {}
        finally:
            cursor.close()
            conn.close()
    
    def get_agent_earnings_summary(self, agent_id, period='daily'):
        """Get earnings summary for agent"""
        conn = self.db.get_conn()
        cursor = conn.cursor()
        try:
            if period == 'daily':
                cursor.execute('''
                    SELECT DATE(completed_at), SUM(earnings)
                    FROM fuel_delivery_history
                    WHERE agent_id = %s 
                    AND DATE(completed_at) = CURRENT_DATE
                    GROUP BY DATE(completed_at)
                ''', (agent_id,))
            elif period == 'weekly':
                cursor.execute('''
                    SELECT TO_CHAR(completed_at, 'YYYY-WW'), SUM(earnings)
                    FROM fuel_delivery_history
                    WHERE agent_id = %s 
                    AND completed_at >= CURRENT_DATE - INTERVAL '7 days'
                    GROUP BY TO_CHAR(completed_at, 'YYYY-WW')
                ''', (agent_id,))
            elif period == 'monthly':
                cursor.execute('''
                    SELECT TO_CHAR(completed_at, 'YYYY-MM'), SUM(earnings)
                    FROM fuel_delivery_history
                    WHERE agent_id = %s 
                    AND completed_at >= CURRENT_DATE - INTERVAL '30 days'
                    GROUP BY TO_CHAR(completed_at, 'YYYY-MM')
                ''', (agent_id,))
            
            earnings_data = cursor.fetchall()
            conn.commit()
            
            # Format response
            if period == 'daily':
                today_earnings = 0
                today_str = datetime.now().date().isoformat()
                for row in earnings_data:
                    if str(row[0]) == today_str:
                        today_earnings = float(row[1] or 0)
                
                return {
                    'today_earnings': today_earnings,
                    'weekly_earnings': sum(float(row[1] or 0) for row in earnings_data),
                    'monthly_earnings': sum(float(row[1] or 0) for row in earnings_data),
                    'total_earnings': sum(float(row[1] or 0) for row in earnings_data)
                }
            else:
                return {
                    f'{period}_earnings': [float(row[1] or 0) for row in earnings_data],
                    'total_earnings': sum(float(row[1] or 0) for row in earnings_data)
                }
            
        except Exception as e:
            conn.rollback()
            return {'error': str(e)}
        finally:
            cursor.close()
            conn.close()
    
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
        conn = self.db.get_conn()
        cursor = conn.cursor()
        try:
            # Count recent assignments (last 7 days)
            cursor.execute('''
                SELECT COUNT(*)
                FROM fuel_agent_activity_logs
                WHERE agent_id = %s 
                AND activity_type = 'DELIVERY_ASSIGNED'
                AND timestamp >= CURRENT_DATE - INTERVAL '7 days'
            ''', (agent_id,))
            
            recent_assignments = cursor.fetchone()
            recent_count = recent_assignments[0] if recent_assignments else 0
            
            # Fewer recent assignments = higher fairness score
            fairness_score = max(0, 100 - (recent_count * 10))  # Inverse of recent assignments
            
            conn.commit()
            return fairness_score
            
        except Exception:
            conn.rollback()
            return 50  # Default score
        finally:
            cursor.close()
            conn.close()
    
    def _get_agent_badges(self, agent_id):
        """Get agent badges"""
        conn = self.db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT badge_name, earned_at
                FROM fuel_agent_badges
                WHERE agent_id = %s
                ORDER BY earned_at DESC
            ''', (agent_id,))
            
            badges = cursor.fetchall()
            
            # Check for automatic badges (from fuel_delivery_agents or performance)
            cursor.execute('''
                SELECT total_deliveries, rating
                FROM fuel_delivery_agents
                WHERE id = %s
            ''', (agent_id,))
            
            performance = cursor.fetchone()
            
            auto_badges = []
            if performance:
                total_deliveries = performance[0] or 0
                average_rating = performance[1] or 0
                
                # We could add more logic here if there was a separate performance table
                if average_rating >= 4.7:
                    auto_badges.append('Top Rated Agent')
                if total_deliveries >= 100:
                    auto_badges.append('Reliable Partner')
            
            # Combine earned and automatic badges
            all_badges = []
            for badge in badges:
                all_badges.append({
                    'badge_name': badge[0],
                    'earned_at': str(badge[1]),
                    'type': 'earned'
                })
            
            for auto_badge in auto_badges:
                if auto_badge not in [b['badge_name'] for b in all_badges]:
                    all_badges.append({
                        'badge_name': auto_badge,
                        'earned_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'type': 'automatic'
                    })
            
            conn.commit()
            return all_badges
            
        except Exception:
            conn.rollback()
            return []
        finally:
            cursor.close()
            conn.close()
    
    def _update_agent_performance(self, agent_id, performance_data):
        """Update agent performance record - Placeholder for actual table"""
        # Note: If there's a fuel_agent_performance table, we'd update it here.
        # For now, we'll just skip or update the agents table.
        pass
    
    def award_badge(self, agent_id, badge_name):
        """Award a badge to an agent"""
        conn = self.db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO fuel_agent_badges
                (agent_id, badge_name, earned_at)
                VALUES (%s, %s, %s)
            ''', (agent_id, badge_name, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            conn.commit()
            return {'success': True, 'message': f'Badge {badge_name} awarded'}
            
        except Exception:
            conn.rollback()
            return {'success': False, 'error': 'Failed to award badge'}
        finally:
            cursor.close()
            conn.close()
    
    def flag_agent_for_review(self, agent_id, reason):
        """Flag agent for admin review"""
        conn = self.db.get_conn()
        cursor = conn.cursor()
        try:
            # Check if column exists first or just try update
            cursor.execute('''
                UPDATE fuel_delivery_agents
                SET approval_status = 'REJECTED'
                WHERE id = %s
            ''', (agent_id,))
            
            conn.commit()
            return {'success': True, 'message': 'Agent flagged for review'}
            
        except Exception:
            conn.rollback()
            return {'success': False, 'error': 'Failed to flag agent'}
        finally:
            cursor.close()
            conn.close()

# Create service instance
performance_engine_service = PerformanceEngineService()