from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

from src.auth import routes_auth, routes_password  # This imports the routes after blueprint creation