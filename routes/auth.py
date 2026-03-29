import bcrypt
import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from models.db import get_db_connection

auth_bp = Blueprint('auth', __name__)

def generate_token(user_id):
    expires = datetime.timedelta(days=30)
    return create_access_token(identity=str(user_id), expires_delta=expires)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    email = data.get('email', '').lower()
    password = data.get('password')

    if not all([name, email, password]):
        return jsonify({"error": "Missing fields"}), 400

    conn = get_db_connection()
    try:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, hashed_password))
        user_id = cursor.lastrowid
        conn.commit()
        token = generate_token(user_id)
        return jsonify({
            "_id": str(user_id),
            "name": name,
            "email": email,
            "token": token
        }), 201
    except Exception as e:
        return jsonify({"error": "User already exists or database error"}), 400
    finally:
        conn.close()

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email', '').lower()
    password = data.get('password')

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email = (?)", (email,)).fetchone()
    conn.close()

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        token = generate_token(user['id'])
        return jsonify({
            "_id": str(user['id']),
            "name": user['name'],
            "email": user['email'],
            "token": token
        }), 200
    
    return jsonify({"error": "Invalid email or password"}), 401

@auth_bp.route('/firebase-login', methods=['POST'])
def firebase_login():
    data = request.json
    email = data.get('email', '').lower()
    name = data.get('name', 'Firebase User')
    uid = data.get('uid')

    if not email or not uid:
        return jsonify({"error": "Missing Firebase identifiers"}), 400

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email = (?)", (email,)).fetchone()
    
    # If user doesn't exist, register them via Firebase sync
    if not user:
        cursor = conn.cursor()
        # Create dummy password hash for firebase users
        dummy_hash = bcrypt.hashpw(uid.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, dummy_hash))
        user_id = cursor.lastrowid
        conn.commit()
    else:
        user_id = user['id']
        name = user['name']

    conn.close()
    
    # Issue backend token
    token = generate_token(user_id)
    return jsonify({
        "_id": str(user_id),
        "name": name,
        "email": email,
        "token": token
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    user_id = get_jwt_identity()
    conn = get_db_connection()
    user = conn.execute("SELECT name, email FROM users WHERE id = (?)", (user_id,)).fetchone()
    conn.close()
    if user:
        return jsonify(dict(user)), 200
    return jsonify({"error": "User not found"}), 404
