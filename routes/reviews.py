from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.db import get_db_connection

review_bp = Blueprint('reviews', __name__)

@review_bp.route('/', methods=['POST'])
@jwt_required()
def add_review():
    user_id = get_jwt_identity()
    data = request.json
    
    rating = data['rating']
    comment = data.get('comment', '')
    category = data.get('category', 'General')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO reviews (user_id, rating, comment, category) VALUES (?, ?, ?, ?)",
                   (user_id, rating, comment, category))
    conn.commit()
    review_id = cursor.lastrowid
    conn.close()

    return jsonify({"id": review_id, "status": "success"}), 201

@review_bp.route('/', methods=['GET'])
def get_reviews():
    conn = get_db_connection()
    # Fetch top reviews joined with user names
    reviews = conn.execute("""
        SELECT r.*, u.name 
        FROM reviews r 
        JOIN users u ON r.user_id = u.id 
        ORDER BY r.created_at DESC 
        LIMIT 10
    """).fetchall()
    conn.close()
    return jsonify({"reviews": [dict(r) for r in reviews]}), 200
