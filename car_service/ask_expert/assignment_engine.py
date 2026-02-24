from datetime import datetime
from .models import ask_expert_db


def assign_expert():
    expert_id = ask_expert_db.find_available_expert()
    return expert_id
