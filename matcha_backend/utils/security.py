# utils/security.py
import logging
from flask import current_app, request, jsonify, g
import jwt
from functools import wraps
import datetime


class SecurityUtils:
    
    @staticmethod
    def password_hash(password):
        """Hash a password using bcrypt."""
        bcrypt = current_app.config.get('BCRYPT')
        if not bcrypt:
            raise RuntimeError("BCRYPT not configured in app context")
        return bcrypt.generate_password_hash(password).decode('utf-8')
    
    @staticmethod
    def password_check(hashed_password, password):#! or should i fetch user form db?
        """Check a password against a hashed password."""
        bcrypt = current_app.config.get('BCRYPT')
        if not bcrypt:
            raise RuntimeError("BCRYPT not configured in app context")
        return bcrypt.check_password_hash(hashed_password, password)
    
    
    
    def generate_refresh_token(user_id):
        #! HTTP-only Cookie (withcredentials = true) for refresh token
        token = jwt.encode(
            {
                'user_id': user_id,
                'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7),
                'type': 'refresh',           },
            current_app.config['JWT_REFRESH_TOKEN'],
            algorithm='HS256'
        )
        return token
    
    def generate_access_token(user_id):
        #! Authorization Header
        token = jwt.encode(
            {
                'user_id': user_id,
                'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1),
                'type': 'access',},
            current_app.config['JWT_ACCESS_TOKEN'],
            algorithm='HS256'
        )
        return token
    
    @staticmethod
    def verify_jwt_token(token):
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(
                token, 
                current_app.config['JWT_ACCESS_TOKEN'],
                algorithms=['HS256']
            )
            return payload
        except jwt.ExpiredSignatureError:
            return {"error": "Token has expired"}
        except jwt.InvalidTokenError:
            return {"error": "Invalid token format or signature"} 

logger = logging.getLogger(__name__)

def auth_guard(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token is missing or invalid format'}), 401

        token = auth_header.split(' ')[1]

        # Verify token
        payload = SecurityUtils.verify_jwt_token(token)

        if 'error' in payload:
            return jsonify({'error': payload['error']}), 403

        # Attach user_id to request context
        g.user_id = payload['user_id']
        return f(*args, **kwargs)

    return decorated

# def auth_guard(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         auth_header = request.headers.get('Authorization')
#         if not auth_header or not auth_header.startswith('Bearer '):
#             return jsonify({'error': 'Token is missing or invalid format'}), 401
        
#         token = auth_header.split(' ')[1]  #! Extract token from "Bearer <token>" in react header
        
#         # Verify token
#         payload = SecurityUtils.verify_jwt_token(token)
#         if not payload:
#             return jsonify({'error': 'Invalid or expired token'}), 403
        
#         # Add user_id to request context for use in the route
#         if 'error' in payload:
#             return jsonify({'error': payload['error']}), 403
#         g.user_id = payload['user_id']

#         return f(*args, **kwargs)
    
#     return decorated

    # @staticmethod
    # def generate_jwt_token(user_id, expires_hours=24):
    #     """Generate a JWT token for the user."""
    #     token = jwt.encode(
    #         {
    #             'user_id': user_id,
    #             'exp': datetime.utcnow() + timedelta(hours=expires_hours)
    #         },
    #         current_app.config['JWT_ACCESS_TOKEN'],
    #         algorithm='HS256'
    #     )
    #     return token