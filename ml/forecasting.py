import datetime
import numpy as np
from models.db import get_db_connection

def simple_linear_regression(data):
    """
    Fits a linear model y = mx + b to the given data points.
    Returns the predicted y for x = len(data).
    """
    n = len(data)
    if n < 2:
        return data[-1]['amount'] if n == 1 else 0

    x = np.array(range(n))
    y = np.array([item['amount'] for item in data])

    # Calculate slope (m) and intercept (b)
    sum_x = np.sum(x)
    sum_y = np.sum(y)
    sum_xy = np.sum(x * y)
    sum_x2 = np.sum(x**2)

    m = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)
    b = (sum_y - m * sum_x) / n

    # Predict for next month (x = n)
    prediction = m * n + b
    return max(0, float(prediction))

def get_forecast_data(user_id):
    """
    Analyzes last 6 months of habit and predicts next month.
    """
    conn = get_db_connection()
    
    # Aggregation for total monthly trends (SQLite: strftime for grouping)
    query = """
    SELECT strftime('%Y-%m', date) as month, SUM(amount) as total_amount
    FROM expenses
    WHERE user_id = ?
    GROUP BY month
    ORDER BY month ASC
    LIMIT 6
    """
    history_agg = conn.execute(query, (user_id,)).fetchall()
    history_data = [
        {"month": item['month'], "amount": item['total_amount']} 
        for item in history_agg
    ]
    
    # Predict overall
    next_month_total = simple_linear_regression(history_data)
    
    # Category predictions
    categories = [c['category'] for c in conn.execute("SELECT DISTINCT category FROM expenses WHERE user_id = ?", (user_id,)).fetchall()]
    category_forecasts = {}
    
    for cat in categories:
        cat_query = """
        SELECT SUM(amount) as total_amount
        FROM expenses
        WHERE user_id = ? AND category = ?
        GROUP BY strftime('%Y-%m', date)
        ORDER BY date ASC
        LIMIT 6
        """
        cat_history = conn.execute(cat_query, (user_id, cat)).fetchall()
        cat_data = [{"amount": item['total_amount']} for item in cat_history]
        
        if len(cat_data) >= 1:
            category_forecasts[cat] = simple_linear_regression(cat_data)
        else:
            category_forecasts[cat] = 0

    conn.close()
    return {
        "next_month_forecast": round(next_month_total, 2),
        "category_forecasts": {k: round(v, 2) for k, v in category_forecasts.items()},
        "historical_data": history_data
    }
