
from flask import Blueprint, request, jsonify, current_app,  redirect
from itsdangerous import SignatureExpired
from psycopg2.errors import UniqueViolation
import datetime
import sys
import os
from src.auth import auth_bp
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))
import logging
from utils.security import SecurityUtils

from database.crud.user_crud import User
from flask_bcrypt import Bcrypt

logging.basicConfig(level=logging.DEBUG)
from utils.email_service import EmailService
logger = logging.getLogger(__name__)


@auth_bp.route("/forgot_password", methods=["POST"])
def forgot_password():
    """
    Step 1: User submits username.
    We look up the user, generate a reset token via EmailService,
    store it in DB, and send the reset email. We always return 200
    to avoid username enumeration.
    """
    try:
        payload = request.get_json(force=True) or {}
        username = (payload.get("username") or "").strip()
        if not username:
            return jsonify({"error": "username is required"}), 400

        connection_pool = current_app.config["CONNECTION_POOL"]
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500

        user_crud = User(connection_pool=connection_pool)
        user = user_crud.get_user_by_username(username)

        # Always return 200 to avoid enumerating users
        if not user:
            return jsonify({
                "status": "ok",
                "message": "If the account exists, an email was sent."
            }), 200

        # Generate token *using EmailService* - it now generates and returns the token
        mail_service = EmailService()
        token = mail_service.send_password_reset_email(user['email'], user['username'])

        # Store token so we can verify it later
        user_crud.update_user({'reset_password_token': token}, user['username'])

        # Return response with token for development/testing
        # In production, you might want to remove the token from the response
        return jsonify({
            "status": "ok",
            "message": "If the account exists, an email was sent.",
            "token": token  # For testing - allows frontend to create direct link
        }), 200

    except Exception as e:
        logger.exception("forgot_password failed")
        return jsonify({"error": str(e)}), 400


@auth_bp.route("/reset_password", methods=["POST"])
def reset_password():
    """
    Step 3: Frontend posts token + username + new_password.
    We verify the token against what's stored in DB for that user,
    then update the password.
    """
    try:
        body = request.get_json(force=True) or {}
        token = (body.get("token") or "").strip()
        new_password = (body.get("new_password") or "").strip()
        username = (body.get("username") or "").strip()

        if not token or not new_password or not username:
            return jsonify({"error": "Missing required fields: token, new_password, username"}), 400

        connection_pool = current_app.config["CONNECTION_POOL"]
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500

        user_crud = User(connection_pool)
        user = user_crud.get_user_by_username(username)

        # Do not leak which check failed
        if not user or user.get("reset_password_token") != token:
            return jsonify({"error": "Error resetting password"}), 401

        hashed = SecurityUtils.password_hash(new_password)
        user_crud.update_user(
            {
                'reset_password_token': None,
                'active': True,
                'password': hashed
            },
            user['username']
        )

        # Keep it simple: make the user sign in after reset
        return jsonify({"message": "password reset successfully"}), 200

    except Exception as e:
        logger.exception("reset_password failed")
        return jsonify({"error": str(e)}), 400


@auth_bp.route("/confirm_email_reset/<token>", methods=["GET"])
def confirm_email_reset(token):
    """
    Step 2: User clicks link in email. We decode the token to get the email,
    look up the user, and redirect to the frontend reset page with token + username.
    """
    try:
        connection_pool = current_app.config["CONNECTION_POOL"]
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500

        # Decode the token to get the email
        mail_service = EmailService()
        email = mail_service.confirm_reset_token(token)
        
        # Look up user by email
        user_crud = User(connection_pool)
        user = user_crud.get_user_by_email(email=email)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Verify the token matches what's stored
        if user.get("reset_password_token") != token:
            return jsonify({"error": "Token invalid or expired"}), 400

        # ✅ Redirect to frontend reset page with token AND username
        frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
        return redirect(f"{frontend_url}/reset-password?token={token}&username={user['username']}", code=302)

    except SignatureExpired:
        return jsonify({"error": "Token expired"}), 400
    except Exception as e:
        logger.exception("confirm_email_reset failed")
        return jsonify({"error": str(e)}), 400