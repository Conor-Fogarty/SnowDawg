from datetime import datetime
import re
from flask import Blueprint, request, jsonify
import sqlite3
import hashlib

user_bp = Blueprint("user_bp", __name__)

# Initialize SQLite DB and create user table if not exists
def init_user_db():
    with sqlite3.connect("users.db") as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT NOT NULL,
                favorite_mountains TEXT,
                location TEXT,
                pass_type TEXT
            )
        ''')
        conn.commit()

init_user_db()

# Utility to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@user_bp.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
        return jsonify({"error": "Invalid email format"}), 400
    favorite_mountains = ",".join(data.get("favorite_mountains", []))
    location = data.get("location")
    pass_type = data.get("pass_type")

    if not all([username, password, email]):
        return jsonify({"error": "Missing required fields"}), 400

    hashed_password = hash_password(password)

    try:
        with sqlite3.connect("users.db") as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO users (username, password, email, favorite_mountains, location, pass_type)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, hashed_password, email, favorite_mountains, location, pass_type))
            conn.commit()
        return jsonify({"message": "User registered successfully"})
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exists"}), 409

@user_bp.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not all([username, password]):
        return jsonify({"error": "Missing username or password"}), 400

    try:
        with sqlite3.connect("users.db") as conn:
            c = conn.cursor()
            c.execute("SELECT password FROM users WHERE username = ?", (username,))
            row = c.fetchone()

            if not row:
                # Avoid revealing if the user exists; generic error
                return jsonify({"error": "Invalid username or password"}), 401
            
            stored_password = row[0]
            hashed_password = hash_password(password)

            if hashed_password == stored_password:
                return jsonify({"message": "Login successful"})
            else:
                return jsonify({"error": "Invalid username or password"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@user_bp.route("/api/user/<username>", methods=["GET"])
def get_user(username):
    try:
        with sqlite3.connect("users.db") as conn:
            c = conn.cursor()
            c.execute("SELECT username, email, favorite_mountains, location, pass_type FROM users WHERE username = ?", (username,))
            row = c.fetchone()

            if row:
                user_data = {
                    "username": row[0],
                    "email": row[1],
                    "favorite_mountains": row[2].split(",") if row[2] else [],
                    "location": row[3],
                    "pass_type": row[4]
                }
                return jsonify(user_data)
            else:
                return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route("/api/user/<username>", methods=["PUT"])
def update_user(username):
    data = request.get_json()
    fields = ["email", "favorite_mountains", "location", "pass_type"]
    updates = {field: data.get(field) for field in fields if data.get(field) is not None}

    if "favorite_mountains" in updates:
        updates["favorite_mountains"] = ",".join(updates["favorite_mountains"])

    if not updates:
        return jsonify({"error": "No valid fields provided for update"}), 400

    set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values())
    values.append(username)

    try:
        with sqlite3.connect("users.db") as conn:
            c = conn.cursor()
            c.execute(f"UPDATE users SET {set_clause} WHERE username = ?", values)
            conn.commit()
            if c.rowcount == 0:
                return jsonify({"error": "User not found"}), 404
        return jsonify({"message": "User updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route("/api/user/<username>", methods=["DELETE"])
def delete_user(username):
    try:
        with sqlite3.connect("users.db") as conn:
            c = conn.cursor()
            c.execute("DELETE FROM users WHERE username = ?", (username,))
            conn.commit()
            if c.rowcount == 0:
                return jsonify({"error": "User not found"}), 404
        return jsonify({"message": "User deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
