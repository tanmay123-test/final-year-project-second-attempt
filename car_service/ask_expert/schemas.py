def serialize_request_row(row):
    return {
        "id": row[0],
        "user_id": row[1],
        "assigned_expert_id": row[2],
        "problem_description": row[3],
        "category": row[4],
        "location": row[5],
        "status": row[6],
        "created_at": row[7],
        "resolved_at": row[8]
    }


def serialize_message_row(row):
    return {
        "id": row[0],
        "sender_type": row[1],
        "sender_id": row[2],
        "message_text": row[3],
        "created_at": row[4]
    }
