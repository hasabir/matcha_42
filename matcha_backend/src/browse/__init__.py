from flask import Blueprint

browse_bp = Blueprint('browse', __name__)

from . import routes_browse
