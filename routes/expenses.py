import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.db import get_db_connection

expense_bp = Blueprint('expenses', __name__)

@expense_bp.route('/', methods=['GET'])
@jwt_required()
def get_expenses():
    user_id = get_jwt_identity()
    category = request.args.get('category')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = "SELECT * FROM expenses WHERE user_id = ?"
    params = [user_id]
    
    if category:
        query += " AND category = ?"
        params.append(category)
    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)
    
    query += " ORDER BY date DESC"

    conn = get_db_connection()
    expenses = conn.execute(query, params).fetchall()
    conn.close()

    return jsonify({"expenses": [dict(e) for e in expenses]}), 200

@expense_bp.route('/', methods=['POST'])
@jwt_required()
def add_expense():
    user_id = get_jwt_identity()
    data = request.json
    
    date = data.get('date', datetime.datetime.now().strftime('%Y-%m-%d'))
    amount = float(data['amount'])
    category = data['category']
    notes = data.get('notes', '')
    recurring = 1 if data.get('recurring') else 0

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (user_id, amount, category, date, notes, recurring) VALUES (?, ?, ?, ?, ?, ?)",
                   (user_id, amount, category, date, notes, recurring))
    conn.commit()
    expense_id = cursor.lastrowid
    conn.close()

    return jsonify({"id": expense_id, "status": "success"}), 201

@expense_bp.route('/<expense_id>', methods=['PUT'])
@jwt_required()
def update_expense(expense_id):
    user_id = get_jwt_identity()
    data = request.json
    
    amount = float(data['amount'])
    category = data['category']
    date = data['date']
    notes = data.get('notes', '')

    conn = get_db_connection()
    result = conn.execute(
        "UPDATE expenses SET amount = ?, category = ?, date = ?, notes = ? WHERE id = ? AND user_id = ?",
        (amount, category, date, notes, expense_id, user_id)
    )
    conn.commit()
    updated = result.rowcount
    conn.close()

    if updated:
        return jsonify({"message": "Expense updated"}), 200
    return jsonify({"error": "Expense not found"}), 404

@expense_bp.route('/<expense_id>', methods=['DELETE'])
@jwt_required()
def delete_expense(expense_id):
    user_id = get_jwt_identity()
    conn = get_db_connection()
    result = conn.execute("DELETE FROM expenses WHERE id = ? AND user_id = ?", (expense_id, user_id))
    conn.commit()
    deleted = result.rowcount
    conn.close()
    if deleted:
        return jsonify({"message": "Expense deleted"}), 200
    return jsonify({"error": "Expense not found"}), 404
