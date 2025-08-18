from flask import Blueprint, request, jsonify, current_app
import sys
import os
from src.auth import auth_bp
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))


from  database.crud.user_crud import User
# auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    ...
    



@auth_bp.route("/register", methods=["POST"])
def register():
    user_data = request.json
    connection_pool = current_app.config["CONNECTION_POOL"]
    print("Connection Pool:", connection_pool)
    if not connection_pool:
        return jsonify({"error": "Database connection pool is not available"}), 500
    user_crud = User(connection_pool)
    result = user_crud.create_user(user_data)
    return {"status": "ok", "data": result}

@auth_bp.route('/logout', methods=['POST'])
def logout():
    ...



