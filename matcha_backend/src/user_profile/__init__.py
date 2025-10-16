from flask import Blueprint


profile_bp = Blueprint('profile', __name__)


from src.user_profile import routes_profile, routes_images, routes_interests, routes_location
