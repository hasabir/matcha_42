from flask import Blueprint, request, jsonify, current_app
from psycopg2.errors import UniqueViolation

import sys
import os
from src.auth import auth_bp
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))
import logging
from utils.security import SecurityUtils

from  database.crud.user_crud import User
from flask_bcrypt import Bcrypt

logging.basicConfig(level=logging.DEBUG)

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        user_data = request.json
        response = jsonify({"status": "ok"})
        connection_pool = current_app.config["CONNECTION_POOL"]
        
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500
        
        user_crud = User(connection_pool)
        
        user = user_crud.get_user_by_username(user_data['username'])
        
        if not user or not SecurityUtils.password_check(user['password'], user_data['password']):
            return jsonify({"error": "Invalid username or password"}), 401
        
        # Generate tokens
        access_token = SecurityUtils.generate_access_token(user['id'])
        refresh_token = SecurityUtils.generate_refresh_token(user['id'])
        
        # Send access token in JSON, refresh token as secure cookie
        response = jsonify({'access_token': access_token})
        response.set_cookie(
            'refresh_token',
            refresh_token,
            httponly=True,
            # secure=True,  #TODO Uncomment if we are using HTTPS
            samesite='Strict'
        )
    except Exception as e:
        logging.error(f"Error during login: {e}")
        return jsonify({"error": str(e), "message": "Login failed"}), 400

    return response



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



@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    """Refresh access token using refresh token stored in HTTP-only cookie."""

    #! Get refresh token from COOKIE (automatically sent by browser)
    refresh_token = request.cookies.get('refresh_token')
    
    # Verify refresh token and issue new access token
    payload = SecurityUtils.verify_jwt_token(refresh_token, 'refresh')
    new_access_token = SecurityUtils.generate_access_token(payload['user_id'])
    
    return jsonify({'access_token': new_access_token})