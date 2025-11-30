from flask import Blueprint


search_bp = Blueprint('search', __name__)


from src.search import routes_sort, routes_search
