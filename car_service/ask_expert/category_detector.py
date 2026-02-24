def detect_category(problem_description: str) -> str:
    if not problem_description:
        return "General"
    text = problem_description.lower()
    if "dashboard" in text or "battery" in text:
        return "Electrical"
    if "engine" in text or "smoke" in text:
        return "Engine"
    if "brake" in text:
        return "Brake"
    if "tyre" in text or "tire" in text:
        return "Tyre"
    if "overheating" in text or "heat" in text or "coolant" in text:
        return "Cooling"
    return "General"
