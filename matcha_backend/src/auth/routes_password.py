from flask import Blueprint, request, jsonify, current_app
from itsdangerous import SignatureExpired
from psycopg2.errors import UniqueViolation
import datetime
import sys
import os
from src.auth import auth_bp
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))
import logging
from utils.security import SecurityUtils

from  database.crud.user_crud import User
from flask_bcrypt import Bcrypt

logging.basicConfig(level=logging.DEBUG)
from utils.email_service import EmailService
logger = logging.getLogger(__name__)





@auth_bp.route("/forgot_password", methods=['POST'])
def forgot_password():
    try:
        username = request.json
        connection_pool = current_app.config["CONNECTION_POOL"]
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500
        
        user_crud = User(connection_pool=connection_pool)
        user_data = user_crud.get_user_by_username(username["username"])
        
        if not user_data:
            return jsonify({"error": "User not singed up"}), 401
        
        mail_service = EmailService()
        token = mail_service.send_verification_email(user_data['email'], "reset_password")
        user_crud.update_user({'reset_password_token': token}, user_data['username'])
        return jsonify({"status": "ok", "message": "check you're email to verify your account"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400



@auth_bp.route("/reset_password", methods=["POST"])
def reset_password():
    try:
        request_data = request.json
        if not all([request_data["token"], request_data["new_password"], request_data["username"]]):
            return jsonify({"error": "Missing required fields: <token>, <new_password>, <username>"}), 400
        connection_pool = current_app.config["CONNECTION_POOL"]
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500
        
        user_crud = User(connection_pool)
        
        user_data = user_crud.get_user_by_username(request_data["username"])
        if request_data["token"] != user_data["reset_password_token"]:
            return jsonify({"error": "Error Resetting password"}), 401
        new_hashed_passwrod = SecurityUtils.password_hash(request_data['new_password'])
        user_crud.update_user({'reset_password_token': None,
                                'active': True,
                                'password': new_hashed_passwrod}
                                ,user_data['username'])
        access_token = SecurityUtils.generate_access_token(user_data['id'])
        refresh_token = SecurityUtils.generate_refresh_token(user_data['id'])
        
        response = jsonify({
            "message": "password reset successfully",
            "access_token": access_token,
            "user_id": user_data['id'],
            "username": user_data['username']
        })
        response.set_cookie(
            'refresh_token',
            refresh_token,
            httponly=True,
            samesite='Strict'
        )
        return response, 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400





@auth_bp.route("/confirm_email_reset/<token>")
def confirm_email_reset(token):
    try:
        connection_pool = current_app.config["CONNECTION_POOL"]
        user_crud = User(connection_pool)
    
        user_data = user_crud.get_user_by("reset_password_token", token)
        if not user_data:
            return jsonify({"error": "Token invalide or expired"}), 400
        logger.error(f"❌ Failed to retreave username -> {user_data["username"]}")

        mail_service = EmailService()

        mail_service = mail_service.confirm_email(token)
        return jsonify({"status": "ok",
                        "message": "ready to reset password",
                        "token": token}), 200
        #TODO or directly redirect to change password page <to confirm after merge>
    except SignatureExpired:
        return jsonify({"error": "Token expired"}), 400
    except Exception as e:
        return jsonify({"error": e}), 400