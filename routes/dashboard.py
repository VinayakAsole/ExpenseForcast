import datetime
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.db import get_db_connection
from services.analytics_service import get_financial_health_score, get_smart_insights
from ml.forecasting import get_forecast_data

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/', methods=['GET'])
@jwt_required()
def get_dashboard_data():
    user_id = get_jwt_identity()
    conn = get_db_connection()
    
    # 1. Stats
    now = datetime.datetime.now()
    current_month_start = datetime.datetime(now.year, now.month, 1).strftime('%Y-%m-%d')

    expenses_res = conn.execute("SELECT SUM(amount) as total FROM expenses WHERE user_id = ? AND date >= ?", (user_id, current_month_start)).fetchone()
    total_spent = expenses_res['total'] if expenses_res['total'] else 0

    income_res = conn.execute("SELECT SUM(amount) as total FROM income WHERE user_id = ? AND date >= ?", (user_id, current_month_start)).fetchone()
    total_income = income_res['total'] if income_res['total'] else 0

    # 2. Category Distribution
    category_distribution = conn.execute("""
        SELECT category as name, SUM(amount) as value 
        FROM expenses 
        WHERE user_id = ? AND date >= ? 
        GROUP BY category
    """, (user_id, current_month_start)).fetchall()

    # 3. Monthly Trends (Last 6 Months)
    six_months_ago = (now - datetime.timedelta(days=180)).strftime('%Y-%m-%d')
    monthly_trends = conn.execute("""
        SELECT strftime('%Y-%m', date) as name, SUM(amount) as amount
        FROM expenses
        WHERE user_id = ? AND date >= ?
        GROUP BY name
        ORDER BY name ASC
    """, (user_id, six_months_ago)).fetchall()

    conn.close()

    # 4. AI Services
    health = get_financial_health_score(user_id)
    insights = get_smart_insights(user_id)
    forecast = get_forecast_data(user_id)

    return jsonify({
        "health": health,
        "insights": insights,
        "forecast": forecast,
        "total_spent": total_spent,
        "total_income": total_income,
        "category_distribution": [dict(c) for c in category_distribution],
        "monthly_trends": [dict(m) for m in monthly_trends]
    }), 200
