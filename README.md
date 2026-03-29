# ExpenWise | AI-Powered Financial Assistant (Python Edition)

A professional, production-ready intelligent expense forecasting system built with **Python (Flask)**, **MongoDB**, and **Standard Web Stack (HTML/CSS/JS)**. This project follows a modular, clean architecture inspired by transit intelligence systems.

---

## 🚀 Key Features

*   **Intelligent Forecasting Module**: A custom Linear Regression engine in Python (`ml/forecasting.py`) that analyzes last 6 months of habit to predict next month.
*   **Financial Health AI**: Proprietary scoring algorithm (`services/analytics_service.py`) that evaluates user performance.
*   **Smart Insight Engine**: Automated spending pattern detection and threshold alerts.
*   **Modern Premium UI**: Built with Bootstrap 5, Chart.js, and Lucide icons for a sleek, dark-mode-ready aesthetic.
*   **REST API Architecture**: Clean separation between AI services, data models, and presentation layer.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, Flask, PyMongo, Flask-JWT-Extended, Bcrypt.
- **AI/ML**: NumPy for linear regression modeling.
- **Frontend**: HTML5, CSS3, ES6 JavaScript, Chart.js, Bootstrap 5.
- **Database**: MongoDB (Local or Atlas).

---

## ⚙️ Setup & Execution

### 1. Prerequisites
- Python 3.10+
- MongoDB Running locally (default port 27017)

### 2. Environment Setup
1. Open a terminal in the project root.
2. Install dependencies: `pip install -r requirements.txt`
3. (Optional) Run the seed script to create a test account and 6 months of data:
   ```bash
   python seed.py
   ```

### 3. Start the Server
1. Run the Flask application:
   ```bash
   python app.py
   ```
2. Open your browser and navigate to `http://localhost:5000`.

---

## 🔐 Credentials (After Seeding)
- **Account**: `john@example.com`
- **Password**: `password123`

---

## 📂 Architecture Overview

```text
/project
├── app.py             # Entry point & Config
├── requirements.txt   # Python dependencies
├── seed.py            # Data generation tool
├── /models            # Database schema & indexing
├── /routes            # API Endpoints (Auth, Analytics, Expenses)
├── /services          # Business Logic & Math services
├── /ml                # Linear Regression forecasting engine
├── /static            # CSS theme & Vanilla JS logic
└── /templates         # HTML view templates
```
