import os
from flask import Flask, render_template, send_from_directory, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import yfinance as yf

# Load env vars
load_dotenv()

app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-123')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-456')

CORS(app)
jwt = JWTManager(app)

# Import and Register Blueprints
from routes.auth import auth_bp
from routes.expenses import expense_bp
from routes.income import income_bp
from routes.dashboard import dashboard_bp
from routes.budgets import budget_bp
from routes.goals import goal_bp
from routes.reports import report_bp
from routes.sync import sync_bp
from routes.investments import investments_bp
from routes.reviews import review_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(expense_bp, url_prefix='/api/expenses')
app.register_blueprint(income_bp, url_prefix='/api/income')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
app.register_blueprint(budget_bp, url_prefix='/api/budgets')
app.register_blueprint(goal_bp, url_prefix='/api/goals')
app.register_blueprint(report_bp, url_prefix='/api/reports')
app.register_blueprint(sync_bp, url_prefix='/api/sync')
app.register_blueprint(investments_bp, url_prefix='/api/investments')
app.register_blueprint(review_bp, url_prefix='/api/reviews')

# Frontend Routes (serving HTML templates)
@app.route('/')
def dashboard_page():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/expenses')
def expenses_page():
    return render_template('expenses.html')

@app.route('/income')
def income_page():
    return render_template('income.html')

@app.route('/budgets')
def budgets_page():
    return render_template('budgets.html')

@app.route('/goals')
def goals_page():
    return render_template('goals.html')

@app.route('/reports')
def reports_page():
    return render_template('reports.html')

@app.route('/reviews')
def reviews_page():
    return render_template('reviews.html')

# Investment Routes
@app.route('/investments/stocks')
def stocks_page():
    return render_template('stocks.html')

@app.route('/investments/crypto')
def crypto_page():
    return render_template('crypto.html')

@app.route('/investments/real-estate')
def real_estate_page():
    return render_template('real_estate.html')

@app.route('/investments/fixed-deposits')
def fixed_deposits_page():
    return render_template('fixed_deposits.html')

# Stock Proxy (FREE & RELIABLE)
@app.route('/api/proxy/stock/<symbol>')
def stock_proxy(symbol):
    try:
        # Check if user added .NS for Indian stocks manually or handle it
        ticker_sym = symbol.upper()
        if not ticker_sym.endswith('.NS') and len(ticker_sym) > 5:
             # Heuristic for Indian stocks if user types just 'RELIANCE'
             ticker_sym += '.NS'
             
        ticker = yf.Ticker(ticker_sym)
        data = ticker.fast_info
        price = data.last_price
        
        # Fallback if first symbol fails (especially for Indian names)
        if not price or price == 0:
            if not ticker_sym.endswith('.NS'):
                 ticker = yf.Ticker(ticker_sym + '.NS')
                 price = ticker.fast_info.last_price

        return jsonify({
            "symbol": ticker_sym,
            "price": price,
            "currency": data.currency
        }), 200
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route('/health')
def health():
    return jsonify({"status": "OK", "message": "Smart Financial AI API is running"}), 200

# Error Handlers for Production (Ensure JSON for API routes)
@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api'):
        return jsonify(error="Resource not found", message=str(e)), 404
    return render_template('layout.html'), 404 # Fallback or home

@app.errorhandler(500)
def server_error(e):
    if request.path.startswith('/api'):
        return jsonify(error="Internal server error", message="Something went wrong on our end."), 500
    return render_template('layout.html'), 500

# For local development
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
