from flask import request
import jwt
import datetime
from config import JWT_SECRET, JWT_EXP_MINUTES


def generate_token(username):
    payload = {
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=JWT_EXP_MINUTES)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def verify_token(token):
    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return data["username"]
    except:
        return None


def get_current_user_id():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    token = auth_header.split(' ')[1]
    username_or_email = verify_token(token)
    if not username_or_email:
        return None
    
    # Imports here to avoid circular dependencies
    from user_db import UserDB
    from worker_db import WorkerDB

    # 1. Check UserDB (for clients)
    user_db = UserDB()
    user_id = user_db.get_user_by_username(username_or_email)
    if user_id:
        return user_id
        
    # 2. Check WorkerDB (for freelancers)
    worker_db = WorkerDB()
    worker = worker_db.get_worker_by_email(username_or_email)
    if worker:
        return worker['id']
        
    return None
