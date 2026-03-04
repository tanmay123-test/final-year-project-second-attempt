#!/usr/bin/env python3
"""
Smart Search Setup Script
Initializes the Smart Search Engine with sample data
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'car_service'))

from smart_search_db import smart_search_db
from car_service_worker_db import car_service_worker_db
from location_resolution_engine import location_resolution_engine

def setup_smart_search():
    """Setup smart search system with sample data"""
    print("🚀 Setting up Smart Search Engine...")
    
    # 1. Initialize database tables
    print("✅ Database tables initialized")
    
    # 2. Get all mechanics and add them to FTS5
    print("🔧 Adding mechanics to FTS5 search...")
    workers = car_service_worker_db.get_all_workers()
    mechanics = [w for w in workers if w.get('role') == 'Mechanic']
    
    for mechanic in mechanics:
        smart_search_db.update_mechanic_fts(
            mechanic_id=mechanic['id'],
            name=mechanic.get('name', 'Unknown'),
            skills=mechanic.get('skills', 'General Mechanic'),
            service_area=mechanic.get('city', 'Mumbai')
        )
        print(f"   • {mechanic.get('name', 'Unknown')} - {mechanic.get('skills', 'General')}")
    
    # 3. Add sample mechanic locations
    print("📍 Adding sample mechanic locations...")
    
    # Sample locations for mechanics in Mumbai
    sample_locations = {
        2: (19.0954, 72.8783),  # Tanmay - Asalpha
        # Add more mechanics as needed
    }
    
    for mechanic_id, (lat, lon) in sample_locations.items():
        smart_search_db.update_mechanic_location(mechanic_id, lat, lon)
        print(f"   • Mechanic {mechanic_id}: {lat}, {lon}")
    
    print("✅ Smart Search Engine setup complete!")
    print(f"📊 Total mechanics in FTS5: {len(mechanics)}")
    print(f"📍 Total locations added: {len(sample_locations)}")

def test_components():
    """Test all smart search components"""
    print("\n🧪 Testing Smart Search Components...")
    
    # Test location resolution
    print("\n1. 📍 Testing Location Resolution...")
    try:
        location = location_resolution_engine.resolve_location({"location_name": "Asalpha Mumbai"})
        print(f"   ✅ Asalpha Mumbai → ({location.latitude:.4f}, {location.longitude:.4f})")
    except Exception as e:
        print(f"   ❌ Location resolution error: {e}")
    
    # Test skill detection
    print("\n2. 🧠 Testing Skill Detection...")
    try:
        from skill_detection_engine import skill_detection_engine
        skill, confidence = skill_detection_engine.detect_skill("my car brake is stuck")
        print(f"   ✅ 'brake is stuck' → {skill} (confidence: {confidence:.2f})")
    except Exception as e:
        print(f"   ❌ Skill detection error: {e}")
    
    # Test FTS5 search
    print("\n3. 🔍 Testing FTS5 Search...")
    try:
        results = smart_search_db.search_mechanics_fts("tanmay")
        print(f"   ✅ FTS5 search for 'tanmay' → {len(results)} results")
        for result in results:
            print(f"      • {result.get('name', 'Unknown')}")
    except Exception as e:
        print(f"   ❌ FTS5 search error: {e}")
    
    # Test distance calculation
    print("\n4. 📏 Testing Distance Calculation...")
    try:
        distance = smart_search_db.calculate_distance(19.0954, 72.8783, 19.0836, 72.8896)
        print(f"   ✅ Asalpha to Ghatkopar → {distance:.2f} km")
    except Exception as e:
        print(f"   ❌ Distance calculation error: {e}")
    
    print("\n✅ Component testing complete!")

def main():
    """Main setup function"""
    print("="*60)
    print("🚗 SMART SEARCH ENGINE SETUP")
    print("="*60)
    
    try:
        setup_smart_search()
        test_components()
        
        print("\n" + "="*60)
        print("🎉 SMART SEARCH ENGINE READY!")
        print("="*60)
        print("📋 Next steps:")
        print("1. Start the server: python app.py")
        print("2. Test with CLI: python car_service/smart_search_cli.py")
        print("3. Or use API: POST /api/car/smart-search")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
