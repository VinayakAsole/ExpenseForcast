import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.db import get_db_connection

report_bp = Blueprint('reports', __name__)

@report_bp.route('/', methods=['GET'])
@jwt_required()
def get_report():
    user_id = get_jwt_identity()
    month = request.args.get('month') # format YYYY-MM
    if not month:
        return jsonify({"error": "Month is required"}), 400

    year, mon = map(int, month.split('-'))
    start = f"{year}-{mon:02d}-01"
    if mon == 12:
        end = f"{year + 1}-01-01"
    else:
        end = f"{year}-{mon + 1:02d}-01"

    conn = get_db_connection()
    expenses = conn.execute("SELECT * FROM expenses WHERE user_id = ? AND date >= ? AND date < ? ORDER BY date ASC", (user_id, start, end)).fetchall()
    incomes = conn.execute("SELECT * FROM income WHERE user_id = ? AND date >= ? AND date < ? ORDER BY date ASC", (user_id, start, end)).fetchall()

    total_income = sum(i['amount'] for i in incomes)
    total_expense = sum(e['amount'] for e in expenses)

    expense_categories = ["Food", "Rent", "Transport", "Entertainment", "Utilities", "Shopping", "Healthcare", "Investment", "Education", "Other"]
    
    # Store results in a dictionary for easy merging
    summary_dict = {cat: 0 for cat in expense_categories}
    category_rows = conn.execute("""
        SELECT category as name, SUM(amount) as total 
        FROM expenses 
        WHERE user_id = ? AND date >= ? AND date < ? 
        GROUP BY category
    """, (user_id, start, end)).fetchall()
    
    for row in category_rows:
        if row['name'] in summary_dict:
            summary_dict[row['name']] = row['total']
        else:
            # Handle categories that might not be in our default list if any
            summary_dict[row['name']] = row['total']

    # Convert back to sorted list of dicts for frontend (sorted by total descending)
    category_summary = [{"name": k, "total": v} for k, v in summary_dict.items()]
    category_summary.sort(key=lambda x: x['total'], reverse=True)

    conn.close()

    return jsonify({
        "month": month,
        "summary": {
            "total_income": total_income,
            "total_expense": total_expense,
            "net_savings": total_income - total_expense,
            "expense_to_income_ratio": round(total_expense / total_income, 2) if total_income > 0 else 0
        },
        "category_summary": category_summary,
        "expenses": [dict(e) for e in expenses],
        "incomes": [dict(i) for i in incomes]
    }), 200
