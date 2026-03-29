import sqlite3
import datetime
import bcrypt
import os
from models.db import get_db_connection, setup_db

def seed_data():
    setup_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("Clearing database...")
    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM expenses")
    cursor.execute("DELETE FROM income")
    cursor.execute("DELETE FROM budgets")
    cursor.execute("DELETE FROM goals")

    print("Creating sample user...")
    hashed_password = bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt())
    cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", 
                   ("John Doe", "john@example.com", hashed_password))
    user_id = cursor.lastrowid

    print("Seeding income (last 6 months)...")
    for i in range(6):
        date = (datetime.datetime.now() - datetime.timedelta(days=i*30)).strftime('%Y-%m-%d')
        cursor.execute("INSERT INTO income (user_id, amount, source, date) VALUES (?, ?, ?, ?)",
                       (user_id, 5000 + (100 * (5-i)), "Monthly Salary", date))

    print("Seeding expenses (last 6 months with trend)...")
    categories = ['Food', 'Rent', 'Transport', 'Utilities', 'Shopping']
    for i in range(6):
        month_offset = (5 - i)
        base_amount = 2500 + (month_offset * 150)
        date = (datetime.datetime.now() - datetime.timedelta(days=i*30)).strftime('%Y-%m-%d')
        
        for cat in categories:
            cursor.execute("INSERT INTO expenses (user_id, amount, category, date, notes) VALUES (?, ?, ?, ?, ?)",
                           (user_id, (base_amount / len(categories)) + (month_offset * 20), cat, date, f"Sample {cat} expense"))

    print("Adding current month budget...")
    now = datetime.datetime.now()
    month_str = f"{now.year}-{now.month:02d}"
    cursor.execute("INSERT INTO budgets (user_id, month, total_budget, category_budgets) VALUES (?, ?, ?, ?)",
                   (user_id, month_str, 3500, '{"Food": 600, "Rent": 1200, "Transport": 400}'))

    print("Adding a savings goal...")
    deadline = (datetime.datetime.now() + datetime.timedelta(days=120)).strftime('%Y-%m-%d')
    cursor.execute("INSERT INTO goals (user_id, name, target_amount, current_amount, deadline, category) VALUES (?, ?, ?, ?, ?, ?)",
                   (user_id, "New Gaming PC", 2000, 850, deadline, "Short-term"))

    conn.commit()
    conn.close()
    print("✅ Database Seeded Successfully!")
    print(f"Login: john@example.com / password123")

if __name__ == '__main__':
    seed_data()
