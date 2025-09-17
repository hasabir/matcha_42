import os
import sys
import logging

from flask import Blueprint, request, jsonify, current_app, g, send_file, url_for
from werkzeug.exceptions import BadRequestKeyError

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))

from database.crud.user_crud import User
from database.crud.profile_crud import Profile
from utils.validate_profile_data import validate_profile_data
from utils.security import auth_guard
from utils.fame_rating import calculate_fame_rating
from utils.image_handler import upload_pictures
from src.user_profile import profile_bp

logger = logging.getLogger(__name__)


@profile_bp.route("/update_profile_picture", methods=["PUT", "DELETE"])
@auth_guard
def update_profile_picture():
    '''Handle profile picture operations for the logged in user
    PUT: Upload a new profile picture (expects file in 'profile_pic' field)
    DELETE: Remove the profile picture (sets to null in database)
    '''
    try:
        connection_pool = current_app.config["CONNECTION_POOL"]
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500
        
        profile_crud = Profile(connection_pool)
        
        # Handle DELETE request - remove profile picture
        if request.method == "DELETE":
            profile_crud.update_profile(g.user_id, {"profile_picture": None})
            return jsonify({"status": "ok", "message": "Profile picture removed successfully"}), 200
        
        # Handle PUT request - upload new profile picture
        if 'profile_pic' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400
        
        requested_file = request.files['profile_pic']
        if requested_file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not requested_file:
            return jsonify({"error": "Invalid file"}), 400
        
        profile_path = upload_pictures(requested_file, g.user_id)
        url_path = url_for('static', filename=profile_path)
        profile_crud.update_profile(g.user_id, {"profile_picture": url_path})
        
        return jsonify({"status": "ok"}), 200
        
    except BadRequestKeyError:
        return jsonify({"error": "KeyError, file must be stored with key = profile_pic"}), 415
    except Exception as e:
        return jsonify({"error": str(e)}), 409
    except TypeError as te:
        return jsonify({"error": str(te)}), 400



@profile_bp.route("/upload_images", methods=["POST"])
@auth_guard
def upload_images():
    '''upload multiple images for the logged in user
        Expects files in the 'images' field of the form data.
        '''
    try:
        if 'images' not in request.files:
            return jsonify({"error": "No files uploaded or required filed name is not correct <images>"}), 400

        uploaded_files = request.files.getlist('images')
        if not uploaded_files or uploaded_files == []:
            return jsonify({"error": "No files uploaded"}), 400

        connection_pool = current_app.config["CONNECTION_POOL"]
        profile_crud = Profile(connection_pool)
        if not  connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500
        image_paths = []
        for file in uploaded_files:
            path = upload_pictures(file, g.user_id)
            url_path = url_for('static', filename=path)
            profile_crud.insert_images(url_path, g.user_id)
            image_paths.append(url_path)
        return jsonify({"status": "ok", "image_paths": image_paths}), 200

    except BadRequestKeyError:
        return jsonify({"error": "KeyError, files must be stored with key = images"}), 415
    except Exception as e:
        logger.exception("Error uploading images")
        return jsonify({"error": str(e)}), 409




@profile_bp.route("/get_profile_pic/<username>")
@auth_guard
def get_user_profile_pic(username):
    '''get the profile picture of a user,
     if username is "me" get the profile picture of the logged in user'''
    try:
        connection_pool = current_app.config["CONNECTION_POOL"]
        if not  connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500
        profile_crud = Profile(connection_pool)

        #TODO check first if the user is not blocked then continue
        
        if username == "me":
            profile_data = profile_crud.get_profile_by_user_id(g.user_id)
            logger.debug(f"⚠️⚠️⚠️🔍 request data -> {profile_data} ⚠️⚠️⚠️")

        else:
            user_crud = User(connection_pool)
            user_data = user_crud.get_user_by_username(username=username)
            if not user_data:
                return jsonify({"error": "user not found"}), 404
            profile_data = profile_crud.get_profile_by_user_id(user_data["id"])

        return jsonify({"status": "ok", "result": profile_data["profile_picture"]})

    except KeyError:
        return jsonify({"error": "Profile picture not found in database"}), 404
    except Exception as e:
        current_app.logger.error(f"Error retrieving profile picture: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500




@profile_bp.route("/get_images/<username>")
@auth_guard
def get_images(username):
    '''get all images of a user,
     if username is "me" get the images of the logged in user'''
    try:
        connection_pool = current_app.config["CONNECTION_POOL"]
        if not connection_pool:
            return jsonify({"error": "Database connection pool is not available"}), 500

        profile_crud = Profile(connection_pool)
        if username == "me":
            user_images = profile_crud.get_images(g.user_id)
            return jsonify({"result": user_images}), 200
        
        user_crud = User(connection_pool)
        user_data = user_crud.get_user_by_username(username=username)
        if not user_data:
            return jsonify({"error": "user not found"}), 404

        #TODO check first if the user is not blocked then continue
        user_images = profile_crud.get_images(user_data["id"])

        return jsonify({"result": user_images}), 200

    except KeyError:
        return jsonify({"error": "Profile picture not found in database"}), 404
    
    except Exception as e:
        current_app.logger.error(f"Error retrieving profile picture: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


