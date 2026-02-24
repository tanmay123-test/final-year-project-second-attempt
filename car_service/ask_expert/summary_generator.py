from .models import ask_expert_db


def generate_summary(request_id: int) -> str:
    req = ask_expert_db.get_request(request_id)
    messages = ask_expert_db.get_messages(request_id)
    problem = req[3] if req else ""
    last_expert = ""
    for mid, sender_type, sender_id, text, ts in messages[::-1]:
        if sender_type.upper() == "EXPERT":
            last_expert = text
            break
    summary = f"Issue: {problem}\nAdvice: {last_expert or 'N/A'}"
    ask_expert_db.save_summary(request_id, summary)
    return summary
