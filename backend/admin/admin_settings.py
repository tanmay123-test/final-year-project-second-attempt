"""
Admin routes for platform settings management.
"""

from flask import Blueprint, request, jsonify
import sqlite3
import json
from datetime import datetime

settings_admin_bp = Blueprint('settings_admin', __name__, url_prefix='/settings')

def get_db_connection():
    """Get database connection for admin operations"""
    conn = sqlite3.connect('expertease.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_settings_table():
    """Create settings table if it doesn't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_key TEXT UNIQUE NOT NULL,
            setting_value TEXT,
            setting_type TEXT DEFAULT 'string',
            description TEXT,
            category TEXT DEFAULT 'general',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

# Initialize default settings
DEFAULT_SETTINGS = {
    # General Settings
    "platform_name": {"value": "ExpertEase", "type": "string", "category": "general", "description": "Platform name"},
    "platform_version": {"value": "1.0.0", "type": "string", "category": "general", "description": "Platform version"},
    "maintenance_mode": {"value": "false", "type": "boolean", "category": "general", "description": "Enable maintenance mode"},
    
    # Commission Settings
    "healthcare_commission": {"value": "20", "type": "number", "category": "commission", "description": "Healthcare service commission percentage"},
    "housekeeping_commission": {"value": "15", "type": "number", "category": "commission", "description": "Housekeeping service commission percentage"},
    "freelance_commission": {"value": "10", "type": "number", "category": "commission", "description": "Freelance service commission percentage"},
    "car_service_commission": {"value": "18", "type": "number", "category": "commission", "description": "Car service commission percentage"},
    "money_management_commission": {"value": "12", "type": "number", "category": "commission", "description": "Money management commission percentage"},
    
    # Service Settings
    "healthcare_service_available": {"value": "true", "type": "boolean", "category": "services", "description": "Enable healthcare service"},
    "housekeeping_service_available": {"value": "true", "type": "boolean", "category": "services", "description": "Enable housekeeping service"},
    "freelance_service_available": {"value": "true", "type": "boolean", "category": "services", "description": "Enable freelance service"},
    "car_service_available": {"value": "true", "type": "boolean", "category": "services", "description": "Enable car service"},
    "money_management_available": {"value": "true", "type": "boolean", "category": "services", "description": "Enable money management service"},
    
    # Pricing Settings
    "healthcare_default_fee": {"value": "500", "type": "number", "category": "pricing", "description": "Default healthcare consultation fee"},
    "housekeeping_default_rate": {"value": "300", "type": "number", "category": "pricing", "description": "Default housekeeping hourly rate"},
    "freelance_min_rate": {"value": "100", "type": "number", "category": "pricing", "description": "Minimum freelance hourly rate"},
    "car_service_base_fee": {"value": "200", "type": "number", "category": "pricing", "description": "Base car service fee"},
    "money_management_fee": {"value": "1000", "type": "number", "category": "pricing", "description": "Money management consultation fee"},
    
    # Worker Settings
    "auto_approve_workers": {"value": "false", "type": "boolean", "category": "workers", "description": "Auto-approve worker registrations"},
    "worker_verification_required": {"value": "true", "type": "boolean", "category": "workers", "description": "Require worker document verification"},
    "max_appointments_per_day": {"value": "20", "type": "number", "category": "workers", "description": "Maximum appointments per worker per day"},
    
    # User Settings
    "user_verification_required": {"value": "true", "type": "boolean", "category": "users", "description": "Require user email verification"},
    "max_appointments_per_user": {"value": "5", "type": "number", "category": "users", "description": "Maximum appointments per user per day"},
    
    # Notification Settings
    "email_notifications_enabled": {"value": "true", "type": "boolean", "category": "notifications", "description": "Enable email notifications"},
    "sms_notifications_enabled": {"value": "false", "type": "boolean", "category": "notifications", "description": "Enable SMS notifications"},
    "push_notifications_enabled": {"value": "true", "type": "boolean", "category": "notifications", "description": "Enable push notifications"},
    
    # Payment Settings
    "payment_gateway_enabled": {"value": "true", "type": "boolean", "category": "payments", "description": "Enable payment gateway"},
    "refund_policy_days": {"value": "7", "type": "number", "category": "payments", "description": "Refund policy in days"},
    "payment_timeout_minutes": {"value": "15", "type": "number", "category": "payments", "description": "Payment timeout in minutes"}
}

def initialize_default_settings():
    """Initialize default settings if they don't exist"""
    create_settings_table()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for key, config in DEFAULT_SETTINGS.items():
        cursor.execute("""
            INSERT OR IGNORE INTO admin_settings (setting_key, setting_value, setting_type, description, category)
            VALUES (?, ?, ?, ?, ?)
        """, (key, config['value'], config['type'], config['description'], config['category']))
    
    conn.commit()
    conn.close()

@settings_admin_bp.route('/', methods=['GET'])
def get_all_settings():
    """
    Get all platform settings grouped by category.
    
    Query Parameters:
    - category: Filter by category (general, commission, services, pricing, workers, users, notifications, payments)
    
    Returns:
    {
        "settings": {
            "general": [
                {
                    "key": "platform_name",
                    "value": "ExpertEase",
                    "type": "string",
                    "description": "Platform name",
                    "updated_at": "2024-01-01 10:00:00"
                }
            ],
            "commission": [...]
        }
    }
    """
    try:
        category_filter = request.args.get('category')
        
        initialize_default_settings()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM admin_settings"
        params = []
        
        if category_filter:
            query += " WHERE category = ?"
            params.append(category_filter)
        
        query += " ORDER BY category, setting_key"
        
        cursor.execute(query, params)
        settings = {}
        
        for row in cursor.fetchall():
            setting = dict(row)
            category = setting['category']
            
            if category not in settings:
                settings[category] = []
            
            settings[category].append(setting)
        
        conn.close()
        
        return jsonify({"settings": settings}), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch settings: {str(e)}"}), 500

@settings_admin_bp.route('/<setting_key>', methods=['GET'])
def get_setting(setting_key):
    """
    Get a specific setting by key.
    
    Returns:
    {
        "setting": {
            "key": "platform_name",
            "value": "ExpertEase",
            "type": "string",
            "description": "Platform name",
            "category": "general",
            "updated_at": "2024-01-01 10:00:00"
        }
    }
    """
    try:
        initialize_default_settings()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM admin_settings WHERE setting_key = ?", (setting_key,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return jsonify({"error": "Setting not found"}), 404
        
        setting = dict(row)
        conn.close()
        
        return jsonify({"setting": setting}), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch setting: {str(e)}"}), 500

@settings_admin_bp.route('/', methods=['POST'])
def update_settings():
    """
    Update multiple settings.
    
    Request Body:
    {
        "settings": {
            "platform_name": "ExpertEase Pro",
            "healthcare_commission": "25",
            "maintenance_mode": "false"
        }
    }
    
    Returns:
    {
        "message": "Settings updated successfully",
        "updated_settings": {...}
    }
    """
    try:
        data = request.get_json()
        if not data or not data.get('settings'):
            return jsonify({"error": "Settings data is required"}), 400
        
        settings_to_update = data.get('settings')
        updated_settings = {}
        
        initialize_default_settings()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for key, value in settings_to_update.items():
            # Check if setting exists
            cursor.execute("SELECT setting_type FROM admin_settings WHERE setting_key = ?", (key,))
            row = cursor.fetchone()
            
            if not row:
                conn.close()
                return jsonify({"error": f"Setting '{key}' not found"}), 404
            
            setting_type = row['setting_type']
            
            # Validate value type
            if setting_type == 'boolean' and value not in ['true', 'false']:
                conn.close()
                return jsonify({"error": f"Setting '{key}' must be 'true' or 'false'"}), 400
            elif setting_type == 'number':
                try:
                    float(value)
                except ValueError:
                    conn.close()
                    return jsonify({"error": f"Setting '{key}' must be a number"}), 400
            
            # Update setting
            cursor.execute("""
                UPDATE admin_settings 
                SET setting_value = ?, updated_at = CURRENT_TIMESTAMP
                WHERE setting_key = ?
            """, (str(value), key))
            
            updated_settings[key] = value
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "message": "Settings updated successfully",
            "updated_settings": updated_settings
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to update settings: {str(e)}"}), 500

@settings_admin_bp.route('/<setting_key>', methods=['POST'])
def update_setting(setting_key):
    """
    Update a specific setting.
    
    Request Body:
    {
        "value": "ExpertEase Pro"
    }
    
    Returns:
    {
        "message": "Setting updated successfully",
        "setting": {
            "key": "platform_name",
            "value": "ExpertEase Pro",
            "updated_at": "2024-01-01 10:00:00"
        }
    }
    """
    try:
        data = request.get_json()
        if not data or 'value' not in data:
            return jsonify({"error": "Setting value is required"}), 400
        
        new_value = str(data['value'])
        
        initialize_default_settings()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if setting exists and get type
        cursor.execute("SELECT setting_type FROM admin_settings WHERE setting_key = ?", (setting_key,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return jsonify({"error": "Setting not found"}), 404
        
        setting_type = row['setting_type']
        
        # Validate value type
        if setting_type == 'boolean' and new_value not in ['true', 'false']:
            conn.close()
            return jsonify({"error": "Setting must be 'true' or 'false'"}), 400
        elif setting_type == 'number':
            try:
                float(new_value)
            except ValueError:
                conn.close()
                return jsonify({"error": "Setting must be a number"}), 400
        
        # Update setting
        cursor.execute("""
            UPDATE admin_settings 
            SET setting_value = ?, updated_at = CURRENT_TIMESTAMP
            WHERE setting_key = ?
        """, (new_value, setting_key))
        
        # Get updated setting
        cursor.execute("SELECT * FROM admin_settings WHERE setting_key = ?", (setting_key,))
        updated_row = cursor.fetchone()
        
        conn.commit()
        conn.close()
        
        updated_setting = dict(updated_row)
        
        return jsonify({
            "message": "Setting updated successfully",
            "setting": updated_setting
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to update setting: {str(e)}"}), 500

@settings_admin_bp.route('/reset', methods=['POST'])
def reset_settings():
    """
    Reset settings to default values.
    
    Request Body:
    {
        "category": "commission"  // Optional: reset specific category only
    }
    
    Returns:
    {
        "message": "Settings reset successfully",
        "reset_count": 25
    }
    """
    try:
        data = request.get_json() or {}
        category_filter = data.get('category')
        
        initialize_default_settings()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        reset_count = 0
        
        for key, config in DEFAULT_SETTINGS.items():
            if category_filter and config['category'] != category_filter:
                continue
            
            cursor.execute("""
                UPDATE admin_settings 
                SET setting_value = ?, updated_at = CURRENT_TIMESTAMP
                WHERE setting_key = ?
            """, (config['value'], key))
            
            if cursor.rowcount > 0:
                reset_count += 1
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "message": "Settings reset successfully",
            "reset_count": reset_count
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to reset settings: {str(e)}"}), 500

@settings_admin_bp.route('/export', methods=['GET'])
def export_settings():
    """
    Export all settings as JSON.
    
    Returns:
    {
        "settings": {
            "platform_name": "ExpertEase",
            "healthcare_commission": "20",
            ...
        },
        "exported_at": "2024-01-01 10:00:00"
    }
    """
    try:
        initialize_default_settings()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT setting_key, setting_value FROM admin_settings")
        settings = {}
        
        for row in cursor.fetchall():
            settings[row['setting_key']] = row['setting_value']
        
        conn.close()
        
        return jsonify({
            "settings": settings,
            "exported_at": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to export settings: {str(e)}"}), 500

@settings_admin_bp.route('/import', methods=['POST'])
def import_settings():
    """
    Import settings from JSON.
    
    Request Body:
    {
        "settings": {
            "platform_name": "ExpertEase Pro",
            "healthcare_commission": "25",
            ...
        }
    }
    
    Returns:
    {
        "message": "Settings imported successfully",
        "imported_count": 25
    }
    """
    try:
        data = request.get_json()
        if not data or not data.get('settings'):
            return jsonify({"error": "Settings data is required"}), 400
        
        settings_to_import = data.get('settings')
        imported_count = 0
        
        initialize_default_settings()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for key, value in settings_to_import.items():
            # Check if setting exists
            cursor.execute("SELECT setting_type FROM admin_settings WHERE setting_key = ?", (key,))
            row = cursor.fetchone()
            
            if row:
                setting_type = row['setting_type']
                
                # Validate value type
                if setting_type == 'boolean' and str(value) not in ['true', 'false']:
                    continue
                elif setting_type == 'number':
                    try:
                        float(value)
                    except ValueError:
                        continue
                
                # Update setting
                cursor.execute("""
                    UPDATE admin_settings 
                    SET setting_value = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE setting_key = ?
                """, (str(value), key))
                
                if cursor.rowcount > 0:
                    imported_count += 1
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "message": "Settings imported successfully",
            "imported_count": imported_count
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to import settings: {str(e)}"}), 500
