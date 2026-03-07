# meeting_utils.py
import uuid

def generate_meeting_link():
    room_id = uuid.uuid4().hex[:10]
    return f"https://meet.jit.si/expertease-{room_id}"
