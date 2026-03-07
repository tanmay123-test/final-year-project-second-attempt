"""
Smart Search CLI Test Interface
CLI for testing the Smart Search Engine
"""

import requests
import json
from typing import Dict, List

API_BASE = "http://127.0.0.1:5000"

class SmartSearchCLI:
    def __init__(self):
        self.api_base = API_BASE
    
    def run_interactive_search(self):
        """Run interactive smart search"""
        print("\n" + "="*60)
        print("🔍 SMART SEARCH - NEARBY MECHANIC DISCOVERY")
        print("="*60)
        
        # Get issue description
        issue = input("\nEnter issue description: ").strip()
        if not issue:
            print("❌ Issue description cannot be empty")
            return
        
        # Get location
        print("\nLocation options:")
        print("1. Enter location name (e.g., 'Asalpha Mumbai')")
        print("2. Enter GPS coordinates")
        
        choice = input("Select option (1 or 2): ").strip()
        
        location_data = {}
        
        if choice == "1":
            location_name = input("Enter location name: ").strip()
            if not location_name:
                print("❌ Location name cannot be empty")
                return
            location_data["location_name"] = location_name
        
        elif choice == "2":
            try:
                latitude = float(input("Enter latitude: ").strip())
                longitude = float(input("Enter longitude: ").strip())
                location_data["latitude"] = latitude
                location_data["longitude"] = longitude
            except ValueError:
                print("❌ Invalid coordinates")
                return
        
        else:
            print("❌ Invalid choice")
            return
        
        # Get search options
        try:
            radius = float(input("Enter search radius in km (default 5): ").strip() or "5")
            max_results = int(input("Enter max results (default 10): ").strip() or "10")
        except ValueError:
            radius = 5.0
            max_results = 10
        
        # Perform search
        print(f"\n🔍 Searching for mechanics...")
        print(f"Issue: {issue}")
        print(f"Location: {location_data}")
        print(f"Radius: {radius} km")
        print(f"Max results: {max_results}")
        
        result = self._smart_search(issue, location_data, radius, max_results)
        
        # Display results
        self._display_search_results(result)
    
    def _smart_search(self, issue: str, location_data: Dict, radius: float = 5.0, max_results: int = 10) -> Dict:
        """Call smart search API"""
        try:
            payload = {
                "issue_description": issue,
                "location_data": location_data,
                "search_radius_km": radius,
                "max_results": max_results
            }
            
            response = requests.post(f"{self.api_base}/api/car/smart-search", json=payload)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}",
                    "message": response.text
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": "Network error",
                "message": str(e)
            }
    
    def _display_search_results(self, result: Dict):
        """Display search results"""
        print("\n" + "="*60)
        print("📋 SEARCH RESULTS")
        print("="*60)
        
        if not result.get("success", False):
            print(f"❌ Search failed: {result.get('error', 'Unknown error')}")
            if result.get("message"):
                print(f"Details: {result['message']}")
            return
        
        print(f"📍 Location: {result.get('user_location', 'Unknown')}")
        print(f"🔧 Required Skill: {result.get('required_skill', 'Unknown')}")
        print(f"📏 Search Radius: {result.get('search_radius_km', 5)} km")
        
        if result.get("from_cache"):
            print("⚡ Results from cache")
        
        mechanics = result.get("mechanics", [])
        total_results = result.get("total_results", 0)
        
        if not mechanics:
            print(f"\n📭 No mechanics found within {result.get('search_radius_km', 5)} km")
            print("💡 Try increasing search radius or check location")
            return
        
        print(f"\n🎯 Found {total_results} nearby mechanics:")
        print("-" * 60)
        
        for i, mechanic in enumerate(mechanics, 1):
            print(f"\n{i}. 👤 {mechanic['name']}")
            print(f"   🔧 Skill: {mechanic['skill']}")
            print(f"   📏 Distance: {mechanic['distance_km']} km")
            print(f"   ⏱️ ETA: {mechanic['eta_minutes']} minutes")
            print(f"   ⭐ Rating: {mechanic['rating']}/5.0")
            print(f"   💼 Experience: {mechanic['experience']} years")
            print(f"   📱 Phone: {mechanic['phone']}")
            print(f"   📧 Email: {mechanic['email']}")
            print(f"   🟢 Status: {mechanic['status']}")
            
            if i < len(mechanics):
                print("-" * 40)
    
    def test_skill_detection(self):
        """Test skill detection engine"""
        print("\n" + "="*60)
        print("🧠 SKILL DETECTION TEST")
        print("="*60)
        
        issue = input("\nEnter issue description: ").strip()
        if not issue:
            print("❌ Issue description cannot be empty")
            return
        
        try:
            payload = {"issue_description": issue}
            response = requests.post(f"{self.api_base}/api/car/smart-search/skill/detect", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"\n📝 Issue: {result['issue_description']}")
                print(f"🎯 Detected Skill: {result['detected_skill']}")
                print(f"📊 Confidence: {result['confidence']:.2f}")
                
                print(f"\n🔍 All Skill Matches:")
                for skill, confidence in result['all_matches']:
                    print(f"   • {skill}: {confidence:.2f}")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
        
        except Exception as e:
            print(f"❌ Network error: {e}")
    
    def test_location_resolution(self):
        """Test location resolution engine"""
        print("\n" + "="*60)
        print("📍 LOCATION RESOLUTION TEST")
        print("="*60)
        
        location_name = input("\nEnter location name: ").strip()
        if not location_name:
            print("❌ Location name cannot be empty")
            return
        
        try:
            payload = {"location_name": location_name}
            response = requests.post(f"{self.api_base}/api/car/smart-search/location/resolve", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                location = result['location']
                
                print(f"\n📍 Location: {location['name']}")
                print(f"🌍 Coordinates: {location['latitude']:.4f}, {location['longitude']:.4f}")
                print(f"✅ Resolved: {location['resolved']}")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
        
        except Exception as e:
            print(f"❌ Network error: {e}")
    
    def test_keyword_search(self):
        """Test keyword search using FTS5"""
        print("\n" + "="*60)
        print("🔍 KEYWORD SEARCH TEST")
        print("="*60)
        
        keyword = input("\nEnter search keyword: ").strip()
        if not keyword:
            print("❌ Keyword cannot be empty")
            return
        
        try:
            payload = {"keyword": keyword}
            response = requests.post(f"{self.api_base}/api/car/smart-search/keyword", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"\n🔍 Keyword: {result['keyword']}")
                print(f"📊 Total Results: {result['total_results']}")
                
                mechanics = result.get("mechanics", [])
                if mechanics:
                    print(f"\n🎯 Found Mechanics:")
                    for i, mechanic in enumerate(mechanics, 1):
                        print(f"\n{i}. 👤 {mechanic['name']}")
                        print(f"   🔧 Skills: {mechanic['skills']}")
                        print(f"   📧 Email: {mechanic['email']}")
                        print(f"   ⭐ Rating: {mechanic.get('rating', 'N/A')}")
                else:
                    print(f"\n📭 No mechanics found for '{keyword}'")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
        
        except Exception as e:
            print(f"❌ Network error: {e}")
    
    def show_statistics(self):
        """Show search engine statistics"""
        print("\n" + "="*60)
        print("📊 SEARCH ENGINE STATISTICS")
        print("="*60)
        
        try:
            response = requests.get(f"{self.api_base}/api/car/smart-search/statistics")
            
            if response.status_code == 200:
                result = response.json()
                stats = result['statistics']
                
                print(f"📈 Cache Size: {stats.get('cache_size', 0)} entries")
                print(f"⚡ ETA Cache Size: {stats.get('eta_cache_size', 0)} entries")
                print(f"👷 Total Mechanics: {stats.get('total_mechanics', 0)}")
                print(f"🟢 Online Mechanics: {stats.get('online_mechanics', 0)}")
                print(f"✅ Available Mechanics: {stats.get('available_mechanics', 0)}")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
        
        except Exception as e:
            print(f"❌ Network error: {e}")
    
    def health_check(self):
        """Check smart search engine health"""
        print("\n" + "="*60)
        print("🏥 SMART SEARCH HEALTH CHECK")
        print("="*60)
        
        try:
            response = requests.get(f"{self.api_base}/api/car/smart-search/health")
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success"):
                    print("✅ Smart Search Engine is running")
                    print("\n🔧 Components Status:")
                    components = result.get("components", {})
                    for component, status in components.items():
                        print(f"   • {component}: {status}")
                else:
                    print(f"❌ Smart Search Engine error: {result.get('error')}")
            else:
                print(f"❌ Health check failed: {response.status_code}")
        
        except Exception as e:
            print(f"❌ Network error: {e}")
    
    def run_menu(self):
        """Run main CLI menu"""
        while True:
            print("\n" + "="*60)
            print("🔍 SMART SEARCH CLI")
            print("="*60)
            print("1. 🔍 Smart Search (Nearby Mechanics)")
            print("2. 🧠 Test Skill Detection")
            print("3. 📍 Test Location Resolution")
            print("4. 🔍 Test Keyword Search")
            print("5. 📊 Show Statistics")
            print("6. 🏥 Health Check")
            print("7. ❌ Exit")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "1":
                self.run_interactive_search()
            elif choice == "2":
                self.test_skill_detection()
            elif choice == "3":
                self.test_location_resolution()
            elif choice == "4":
                self.test_keyword_search()
            elif choice == "5":
                self.show_statistics()
            elif choice == "6":
                self.health_check()
            elif choice == "7":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please try again.")

def main():
    """Main function"""
    cli = SmartSearchCLI()
    cli.run_menu()

if __name__ == "__main__":
    main()
