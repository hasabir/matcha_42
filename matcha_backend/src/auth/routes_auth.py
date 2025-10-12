# # from flask import Blueprint, g, request, jsonify, current_app01
# from flask import Blueprint, g, request, jsonify, current_app, redirect
# from itsdangerous import SignatureExpired
# from psycopg2.errors import UniqueViolation
# import datetime
# import sys
# import os
# from src.auth import auth_bp
# sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))
# import logging
# from utils.security import SecurityUtils

# from  database.crud.user_crud import User
# from database.crud.profile_crud import Profile
# from flask_bcrypt import Bcrypt

# logging.basicConfig(level=logging.DEBUG)
# from utils.email_service import EmailService
# logger = logging.getLogger(__name__)


# @auth_bp.route("/register", methods=["POST"])
# def register():
#     try:
#         user_data = request.json
#         # print("\033[92mUser data:\033[0m", user_data)
#         logging.debug(f"@Registering user: {user_data['username']} with email: {user_data['email']}")
#         connection_pool = current_app.config["CONNECTION_POOL"]
        
#         if not connection_pool:
#             return jsonify({"error": "Database connection pool is not available"}), 500
        
#         user_crud = User(connection_pool)
#         # print("\033[93mExecuting query:\033[0m")
        
#         mail_service = EmailService()
#         user_crud.create_user(user_data)
#         token = mail_service.send_verification_email(user_data['email'], "email_verification")
#         user_crud.update_user({'verification_token': token}, user_data['username'])
#         return jsonify({"status": "ok", "message": "check you're email to verify your account", "token" : token}), 200
#     except UniqueViolation as e:
#         logging.error(f"Unique constraint violation: {e}")
#         return jsonify({"error": "username or email already exists"}), 409
#     except Exception as e:
#         logging.error(f"Error during registration: {e}")
#         return jsonify({"error": str(e), "message": "Registration failed"}), 409

# @auth_bp.route('/resend_verification', methods=["POST"])
# def resend_verification():
#     try:
#         user_data = request.json
#         connection_pool = current_app.config["CONNECTION_POOL"]
#         if not connection_pool:
#             return jsonify({"error": "Database connection pool is not available"}), 500
        
#         user_crud = User(connection_pool)
#         user = user_crud.get_user_by_username(username=user_data["username"])
#         if not user:
#             return jsonify({"error": "user is not signed up"}), 401
#         if user["verified"]:
#             return jsonify({"error": "You're already verified"}), 409

#         # Generate a new verification token and build a URL to your front-end
#         mail_service = EmailService()
#         token = SecurityUtils.generate_verification_token(user['id'])
#         verification_url = f"http://localhost:3000/verify/{token}"

#         # Send the verification link in the email (update EmailService accordingly)
#         mail_service.send_verification_email(user_data['email'], verification_url)
#         # Save the token in your DB
#         user_crud.update_user({'verification_token': token}, user_data['username'])

#         return jsonify({
#             "status": "ok",
#             "message": "Check your e‑mail to verify your account"
#         }), 200

#     except UniqueViolation as e:
#         logging.error(f"Unique constraint violation: {e}")
#         return jsonify({"error": "username or email already exists"}), 409
#     except Exception as e:
#         logging.error(f"Error during registration: {e}")
#         return jsonify({"error": str(e), "message": "Resend verification failed"}), 409


# # @auth_bp.route('/resend_verification', methods=["POST"])
# # def resend_verification():
# #     try:
# #         user_data = request.json
# #         connection_pool = current_app.config["CONNECTION_POOL"]
        
# #         if not connection_pool:
# #             return jsonify({"error": "Database connection pool is not available"}), 500
        
# #         user_crud = User(connection_pool)
        
# #         user = user_crud.get_user_by_username(username=user_data["username"])
# #         if not user:
# #             return jsonify({"error": "user is not signed up"}), 401
        
# #         if user["verified"]:
# #             return jsonify({"error":"You're already verified"}), 409
        
# #         mail_service = EmailService()
# #         token = mail_service.send_verification_email(user_data['email'], "email_verification")
# #         user_crud.update_user({'verification_token': token}, user_data['username'])
# #         return jsonify({"status": "ok", "message": "check you're email to verify your account", "token" : token}), 200
# #     except UniqueViolation as e:
# #         logging.error(f"Unique constraint violation: {e}")
# #         return jsonify({"error": "username or email already exists"}), 409
# #     except Exception as e:
# #         logging.error(f"Error during registration: {e}")
# #         return jsonify({"error": str(e), "message": "Registration failed"}), 409



# # @auth_bp.route('/confirm_email/<token>')
# # def confirm_email(token):
# #     try:
# #         connection_pool = current_app.config["CONNECTION_POOL"]
# #         user_crud = User(connection_pool)
    
# #         user_data = user_crud.get_user_by_token(token)
# #         if not user_data:
# #             return jsonify({"error": "Token invalide or expired"}), 400
# #         logger.error(f"❌ Failed to retreave username -> {user_data["username"]}")

# #         mail_service = EmailService()

# #         mail_service = mail_service.confirm_email(token)
# #         user_crud.update_user({'verification_token': None,
# #                                'verified': True,
# #                                'active': True}, user_data['username'])
# #         access_token = SecurityUtils.generate_access_token(user_data['id'])
# #         refresh_token = SecurityUtils.generate_refresh_token(user_data['id'])
        
# #         response = jsonify({
# #             "message": "Email verified successfully",
# #             "access_token": access_token,
# #             "user_id": user_data['id'],
# #             "username": user_data['username']
# #         })
# #         response.set_cookie(
# #             'refresh_token',
# #             refresh_token,
# #             httponly=True,
# #             samesite='Strict'
# #         )
# #         return response, 200
# #     except SignatureExpired:
# #         return jsonify({"error": "Token expired"}), 400
# #     except Exception as e:
# #         return jsonify({"error": e}), 400

# @auth_bp.route('/confirm_email/<token>')
# def confirm_email(token):
#     try:
#         connection_pool = current_app.config["CONNECTION_POOL"]
#         user_crud = User(connection_pool)

#         user_data = user_crud.get_user_by_token(token)
#         if not user_data:
#             return jsonify({"error": "Token invalid or expired"}), 400

#         # Mark user as verified/active and clear the token
#         user_crud.update_user({
#             'verification_token': None,
#             'verified': True,
#             'active': True
#         }, user_data['username'])

#         # Optionally generate tokens and set a cookie
#         refresh_token = SecurityUtils.generate_refresh_token(user_data['id'])
#         response = redirect('http://localhost:3000/signin')
#         response.set_cookie('refresh_token', refresh_token,
#                             httponly=True, samesite='Strict')
#         return response  # status code 302 by default

#     except SignatureExpired:
#         return jsonify({"error": "Token expired"}), 400
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400

# @auth_bp.route('/login', methods=['POST'])
# def login():
#     try:
#         user_data = request.json
#         response = jsonify({"status": "ok"})
#         connection_pool = current_app.config["CONNECTION_POOL"]
#         # print("\033[91mExecuting query:\033[0m", current_app.config["JWT_ACCESS_TOKEN_EXPIRES"])

#         if not connection_pool:
#             return jsonify({"error": "Database connection pool is not available"}), 500
        
#         user_crud = User(connection_pool)
        
#         user = user_crud.get_user_by_username(user_data['username'])
        
#         if not user or not SecurityUtils.password_check(user['password'], user_data['password']):
#             return jsonify({"error": "Invalid username or password"}), 401
        
        
#         # Generate tokens
#         access_token = SecurityUtils.generate_access_token(user['id'])
#         refresh_token = SecurityUtils.generate_refresh_token(user['id'])
        
#         # Send access token in JSON, refresh token as secure cookie
#         response = jsonify({'access_token': access_token})
#         response.set_cookie(
#             'refresh_token',
#             refresh_token,
#             httponly=True,
#             # secure=True,  #TODO Uncomment if we are using HTTPS
#             samesite='Strict'
#         )
#         user_crud.update_user(
#                         {"last_seen": datetime.datetime.utcnow(),
#                          "active": True},
#                         user_data["username"])
#     except Exception as e:
#         logging.error(f"Error during login: {e}")
#         return jsonify({"error": str(e), "message": "Login failed"}), 400

#     return response



# @auth_bp.route('/logout', methods=['POST'])
# def logout():
#     ...


# @auth_bp.route('/users', methods=['GET'])
# def get_all_users():
#     logging.info("*********************Fetching all users**********")
#     connection_pool = current_app.config["CONNECTION_POOL"]
#     if not connection_pool:
#         return jsonify({"error": "Database connection pool is not available"}), 500
#     user_crud = User(connection_pool)
#     result = user_crud.get_all_users()
#     return jsonify({"status": "ok", "data": result}), 200


# # in your auth routes file
# @auth_bp.route('/refresh', methods=['POST'])
# def refresh():
#     try:
#         refresh_token = request.cookies.get('refresh_token')
#         if not refresh_token:
#             return jsonify({'error': 'Missing refresh token'}), 401

#         payload = SecurityUtils.verify_refresh_token(refresh_token)
#         if not payload or 'error' in payload:
#             return jsonify({'error': payload.get('error', 'Invalid or expired token')}), 403

#         new_access_token = SecurityUtils.generate_access_token(payload['user_id'])
#         return jsonify({'access_token': new_access_token}), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# # @auth_bp.route('/refresh')
# # def refresh():
# #     """Refresh access token using refresh token stored in HTTP-only cookie."""
# #     try:
# #         #! Get refresh token from COOKIE (automatically sent by browser)
# #         refresh_token = request.cookies.get('refresh_token')
        
# #         # Verify refresh token and issue new access token
# #         logger.info(f"👉 refresh token -> {refresh_token}")
# #         payload = SecurityUtils.verify_jwt_token(refresh_token)
        
# #         if not payload or 'error' in payload:
# #             return jsonify({'error': 'Invalid or expired token'}), 403
# #         logger.info(f"⚡ {payload} ->")
# #         new_access_token = SecurityUtils.generate_access_token(g.user_id)
# #         if 'error' in payload:
# #             return jsonify({'error': payload['error']}), 403
# #         return jsonify({'access_token': new_access_token})
# #     except Exception as e:
# #         return jsonify({"error": e}), 403




# routes_auth.py
from flask import Blueprint, g, request, jsonify, current_app, redirect
from itsdangerous import SignatureExpired
from psycopg2 import IntegrityError
from psycopg2.errors import UniqueViolation
import datetime
import sys
import os
import logging

from src.auth import auth_bp
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))

from utils.security import SecurityUtils
from database.crud.user_crud import User
from utils.email_service import EmailService

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@auth_bp.route("/register", methods=["POST"])
def register():
  """
  Create user if username/email not already used.
  - Returns 409 if username or email exists (no email sent, no redirect).
  - On success: creates user, sends verification email, stores token, returns 200.
  """
  try:
    user_data = request.get_json(force=True) or {}
    required = ("email", "username", "first_name", "last_name", "password")
    missing = [k for k in required if not str(user_data.get(k, "")).strip()]
    if missing:
      return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    email = user_data["email"].strip()
    username = user_data["username"].strip()

    logging.debug(f"@Registering user: {username} with email: {email}")

    connection_pool = current_app.config.get("CONNECTION_POOL")
    if not connection_pool:
      return jsonify({"error": "Database connection pool is not available"}), 500

    user_crud = User(connection_pool)

    # --- Early existence checks (avoid sending email/update on duplicates)
    existing_by_username = user_crud.get_user_by_username(username=username)
    if existing_by_username:
      return jsonify({"error": "username already exists"}), 409

    # Implement get_user_by_email in your User CRUD if missing
    if hasattr(user_crud, "get_user_by_email"):
      existing_by_email = user_crud.get_user_by_email(email=email)
      if existing_by_email:
        return jsonify({"error": "email already exists"}), 409

    # ❌ Removed password hashing here
    # Password will be hashed inside User.create_user()

    # --- Create user (this must RAISE on unique violations)
    user_crud.create_user(user_data)

    # --- Only after successful insert: send verification email and save token
    mail_service = EmailService()
    token = mail_service.send_verification_email(email, "email_verification")

    user_crud.update_user({'verification_token': token}, username)

    return jsonify({
      "status": "ok",
      "message": "check your email to verify your account"
    }), 200

  except (UniqueViolation, IntegrityError) as e:
    # In case of a race, DB unique constraint still wins
    logger.error(f"Unique constraint violation: {e}")
    return jsonify({"error": "username or email already exists"}), 409
  except Exception as e:
    logger.exception("Error during registration")
    return jsonify({"error": str(e), "message": "Registration failed"}), 409


@auth_bp.route('/resend_verification', methods=["POST"])
def resend_verification():
  try:
    user_data = request.get_json(force=True) or {}
    username = (user_data.get("username") or "").strip()
    email = (user_data.get("email") or "").strip()

    connection_pool = current_app.config.get("CONNECTION_POOL")
    if not connection_pool:
      return jsonify({"error": "Database connection pool is not available"}), 500

    user_crud = User(connection_pool)
    user = user_crud.get_user_by_username(username=username)
    if not user:
      return jsonify({"error": "user is not signed up"}), 401
    if user.get("verified"):
      return jsonify({"error": "You're already verified"}), 409

    mail_service = EmailService()
    token = SecurityUtils.generate_verification_token(user['id'])
    verification_url = f"http://localhost:3000/verify/{token}"

    mail_service.send_verification_email(email or user['email'], verification_url)
    user_crud.update_user({'verification_token': token}, username)

    return jsonify({"status": "ok", "message": "Check your e-mail to verify your account"}), 200

  except (UniqueViolation, IntegrityError) as e:
    logger.error(f"Unique constraint violation: {e}")
    return jsonify({"error": "username or email already exists"}), 409
  except Exception as e:
    logger.exception("Error during resend_verification")
    return jsonify({"error": str(e), "message": "Resend verification failed"}), 409


@auth_bp.route('/confirm_email/<token>', methods=['GET'])
def confirm_email(token):
  try:
    connection_pool = current_app.config.get("CONNECTION_POOL")
    if not connection_pool:
      return jsonify({"error": "Database connection pool is not available"}), 500

    # First, validate and decode the token to get the email
    mail_service = EmailService()
    try:
      email = mail_service.confirm_email(token)  # This decodes the token and returns email
    except SignatureExpired:
      return jsonify({"error": "Verification link has expired. Please request a new one."}), 400
    except Exception as e:
      logger.error(f"Token validation failed: {e}")
      return jsonify({"error": "Invalid verification token"}), 400

    # Now find the user by email
    user_crud = User(connection_pool)
    if hasattr(user_crud, "get_user_by_email"):
      user_data = user_crud.get_user_by_email(email=email)
    else:
      # Fallback: get user by verification_token if get_user_by_email doesn't exist
      user_data = user_crud.get_user_by_token(token)
    
    if not user_data:
      return jsonify({"error": "User not found"}), 404

    # Check if already verified
    if user_data.get('verified'):
      return jsonify({"message": "Email already verified", "already_verified": True}), 200

    # Mark user as verified and active
    user_crud.update_user({
      'verification_token': None,
      'verified': True,
      'active': True,
      'first_login': True  # This is still their first login, they just verified email
    }, user_data['username'])

    # Generate access token for auto-login
    access_token = SecurityUtils.generate_access_token(user_data['id'])
    refresh_token = SecurityUtils.generate_refresh_token(user_data['id'])
    
    # Return JSON response for frontend
    response = jsonify({
      "message": "Email verified successfully!",
      "access_token": access_token,
      "user": {
        "username": user_data['username'],
        "email": user_data['email'],
        "verified": True
      }
    })
    response.set_cookie('refresh_token', refresh_token, httponly=True, samesite='Strict', secure=False)
    return response, 200

  except SignatureExpired:
    return jsonify({"error": "Verification link has expired"}), 400
  except Exception as e:
    logger.exception("confirm_email failed")
    return jsonify({"error": str(e)}), 400


@auth_bp.route('/login', methods=['POST'])
def login():
  try:
    user_data = request.get_json(force=True) or {}
    connection_pool = current_app.config.get("CONNECTION_POOL")
    if not connection_pool:
      return jsonify({"error": "Database connection pool is not available"}), 500

    user_crud = User(connection_pool)
    user = user_crud.get_user_by_username(user_data.get('username'))

    if not user or not SecurityUtils.password_check(user['password'], user_data.get('password', '')):
      return jsonify({"error": "Invalid username or password"}), 401

    # Check if user is verified
    if not user.get('verified', False):
      return jsonify({"error": "Please verify your email before logging in"}), 401

    access_token = SecurityUtils.generate_access_token(user['id'])
    refresh_token = SecurityUtils.generate_refresh_token(user['id'])

    # Import Profile here to avoid circular imports
    from database.crud.profile_crud import Profile
    profile_crud = Profile(connection_pool)
    
    # Get profile completion status for redirect logic
    profile_status = profile_crud.get_profile_completion_status(user['id'])
    is_first_login = user.get('first_login', True)
    
    # Determine redirect destination
    if is_first_login or not profile_status['is_completed']:
      redirect_to = 'setupProfile'
    else:
      redirect_to = 'home'
    
    # Update user status and mark as no longer first login
    update_data = {
      "last_seen": datetime.datetime.utcnow(), 
      "active": True
    }
    
    # Only update first_login if it's currently True
    if is_first_login:
      update_data["first_login"] = False
    
    user_crud.update_user(update_data, user_data["username"])

    response = jsonify({
      'access_token': access_token,
      'redirect_to': redirect_to,
      'first_login': is_first_login,
      'profile_completed': profile_status['is_completed']
    })
    response.set_cookie('refresh_token', refresh_token, httponly=True, samesite='Strict')
    
    return response
  except Exception as e:
    logger.exception("Error during login")
    return jsonify({"error": str(e), "message": "Login failed"}), 400


@auth_bp.route('/refresh', methods=['POST'])
def refresh():
  try:
    refresh_token = request.cookies.get('refresh_token')
    if not refresh_token:
      return jsonify({'error': 'Missing refresh token'}), 401

    payload = SecurityUtils.verify_refresh_token(refresh_token)
    if not payload or 'error' in payload:
      return jsonify({'error': payload.get('error', 'Invalid or expired token')}), 403

    new_access_token = SecurityUtils.generate_access_token(payload['user_id'])
    return jsonify({'access_token': new_access_token}), 200
  except Exception as e:
    logger.exception("refresh failed")
    return jsonify({'error': str(e)}), 500


@auth_bp.route('/profile-status', methods=['GET'])
def get_profile_status():
  """Get user's profile completion status and determine redirect logic"""
  try:
    # This endpoint requires authentication
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
      return jsonify({'error': 'Missing or invalid authorization header'}), 401
    
    token = auth_header.split(' ')[1]
    payload = SecurityUtils.verify_jwt_token(token)
    
    if not payload or 'error' in payload:
      return jsonify({'error': 'Invalid or expired token'}), 401
    
    user_id = payload['user_id']
    
    # Get database connections
    connection_pool = current_app.config.get("CONNECTION_POOL")
    if not connection_pool:
      return jsonify({"error": "Database connection pool is not available"}), 500
    
    user_crud = User(connection_pool)
    
    # Import Profile here to avoid circular imports
    from database.crud.profile_crud import Profile
    profile_crud = Profile(connection_pool)
    
    # Get user info
    user = user_crud.get_user_by("id", user_id)
    if not user:
      return jsonify({'error': 'User not found'}), 404
    
    # Get profile completion status
    profile_status = profile_crud.get_profile_completion_status(user_id)
    
    # Determine redirect logic
    is_first_login = user.get('first_login', True)
    profile_completed = profile_status['is_completed']
    profile_has_essentials = profile_status['has_essentials']
    
    # Determine where to redirect
    if is_first_login or not profile_completed:
      redirect_to = 'setupProfile'
      should_show_setup = True
    else:
      redirect_to = 'home'
      should_show_setup = False
    
    return jsonify({
      'first_login': is_first_login,
      'profile_completed': profile_completed,
      'profile_has_essentials': profile_has_essentials,
      'redirect_to': redirect_to,
      'should_show_setup': should_show_setup,
      'profile_details': profile_status
    }), 200
    
  except Exception as e:
    logger.exception("get_profile_status failed")
    return jsonify({'error': str(e)}), 500


@auth_bp.route('/logo-redirect', methods=['GET'])
def logo_redirect():
  """Handle logo click redirects based on authentication status"""
  try:
    # Check if user is authenticated
    auth_header = request.headers.get('Authorization')
    
    # If no auth header, redirect to landing
    if not auth_header or not auth_header.startswith('Bearer '):
      return jsonify({'redirect_to': 'landing'}), 200
    
    # Verify token
    token = auth_header.split(' ')[1]
    payload = SecurityUtils.verify_jwt_token(token)
    
    # If token is invalid/expired, redirect to landing
    if not payload or 'error' in payload:
      return jsonify({'redirect_to': 'landing'}), 200
    
    # If user is authenticated, redirect to home
    return jsonify({'redirect_to': 'home'}), 200
    
  except Exception as e:
    logger.exception("logo_redirect failed")
    # On error, default to landing page
    return jsonify({'redirect_to': 'landing'}), 200
