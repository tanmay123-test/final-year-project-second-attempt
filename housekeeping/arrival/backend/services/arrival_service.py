import json
from housekeeping.models.database import housekeeping_db

class ArrivalService:
    def __init__(self):
        self.db = housekeeping_db

    def get_home_page_data(self, user_id):
        # 1. Top 10 Services
        services = self.db.get_all_services()
        
        # 2. Upcoming Bookings (if user_id provided)
        upcoming = []
        if user_id:
            all_bookings = self.db.get_user_bookings(user_id)
            # Filter for PENDING or ACCEPTED
            upcoming = [b for b in all_bookings if b['status'] in ['PENDING', 'ACCEPTED', 'ASSIGNED', 'IN_PROGRESS']]
            
        return {
            "top_services": services,
            "upcoming_bookings": upcoming[:3] # Show top 3
        }

    def get_all_services(self):
        services = self.db.get_all_services()
        # Parse JSON fields if necessary (sqlite returns text)
        for s in services:
            if isinstance(s.get('add_ons'), str):
                try:
                    s['add_ons'] = json.loads(s['add_ons'])
                except:
                    s['add_ons'] = []
        return services

    def create_booking_intent(self, data):
        # Calculate price based on service, size, extras
        service_name = data.get('service_name')
        home_size = data.get('home_size', 'Standard')
        extras = data.get('extras', []) # List of extra names
        
        service = self.db.get_service_details(service_name)
        if not service:
            return {"error": "Service not found"}
            
        base_price = service['base_price']
        
        # Size multiplier (Mock logic)
        size_mult = 1.0
        if home_size == 'Large': size_mult = 1.5
        elif home_size == 'Villa': size_mult = 2.0
        
        # Extras cost
        extras_cost = 0
        service_addons = []
        if isinstance(service['add_ons'], str):
             try:
                 service_addons = json.loads(service['add_ons'])
             except:
                 pass
        
        # Simple matching for extras price
        for extra_name in extras:
            for addon in service_addons:
                if addon['name'] == extra_name:
                    extras_cost += addon['price']
                    
        total_price = (base_price * size_mult) + extras_cost
        
        return {
            "service": service_name,
            "home_size": home_size,
            "extras": extras,
            "price_breakdown": {
                "base": base_price,
                "size_multiplier": size_mult,
                "extras_total": extras_cost
            },
            "total_price": total_price,
            "estimated_duration": service['duration']
        }

    def confirm_booking(self, data):
        # Create the booking in DB
        # data should contain: user_id, service_type, address, date, time, price, home_size, extras
        required = ['user_id', 'service_type', 'address', 'date', 'time', 'price']
        if not all(k in data for k in required):
            return {"error": "Missing fields"}, 400
            
        extras_json = json.dumps(data.get('extras', []))
        
        booking_id = self.db.create_booking(
            data['user_id'],
            data['service_type'],
            data['address'],
            data['date'],
            data['time'],
            data['price'],
            data.get('home_size'),
            extras_json,
            data.get('payment_method', 'Cash')
        )
        
        if booking_id:
            return {"success": True, "booking_id": booking_id, "message": "Booking confirmed"}, 201
        else:
            return {"error": "Database error"}, 500
