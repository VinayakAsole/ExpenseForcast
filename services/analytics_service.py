import datetime
import json
from models.db import get_db_connection

def get_financial_health_score(user_id):
    now = datetime.datetime.now()
    current_month_start = datetime.datetime(now.year, now.month, 1).strftime('%Y-%m-%d')

    conn = get_db_connection()

    # 1. Savings Ratio (40 points)
    income_query = "SELECT SUM(amount) as total FROM income WHERE user_id = ? AND date >= ?"
    income_res = conn.execute(income_query, (user_id, current_month_start)).fetchone()
    income = income_res['total'] if income_res['total'] else 0

    expense_query = "SELECT SUM(amount) as total FROM expenses WHERE user_id = ? AND date >= ?"
    expense_res = conn.execute(expense_query, (user_id, current_month_start)).fetchone()
    expense = expense_res['total'] if expense_res['total'] else 0

    savings_score = 0
    if income > 0:
        ratio = (income - expense) / income
        savings_score = min(40, max(0, ratio * 40))

    # 2. Budget Adherence (40 points)
    month_str = f"{now.year}-{now.month:02d}"
    budget = conn.execute("SELECT total_budget FROM budgets WHERE user_id = ? AND month = ?", (user_id, month_str)).fetchone()
    budget_score = 0
    if budget and budget['total_budget'] > 0:
        usage = expense / budget['total_budget']
        if usage <= 1:
            budget_score = 40
        elif usage <= 1.5:
            budget_score = max(0, 40 - (usage - 1) * 80)
    elif expense > 0:
        budget_score = 15
    else:
        budget_score = 30 # No spending and no budget

    # 3. Consistency (20 points)
    hist_query = "SELECT SUM(amount) as total FROM expenses WHERE user_id = ? GROUP BY strftime('%Y-%m', date) LIMIT 3"
    past_avgs = conn.execute(hist_query, (user_id,)).fetchall()
    consistency_score = 20
    if len(past_avgs) > 1:
        avg_total = sum(p['total'] for p in past_avgs) / len(past_avgs)
        diff = abs(expense - avg_total)
        consistency_score = max(0, 20 - (diff / max(1, avg_total)) * 20)

    total_score = round(savings_score + budget_score + consistency_score)
    feedback = "Excellent" if total_score >= 80 else "Good" if total_score >= 60 else "Fair" if total_score >= 40 else "Needs Work"
    
    conn.close()
    return {"score": total_score, "feedback": feedback, "summary": f"Your financial health is {feedback}."}

def get_smart_insights(user_id):
    now = datetime.datetime.now()
    current_month_start = datetime.datetime(now.year, now.month, 1).strftime('%Y-%m-%d')
    conn = get_db_connection()
    insights = []
    
    # Highest category insight
    cat_query = "SELECT category, SUM(amount) as total FROM expenses WHERE user_id = ? AND date >= ? GROUP BY category ORDER BY total DESC LIMIT 1"
    cat_agg = conn.execute(cat_query, (user_id, current_month_start)).fetchone()
    if cat_agg:
        insights.append(f"Top category: {cat_agg['category']} (₹{cat_agg['total']:.2f}).")
        
    # Budget alert
    month_str = f"{now.year}-{now.month:02d}"
    budget = conn.execute("SELECT total_budget FROM budgets WHERE user_id = ? AND month = ?", (user_id, month_str)).fetchone()
    if budget and budget['total_budget'] > 0:
        expense_query = "SELECT SUM(amount) as total FROM expenses WHERE user_id = ? AND date >= ?"
        expense_res = conn.execute(expense_query, (user_id, current_month_start)).fetchone()
        expense = expense_res['total'] if expense_res['total'] else 0
        usage = (expense / budget['total_budget']) * 100
        if usage >= 100:
            insights.append(f"ALERT: Exceeded your ₹{budget['total_budget']} monthly budget!")
        elif usage >= 80:
            insights.append(f"Warning: used {usage:.1f}% of your monthly budget.")

    conn.close()
    return insights
