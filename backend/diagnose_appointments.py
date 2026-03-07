#!/usr/bin/env python3

import sqlite3

def check_appointments_database():
    """Check appointments database to understand the issue"""
    
    conn = sqlite3.connect("data/expertease.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("🔍 DIAGNOSING APPOINTMENTS DATABASE")
    print("="*60)
    
    # Check all recent appointments
    cursor.execute("""
        SELECT id, user_id, user_name, worker_id, status, appointment_type, 
               patient_symptoms, booking_date, created_at
        FROM appointments 
        WHERE id >= 15
        ORDER BY id DESC
        LIMIT 10
    """)
    
    appointments = cursor.fetchall()
    
    print(f"📋 RECENT APPOINTMENTS (Total: {len(appointments)})")
    print("-"*60)
    
    for apt in appointments:
        print(f"🏥 Appointment #{apt['id']}")
        print(f"   👤 User ID: {apt['user_id']} | User Name: {apt['user_name']}")
        print(f"   👨‍⚕️ Worker ID: {apt['worker_id']}")
        print(f"   📋 Status: {apt['status']} | Type: {apt['appointment_type']}")
        print(f"   🩺 Symptoms: {apt['patient_symptoms']}")
        print(f"   📅 Date: {apt['booking_date']}")
        print(f"   🕐 Created: {apt['created_at']}")
        print("-"*40)
    
    # Check user accounts
    cursor.execute("""
        SELECT id, username, email, full_name
        FROM users
        WHERE id IN (SELECT DISTINCT user_id FROM appointments WHERE id >= 15)
    """)
    
    users = cursor.fetchall()
    
    print(f"\n👤 RELATED USERS (Total: {len(users)})")
    print("-"*60)
    
    for user in users:
        print(f"👤 User ID: {user['id']}")
        print(f"   📧 Username: {user['username']}")
        print(f"   📧 Email: {user['email']}")
        print(f"   📝 Full Name: {user['full_name']}")
        print("-"*40)
    
    # Check worker accounts
    cursor.execute("""
        SELECT id, email, full_name, specialization
        FROM workers
        WHERE id IN (SELECT DISTINCT worker_id FROM appointments WHERE id >= 15)
    """)
    
    workers = cursor.fetchall()
    
    print(f"\n👨‍⚕️ RELATED WORKERS (Total: {len(workers)})")
    print("-"*60)
    
    for worker in workers:
        print(f"👨‍⚕️ Worker ID: {worker['id']}")
        print(f"   📧 Email: {worker['email']}")
        print(f"   📝 Full Name: {worker['full_name']}")
        print(f"   🩺 Specialization: {worker['specialization']}")
        print("-"*40)
    
    # Check video sessions
    cursor.execute("""
        SELECT id, appointment_id, room_id, doctor_otp, session_status, started_at, ended_at
        FROM video_sessions
        WHERE appointment_id >= 15
        ORDER BY id DESC
        LIMIT 5
    """)
    
    sessions = cursor.fetchall()
    
    print(f"\n🎥 VIDEO SESSIONS (Total: {len(sessions)})")
    print("-"*60)
    
    for session in sessions:
        print(f"🎥 Session ID: {session['id']}")
        print(f"   📋 Appointment ID: {session['appointment_id']}")
        print(f"   🏠 Room ID: {session['room_id']}")
        print(f"   🔑 OTP: {session['doctor_otp']}")
        print(f"   📋 Status: {session['session_status']}")
        print(f"   🕐 Started: {session['started_at'] or 'Not started'}")
        print(f"   🕐 Ended: {session['ended_at'] or 'Not ended'}")
        print("-"*40)
    
    conn.close()
    
    print(f"\n🎯 DIAGNOSIS COMPLETE")
    print("="*60)
    print("📋 What to check:")
    print("1. Are user IDs matching between appointments and users table?")
    print("2. Are appointment statuses correct?")
    print("3. Are video sessions created correctly?")
    print("4. Is the user login returning the correct user_id?")

if __name__ == "__main__":
    check_appointments_database()
