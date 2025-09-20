from flask import Blueprint

profile_bp = Blueprint('search', __name__)

from src.search import routes_filter, routes_search, routes_sort