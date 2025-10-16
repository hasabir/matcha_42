from flask import Blueprint


notifications_bp = Blueprint('notifications', __name__)


from src.notifications import routes_notifications