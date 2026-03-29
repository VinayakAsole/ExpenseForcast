import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.db import get_db_connection

goal_bp = Blueprint('goals', __name__)

@goal_bp.route('/', methods=['GET'])
@jwt_required()
def get_goals():
    user_id = get_jwt_identity()
    conn = get_db_connection()
    goals = conn.execute("SELECT * FROM goals WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()
    return jsonify([dict(g) for g in goals]), 200

@goal_bp.route('/', methods=['POST'])
@jwt_required()
def add_goal():
    user_id = get_jwt_identity()
    data = request.json
    name = data['name']
    target_amount = float(data['target_amount'])
    current_amount = float(data.get('current_amount', 0))
    deadline = data['deadline']
    category = data.get('category', 'Short-term')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO goals (user_id, name, target_amount, current_amount, deadline, category) VALUES (?, ?, ?, ?, ?, ?)",
                   (user_id, name, target_amount, current_amount, deadline, category))
    conn.commit()
    goal_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": goal_id, "status": "success"}), 201

@goal_bp.route('/<goal_id>', methods=['PUT'])
@jwt_required()
def update_goal(goal_id):
    user_id = get_jwt_identity()
    data = request.json
    
    set_clause = []
    params = []
    for k, v in data.items():
        if k in ['name', 'target_amount', 'current_amount', 'deadline', 'category']:
            set_clause.append(f"{k} = ?")
            params.append(v)
    
    if not set_clause:
        return jsonify({"error": "No valid fields provided"}), 400
        
    set_str = ", ".join(set_clause)
    params.extend([goal_id, user_id])
    
    conn = get_db_connection()
    result = conn.execute(f"UPDATE goals SET {set_str} WHERE id = ? AND user_id = ?", params)
    conn.commit()
    count = result.rowcount
    conn.close()
    if count:
        return jsonify({"message": "Goal updated"}), 200
    return jsonify({"error": "Goal not found"}), 404

@goal_bp.route('/<goal_id>', methods=['DELETE'])
@jwt_required()
def delete_goal(goal_id):
    user_id = get_jwt_identity()
    conn = get_db_connection()
    result = conn.execute("DELETE FROM goals WHERE id = ? AND user_id = ?", (goal_id, user_id))
    conn.commit()
    deleted = result.rowcount
    conn.close()
    if deleted:
        return jsonify({"message": "Goal deleted"}), 200
    return jsonify({"error": "Goal not found"}), 404
