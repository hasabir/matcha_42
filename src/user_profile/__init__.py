from flask import Blueprint

profile_bp = Blueprint('user_profile', __name__)

from src.user_profile import routes_profile, routes_interests, routes_images