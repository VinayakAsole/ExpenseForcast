import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.db import get_db_connection

income_bp = Blueprint('income', __name__)

@income_bp.route('/', methods=['GET'])
@jwt_required()
def get_incomes():
    user_id = get_jwt_identity()
    conn = get_db_connection()
    incomes = conn.execute("SELECT * FROM income WHERE user_id = ? ORDER BY date DESC", (user_id,)).fetchall()
    conn.close()
    return jsonify([dict(inc) for inc in incomes]), 200

@income_bp.route('/', methods=['POST'])
@jwt_required()
def add_income():
    user_id = get_jwt_identity()
    data = request.json
    amount = float(data['amount'])
    source = data['source']
    date = data.get('date', datetime.datetime.now().strftime('%Y-%m-%d'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO income (user_id, amount, source, date) VALUES (?, ?, ?, ?)",
                   (user_id, amount, source, date))
    conn.commit()
    income_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": income_id, "status": "success"}), 201

@income_bp.route('/<income_id>', methods=['PUT'])
@jwt_required()
def update_income(income_id):
    user_id = get_jwt_identity()
    data = request.json
    amount = float(data['amount'])
    source = data['source']
    date = data['date']

    conn = get_db_connection()
    result = conn.execute(
        "UPDATE income SET amount = ?, source = ?, date = ? WHERE id = ? AND user_id = ?",
        (amount, source, date, income_id, user_id)
    )
    conn.commit()
    updated = result.rowcount
    conn.close()
    if updated: return jsonify({"message": "Income updated"}), 200
    return jsonify({"error": "Income not found"}), 404

@income_bp.route('/<income_id>', methods=['DELETE'])
@jwt_required()
def delete_income(income_id):
    user_id = get_jwt_identity()
    conn = get_db_connection()
    result = conn.execute("DELETE FROM income WHERE id = ? AND user_id = ?", (income_id, user_id))
    conn.commit()
    deleted = result.rowcount
    conn.close()
    if deleted: return jsonify({"message": "Income deleted"}), 200
    return jsonify({"error": "Income not found"}), 404
