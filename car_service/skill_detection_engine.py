"""
Skill Detection Engine
Analyzes issue descriptions and detects required mechanic skills
"""

import re
from typing import Dict, List, Tuple

class SkillDetectionEngine:
    def __init__(self):
        # Skill keyword mappings with confidence scores
        self.skill_keywords = {
            "Engine Specialist": {
                "keywords": ["engine", "motor", "starting", "wont start", "crank", "overheating", "temperature", "smoke", "stall", "misfire"],
                "confidence": 0.9,
                "patterns": [
                    r"engine.*not.*start",
                    r"car.*wont.*start",
                    r"overheating",
                    r"engine.*smoke",
                    r"check.*engine"
                ]
            },
            "Brake Specialist": {
                "keywords": ["brake", "braking", "pads", "disc", "drum", "abs", "squeaking", "grinding", "brake fail", "stuck brake"],
                "confidence": 0.95,
                "patterns": [
                    r"brake.*fail",
                    r"brake.*stuck",
                    r"brake.*squeak",
                    r"brake.*grind",
                    r"abs.*light"
                ]
            },
            "Electrical Specialist": {
                "keywords": ["battery", "electrical", "wiring", "fuse", "alternator", "starter", "lights", "horn", "power", "dead battery"],
                "confidence": 0.85,
                "patterns": [
                    r"battery.*dead",
                    r"lights.*not.*work",
                    r"power.*window",
                    r"alternator",
                    r"starter.*motor"
                ]
            },
            "Tire Specialist": {
                "keywords": ["tire", "tyre", "puncture", "flat", "wheel", "alignment", "balancing", "rotation", "pressure"],
                "confidence": 0.9,
                "patterns": [
                    r"flat.*tire",
                    r"tire.*puncture",
                    r"wheel.*alignment",
                    r"tire.*pressure"
                ]
            },
            "Transmission Specialist": {
                "keywords": ["transmission", "gear", "clutch", "shifting", "automatic", "manual", "gearbox", "slipping"],
                "confidence": 0.9,
                "patterns": [
                    r"transmission.*slip",
                    r"gear.*not.*shift",
                    r"clutch.*slip",
                    r"automatic.*transmission"
                ]
            },
            "AC & Cooling Specialist": {
                "keywords": ["ac", "air conditioning", "cooling", "radiator", "fan", "compressor", "refrigerant", "hvac"],
                "confidence": 0.85,
                "patterns": [
                    r"ac.*not.*work",
                    r"air.*conditioning",
                    r"radiator.*leak",
                    r"cooling.*fan"
                ]
            },
            "Suspension Specialist": {
                "keywords": ["suspension", "shock", "strut", "spring", "bushing", "alignment", "steering", "wheel bearing"],
                "confidence": 0.85,
                "patterns": [
                    r"suspension.*noise",
                    r"shock.*absorber",
                    r"steering.*wheel",
                    r"wheel.*bearing"
                ]
            },
            "General Mechanic": {
                "keywords": ["general", "service", "maintenance", "checkup", "inspection", "oil change", "routine"],
                "confidence": 0.7,
                "patterns": [
                    r"general.*service",
                    r"routine.*maintenance",
                    r"oil.*change",
                    r"car.*checkup"
                ]
            }
        }
    
    def detect_skill(self, issue_description: str) -> Tuple[str, float]:
        """
        Detect required skill from issue description
        
        Returns:
            Tuple of (skill_name, confidence_score)
        """
        if not issue_description:
            return "General Mechanic", 0.5
        
        # Normalize input
        description = issue_description.lower().strip()
        
        best_skill = "General Mechanic"
        best_confidence = 0.5
        
        # Check each skill
        for skill_name, skill_data in self.skill_keywords.items():
            confidence = self._calculate_skill_confidence(description, skill_data)
            
            if confidence > best_confidence:
                best_skill = skill_name
                best_confidence = confidence
        
        return best_skill, best_confidence
    
    def _calculate_skill_confidence(self, description: str, skill_data: Dict) -> float:
        """Calculate confidence score for a specific skill"""
        confidence = 0.0
        keyword_matches = 0
        pattern_matches = 0
        
        # Check keyword matches
        for keyword in skill_data["keywords"]:
            if keyword in description:
                keyword_matches += 1
                confidence += 0.2
        
        # Check pattern matches
        for pattern in skill_data["patterns"]:
            if re.search(pattern, description, re.IGNORECASE):
                pattern_matches += 1
                confidence += 0.3
        
        # Apply base confidence
        if keyword_matches > 0 or pattern_matches > 0:
            confidence = min(confidence * skill_data["confidence"], 1.0)
        else:
            confidence = 0.0
        
        return confidence
    
    def get_all_skill_matches(self, issue_description: str) -> List[Tuple[str, float]]:
        """
        Get all skill matches with confidence scores
        
        Returns:
            List of tuples (skill_name, confidence_score) sorted by confidence
        """
        if not issue_description:
            return [("General Mechanic", 0.5)]
        
        description = issue_description.lower().strip()
        matches = []
        
        for skill_name, skill_data in self.skill_keywords.items():
            confidence = self._calculate_skill_confidence(description, skill_data)
            if confidence > 0.1:  # Only include meaningful matches
                matches.append((skill_name, confidence))
        
        # Sort by confidence (highest first)
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return matches if matches else [("General Mechanic", 0.5)]
    
    def get_skill_keywords(self, skill_name: str) -> List[str]:
        """Get keywords for a specific skill"""
        if skill_name in self.skill_keywords:
            return self.skill_keywords[skill_name]["keywords"]
        return []
    
    def add_custom_skill(self, skill_name: str, keywords: List[str], confidence: float = 0.8):
        """Add a custom skill to the detection engine"""
        self.skill_keywords[skill_name] = {
            "keywords": keywords,
            "confidence": confidence,
            "patterns": [rf"\\b{keyword}\\b" for keyword in keywords]
        }
    
    def get_skill_statistics(self, issue_description: str) -> Dict:
        """Get detailed statistics about skill detection"""
        matches = self.get_all_skill_matches(issue_description)
        
        return {
            "issue_description": issue_description,
            "detected_skill": matches[0][0] if matches else "General Mechanic",
            "confidence": matches[0][1] if matches else 0.5,
            "all_matches": matches,
            "total_keywords_found": len(matches),
            "high_confidence_matches": [m for m in matches if m[1] >= 0.7]
        }

# Global instance
skill_detection_engine = SkillDetectionEngine()
