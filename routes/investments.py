import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.db import get_db_connection

investments_bp = Blueprint('investments', __name__)

@investments_bp.route('/fd', methods=['GET'])
@jwt_required()
def get_fds():
    user_id = get_jwt_identity()
    conn = get_db_connection()
    fds = conn.execute("SELECT * FROM fixed_deposits WHERE user_id = ? ORDER BY maturity_date ASC", (user_id,)).fetchall()
    conn.close()
    return jsonify({"fds": [dict(f) for f in fds]}), 200

@investments_bp.route('/fd', methods=['POST'])
@jwt_required()
def add_fd():
    user_id = get_jwt_identity()
    data = request.json
    
    bank_name = data['bank_name']
    principal = float(data['principal'])
    interest_rate = float(data['interest_rate'])
    start_date = data['start_date']
    maturity_date = data['maturity_date']
    category = data.get('category', 'Standard')
    notes = data.get('notes', '')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO fixed_deposits (user_id, bank_name, principal, interest_rate, start_date, maturity_date, category, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, bank_name, principal, interest_rate, start_date, maturity_date, category, notes))
    conn.commit()
    fd_id = cursor.lastrowid
    conn.close()

    return jsonify({"id": fd_id, "status": "success"}), 201

@investments_bp.route('/fd/<fd_id>', methods=['DELETE'])
@jwt_required()
def delete_fd(fd_id):
    user_id = get_jwt_identity()
    conn = get_db_connection()
    result = conn.execute("DELETE FROM fixed_deposits WHERE id = ? AND user_id = ?", (fd_id, user_id))
    conn.commit()
    deleted = result.rowcount
    conn.close()
    if deleted:
        return jsonify({"message": "FD certificate removed"}), 200
    return jsonify({"error": "Certificate not found"}), 404
