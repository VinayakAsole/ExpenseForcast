import datetime
import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.db import get_db_connection

budget_bp = Blueprint('budgets', __name__)

@budget_bp.route('/', methods=['GET'])
@jwt_required()
def get_budgets():
    user_id = get_jwt_identity()
    month = request.args.get('month')
    query = "SELECT * FROM budgets WHERE user_id = ?"
    params = [user_id]
    if month:
        query += " AND month = ?"
        params.append(month)
    
    conn = get_db_connection()
    budgets = conn.execute(query, params).fetchall()
    conn.close()
    
    result = []
    for b in budgets:
        item = dict(b)
        item['category_budgets'] = json.loads(b['category_budgets']) if b['category_budgets'] else {}
        result.append(item)
    return jsonify(result), 200

@budget_bp.route('/', methods=['POST'])
@jwt_required()
def upsert_budget():
    user_id = get_jwt_identity()
    data = request.json
    month = data.get('month', datetime.datetime.now().strftime('%Y-%m'))
    total_budget = float(data.get('total_budget', 0))
    category_budgets = json.dumps(data.get('category_budgets', {}))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO budgets (user_id, month, total_budget, category_budgets)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id, month) DO UPDATE SET
            total_budget = excluded.total_budget,
            category_budgets = excluded.category_budgets,
            updated_at = CURRENT_TIMESTAMP
    """, (user_id, month, total_budget, category_budgets))
    conn.commit()
    conn.close()
    return jsonify({"message": "Budget updated"}), 200
