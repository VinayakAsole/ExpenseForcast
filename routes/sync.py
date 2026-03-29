import requests
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.db import get_db_connection
import datetime

sync_bp = Blueprint('sync', __name__)
FIREBASE_DB_URL = "https://phisher-f3680-default-rtdb.firebaseio.com"

@sync_bp.route('/firebase-push', methods=['POST'])
@jwt_required()
def push_to_firebase():
    user_id = get_jwt_identity()
    conn = get_db_connection()
    
    expenses = [dict(row) for row in conn.execute("SELECT id, amount, category, date, notes, recurring, created_at FROM expenses WHERE user_id = ?", (user_id,)).fetchall()]
    incomes = [dict(row) for row in conn.execute("SELECT id, amount, source, date, created_at FROM income WHERE user_id = ?", (user_id,)).fetchall()]
    goals = [dict(row) for row in conn.execute("SELECT id, name, target_amount, current_amount, deadline, category FROM goals WHERE user_id = ?", (user_id,)).fetchall()]
    fds = [dict(row) for row in conn.execute("SELECT * FROM fixed_deposits WHERE user_id = ?", (user_id,)).fetchall()]
    reviews = [dict(row) for row in conn.execute("SELECT * FROM reviews WHERE user_id = ?", (user_id,)).fetchall()]
    
    conn.close()
    
    data = {
        "expenses": expenses,
        "incomes": incomes,
        "goals": goals,
        "fixed_deposits": fds,
        "reviews": reviews,
        "last_synced": datetime.datetime.now().isoformat()
    }
    
    try:
        res = requests.put(f"{FIREBASE_DB_URL}/user_records/user_{user_id}.json", json=data)
        if res.status_code == 200:
            return jsonify({"message": "Database successfully recorded to Firebase"}), 200
        return jsonify({"error": "Firebase DB rejected request"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
