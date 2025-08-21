from flask import Blueprint, request, jsonify, current_app
from itsdangerous import SignatureExpired
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
from .email_service import EmailService


@auth_bp.route("/register", methods=["POST"])
def register():
    # try:
    user_data = request.json
    # print("\033[92mUser data:\033[0m", user_data)
    logging.debug(f"@Registering user: {user_data['username']} with email: {user_data['email']}")
    connection_pool = current_app.config["CONNECTION_POOL"]
    
    if not connection_pool:
        return jsonify({"error": "Database connection pool is not available"}), 500
    
    user_crud = User(connection_pool)
    # print("\033[93mExecuting query:\033[0m")
    
    result = user_crud.create_user(user_data)
    mail_service = EmailService()
    token = mail_service.send_verification_email(user_data['email'])
    user_crud.update_user({'verification_token': token}, user_data['username'])
    return jsonify({"status": "ok", "data": result, "message": "check you're email to verify your account", "token" : token}), 200
    # except UniqueViolation as e:
    #     logging.error(f"Unique constraint violation: {e}")
    #     return jsonify({"error": "username or email already exists"}), 409
    # except Exception as e:
    #     logging.error(f"Error during registration: {e}")
    #     return jsonify({"error": str(e), "message": "Registration failed"}), 500


@auth_bp.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        mail_service = EmailService()
        email = mail_service.confirm_token(token)
        # Update user as verified in database
        return jsonify({"message": "Email verified successfully"}), 200
    except SignatureExpired:
        return jsonify({"error": "Token expired"}), 400
    except Exception as e:
        return jsonify({"error": "Invalid token"}), 400



# @auth_bp.route('/confirm/<token>', methods=['GET'])
# def confirm_email(token):
#     try:
#         email = EmailService(current_app).confirm_email(token)
#         if isinstance(email, tuple):  # If it returns a tuple, it's an error response
#             return email
        
#         connection_pool = current_app.config["CONNECTION_POOL"]
#         if not connection_pool:
#             return jsonify({"error": "Database connection pool is not available"}), 500
        
#         user_crud = User(connection_pool)
#         user_crud.verify_user(email)
        
#         return jsonify({"status": "ok", "message": "Email verified successfully"}), 200
#     except Exception as e:
#         logging.error(f"Error confirming email: {e}")
#         return jsonify({"error": str(e), "message": "Email confirmation failed"}), 400






@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        user_data = request.json
        response = jsonify({"status": "ok"})
        connection_pool = current_app.config["CONNECTION_POOL"]
        # print("\033[91mExecuting query:\033[0m", current_app.config["JWT_ACCESS_TOKEN_EXPIRES"])

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



@auth_bp.route("/drop")
def drop_tables():
    """Drop all tables in the database."""
    connection_pool = current_app.config["CONNECTION_POOL"]
    if not connection_pool:
        return jsonify({"error": "Database connection pool is not available"}), 500
    
    user_crud = User(connection_pool)
    user_crud.delet_all_users()
    
    return jsonify({"status": "ok", "message": "All tables dropped successfully"}), 200