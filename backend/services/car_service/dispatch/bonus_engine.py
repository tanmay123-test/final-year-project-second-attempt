"""
Car Service Bonus Engine
Calculates bonuses based on job conditions and performance
"""

from datetime import datetime, time

class BonusEngine:
    """Calculate bonuses for mechanics based on various factors"""
    
    @staticmethod
    def calculate_bonus(job_data: dict) -> float:
        """
        Calculate bonus based on job conditions
        
        Args:
            job_data: Dictionary containing job information
                - priority: 'EMERGENCY' or 'NORMAL'
                - created_at: job creation time
                - distance_km: distance to job
                - issue_type: type of issue
                - user_city: job location
        
        Returns:
            Bonus amount in rupees
        """
        bonus = 0.0
        
        # Emergency job bonus
        if job_data.get('priority') == 'EMERGENCY':
            bonus += 100.0
        
        # Night shift bonus (10 PM - 6 AM)
        try:
            job_time = datetime.fromisoformat(job_data.get('created_at', datetime.now().isoformat()))
            if job_time.time() >= time(22, 0) or job_time.time() <= time(6, 0):
                bonus += 50.0
        except:
            pass
        
        # Distance bonus (long distance jobs)
        distance = job_data.get('distance_km', 0)
        if distance > 10:
            bonus += 25.0
        elif distance > 20:
            bonus += 50.0
        
        # Issue type bonus
        issue_type = job_data.get('issue_type', '').lower()
        if issue_type in ['engine repair', 'transmission', 'electrical']:
            bonus += 30.0  # Complex jobs
        elif issue_type in ['brake repair', 'battery replacement']:
            bonus += 15.0  # Medium complexity
        
        # Location bonus (remote areas)
        city = job_data.get('user_city', '').lower()
        remote_cities = ['thane', 'navi mumbai', 'kalyan', 'vasai', 'virar']
        if any(remote in city for remote in remote_cities):
            bonus += 40.0
        
        # Weekend bonus
        try:
            job_time = datetime.fromisoformat(job_data.get('created_at', datetime.now().isoformat()))
            if job_time.weekday() >= 5:  # Saturday or Sunday
                bonus += 20.0
        except:
            pass
        
        return round(bonus, 2)
    
    @staticmethod
    def get_bonus_breakdown(job_data: dict) -> dict:
        """
        Get detailed breakdown of bonus calculation
        
        Returns:
            Dictionary with bonus components and explanations
        """
        breakdown = {
            'total_bonus': 0.0,
            'components': []
        }
        
        # Emergency bonus
        if job_data.get('priority') == 'EMERGENCY':
            breakdown['components'].append({
                'type': 'Emergency Job',
                'amount': 100.0,
                'reason': 'Urgent repair required'
            })
            breakdown['total_bonus'] += 100.0
        
        # Night shift bonus
        try:
            job_time = datetime.fromisoformat(job_data.get('created_at', datetime.now().isoformat()))
            if job_time.time() >= time(22, 0) or job_time.time() <= time(6, 0):
                breakdown['components'].append({
                    'type': 'Night Shift',
                    'amount': 50.0,
                    'reason': 'Late night service (10 PM - 6 AM)'
                })
                breakdown['total_bonus'] += 50.0
        except:
            pass
        
        # Distance bonus
        distance = job_data.get('distance_km', 0)
        if distance > 20:
            breakdown['components'].append({
                'type': 'Long Distance',
                'amount': 50.0,
                'reason': f'Far location ({distance:.1f} km)'
            })
            breakdown['total_bonus'] += 50.0
        elif distance > 10:
            breakdown['components'].append({
                'type': 'Medium Distance',
                'amount': 25.0,
                'reason': f'Medium distance ({distance:.1f} km)'
            })
            breakdown['total_bonus'] += 25.0
        
        # Issue type bonus
        issue_type = job_data.get('issue_type', '').lower()
        if issue_type in ['engine repair', 'transmission', 'electrical']:
            breakdown['components'].append({
                'type': 'Complex Job',
                'amount': 30.0,
                'reason': f'Complex repair: {issue_type}'
            })
            breakdown['total_bonus'] += 30.0
        elif issue_type in ['brake repair', 'battery replacement']:
            breakdown['components'].append({
                'type': 'Medium Complexity',
                'amount': 15.0,
                'reason': f'Medium complexity: {issue_type}'
            })
            breakdown['total_bonus'] += 15.0
        
        # Location bonus
        city = job_data.get('user_city', '').lower()
        remote_cities = ['thane', 'navi mumbai', 'kalyan', 'vasai', 'virar']
        if any(remote in city for remote in remote_cities):
            breakdown['components'].append({
                'type': 'Remote Location',
                'amount': 40.0,
                'reason': f'Remote area service: {city}'
            })
            breakdown['total_bonus'] += 40.0
        
        # Weekend bonus
        try:
            job_time = datetime.fromisoformat(job_data.get('created_at', datetime.now().isoformat()))
            if job_time.weekday() >= 5:  # Saturday or Sunday
                breakdown['components'].append({
                    'type': 'Weekend',
                    'amount': 20.0,
                    'reason': 'Weekend service'
                })
                breakdown['total_bonus'] += 20.0
        except:
            pass
        
        breakdown['total_bonus'] = round(breakdown['total_bonus'], 2)
        return breakdown

# Global instance
bonus_engine = BonusEngine()
