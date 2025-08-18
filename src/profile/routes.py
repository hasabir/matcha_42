from flask import Blueprint, request, jsonify

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/<int:user_id>', methods=['GET'])
def get_profile(user_id):
    # Logic to retrieve user profile by user_id
    return jsonify({"message": f"Profile for user {user_id}"}), 200