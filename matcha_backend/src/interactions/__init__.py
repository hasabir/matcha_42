from flask import Blueprint


interactions_bp = Blueprint('interactions', __name__)


from src.interactions import routes_like, routes_hate, routes_matching