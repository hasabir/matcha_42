from flask import Blueprint, request, jsonify, current_app
from psycopg2.errors import UniqueViolation
import sys
import os
from src.auth import auth_bp
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))
import logging

from  database.crud.user_crud import User
from flask_bcrypt import Bcrypt

# bcrypt = Bcrypt(auth_bp)


@auth_bp.route('/login', methods=['POST'])
def login():
    ...




@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        user_data = request.json
        connection_pool = current_app.config["CONNECTION_POOL"]
        
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500
        
        user_crud = User(connection_pool)
        result = user_crud.create_user(user_data)
        return jsonify({"status": "ok", "data": result}), 200
    except UniqueViolation as e:
        logging.error(f"Unique constraint violation: {e}")
        return jsonify({"error": "username or email already exists"}), 409
    except Exception as e:
        logging.error(f"Error during registration: {e}")
        return jsonify({"error": str(e), "message": "Registration failed"}), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    ...


@auth_bp.route('/users', methods=['GET'])
def get_all_users():
    logging.info("*********************Fetching all users**********")
    connection_pool = current_app.config["CONNECTION_POOL"]
    if not connection_pool:
        return jsonify({"error": "Database connection pool is not available"}), 500
    user_crud = User(connection_pool)
    result = user_crud.get_all_users()
    return jsonify({"status": "ok", "data": result}), 200
