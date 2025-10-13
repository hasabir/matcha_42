# import os
# import sys
# import logging

# from flask import Blueprint, request, jsonify, current_app, g, send_file, url_for
# from werkzeug.exceptions import BadRequestKeyError

# sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))

# from database.crud.user_crud import User
# from database.crud.profile_crud import Profile
# from database.crud.interactions_crud import Interactions
# from utils.validate_profile_data import validate_profile_data
# from utils.security import auth_guard
# from utils.fame_rating import calculate_fame_rating
# from utils.image_handler import upload_pictures
# from src.user_profile import profile_bp

# logger = logging.getLogger(__name__)


# @profile_bp.route("/update_profile_picture", methods=["PUT", "DELETE"])
# @auth_guard
# def update_profile_picture():
#     '''Handle profile picture operations for the logged in user
#     PUT: Upload a new profile picture (expects file in 'profile_pic' field)
#     DELETE: Remove the profile picture (sets to null in database)
#     '''
#     try:
#         connection_pool = current_app.config["CONNECTION_POOL"]
#         if not connection_pool:
#             return jsonify({"error": "Database connection pool is not available"}), 500
        
#         profile_crud = Profile(connection_pool)
        
#         # Handle DELETE request - remove profile picture
#         if request.method == "DELETE":
#             profile_crud.update_profile(g.user_id, {"profile_picture": None})
#             return jsonify({"status": "ok", "message": "Profile picture removed successfully"}), 200
        
#         # Handle PUT request - upload new profile picture
#         if 'profile_pic' not in request.files:
#             return jsonify({"error": "No file part in the request"}), 400
        
#         requested_file = request.files['profile_pic']
#         if requested_file.filename == '':
#             return jsonify({"error": "No file selected"}), 400
        
#         if not requested_file:
#             return jsonify({"error": "Invalid file"}), 400
        
#         profile_path = upload_pictures(requested_file, g.user_id)
#         url_path = url_for('static', filename=profile_path)
#         profile_crud.update_profile(g.user_id, {"profile_picture": url_path})
        
#         return jsonify({"status": "ok"}), 200
        
#     except BadRequestKeyError:
#         return jsonify({"error": "KeyError, file must be stored with key = profile_pic"}), 415
#     except Exception as e:
#         return jsonify({"error": str(e)}), 409
#     except TypeError as te:
#         return jsonify({"error": str(te)}), 400



# @profile_bp.route("/upload_images", methods=["POST"])
# @auth_guard
# def upload_images():
#     '''upload multiple images for the logged in user
#         Expects files in the 'images' field of the form data.
#         '''
#     try:
#         if 'images' not in request.files:
#             return jsonify({"error": "No files uploaded or required filed name is not correct <images>"}), 400

#         uploaded_files = request.files.getlist('images')
#         if not uploaded_files or uploaded_files == []:
#             return jsonify({"error": "No files uploaded"}), 400

#         connection_pool = current_app.config["CONNECTION_POOL"]
#         profile_crud = Profile(connection_pool)
#         if not  connection_pool:
#             return jsonify({"error": "Database connection pool is not available"}), 500
#         image_paths = []
#         for file in uploaded_files:
#             logger.debug(f"$$$$$$$$$$$$$$$$$$$ Processing file: {file.filename}")
#             path = upload_pictures(file, g.user_id, False)
#             url_path = url_for('static', filename=path)
#             profile_crud.insert_images(url_path, g.user_id)
#             image_paths.append(url_path)
#         return jsonify({"status": "ok", "image_paths": image_paths}), 200

#     except BadRequestKeyError:
#         return jsonify({"error": "KeyError, files must be stored with key = images"}), 415
#     except Exception as e:
#         logger.exception("Error uploading images")
#         return jsonify({"error": str(e)}), 409




# @profile_bp.route("/get_profile_pic/<username>")
# @auth_guard
# def get_user_profile_pic(username):
#     '''get the profile picture of a user,
#      if username is "me" get the profile picture of the logged in user'''
#     try:
#         connection_pool = current_app.config["CONNECTION_POOL"]
#         if not  connection_pool:
#             return jsonify({"error": "Database connection pool is not available"}), 500
#         profile_crud = Profile(connection_pool)


#         user_crud = User(connection_pool)
        
#         if username == "me" \
#             or user_crud.get_user_by('id', g.user_id, 'username')["username"]["username"] == username:
#             profile_data = profile_crud.get_profile_by_user_id(g.user_id)

#         else:
#             user_data = user_crud.get_user_by_username(username=username)
#             if not user_data:
#                 return jsonify({"error": "user not found"}), 404
#             interactions_crud = Interactions(connection_pool, g.user_id, user_data["id"])
            
#             if interactions_crud.is_blocked():
#                 return jsonify({"error": "You are blocked by this user"}), 403
#             profile_data = profile_crud.get_profile_by_user_id(user_data["id"])

#         return jsonify({"status": "ok", "result": profile_data["profile_picture"]})



#     except KeyError:
#         return jsonify({"error": "Profile picture not found in database"}), 404
#     except Exception as e:
#         current_app.logger.error(f"Error retrieving profile picture: {str(e)}")
#         return jsonify({"error": e}), 409




# @profile_bp.route("/get_images/<username>")
# @auth_guard
# def get_images(username):
#     '''get all images of a user,
#      if username is "me" get the images of the logged in user'''
#     try:
#         connection_pool = current_app.config["CONNECTION_POOL"]
#         if not connection_pool:
#             return jsonify({"error": "Database connection pool is not available"}), 500

#         profile_crud = Profile(connection_pool)
#         user_crud = User(connection_pool)
#         if username == "me"\
#             or user_crud.get_user_by('id', g.user_id, 'username')["username"]["username"]["username"]["username"] == username:
#             user_images = profile_crud.get_images(g.user_id)
#             return jsonify({"result": user_images}), 200
        
#         user_data = user_crud.get_user_by_username(username=username)
#         if not user_data:
#             return jsonify({"error": "user not found"}), 404

#         interactions_crud = Interactions(connection_pool, g.user_id, user_data["id"])
            
#         if interactions_crud.is_blocked():
#             return jsonify({"error": "You are blocked by this user"}), 403
        
#         user_images = profile_crud.get_images(user_data["id"])

#         return jsonify({"result": user_images}), 200

#     except KeyError:
#         return jsonify({"error": "Profile picture not found in database"}), 404
    
#     except Exception as e:
#         current_app.logger.error(f"Error retrieving profile picture: {str(e)}")
#         return jsonify({"error": e}), 409


# @profile_bp.route("/delete_image/<image_id>", methods=["DELETE"])
# @auth_guard
# def delete_image(image_id):
#     '''Delete an image of the logged in user by image_id'''
#     try:
#         connection_pool = current_app.config["CONNECTION_POOL"]
#         if not connection_pool:
#             return jsonify({"error": "Database connection pool is not available"}), 500

#         if not image_id.isdigit(): 
#             return jsonify({"error": "Invalid image ID format"}), 400

#         profile_crud = Profile(connection_pool)
        
#         if not profile_crud.verify_image_ownership(g.user_id, image_id):
#             return jsonify({"error": "Image not found or you don't have permission to delete it"}), 404
        
#         profile_crud.delete_image(g.user_id, image_id)
        
#         return jsonify({"status": "ok", "message": "Image deleted successfully"}), 200

#     except ValueError as e:
#         current_app.logger.warning(f"Validation error deleting image: {str(e)}")
#         return jsonify({"error": str(e)}), 400
#     except Exception as e:
#         current_app.logger.error(f"Error deleting image: {str(e)}")
#         return jsonify({"error": e}), 409   




import logging
import os
import sys
from flask import request, jsonify, current_app, g, url_for

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))

from src.user_profile import profile_bp
from utils.security import auth_guard
from utils.image_handler import upload_pictures
from database.crud.user_crud import User
from database.crud.profile_crud import Profile
from database.crud.interactions_crud import Interactions

logger = logging.getLogger(__name__)

@profile_bp.route("/update_profile_picture", methods=["PUT", "DELETE"])
@auth_guard
def update_profile_picture():
    """
    PUT: multipart/form-data with 'profile_pic'
    DELETE: remove existing profile picture (set to null)
    """
    try:
        pool = current_app.config.get("CONNECTION_POOL")
        if not pool:
            return jsonify({"error": "Database connection pool is not available"}), 500

        profile = Profile(pool)

        if request.method == "DELETE":
            profile.update_profile(g.user_id, {"profile_picture": None})
            return jsonify({"status": "ok", "message": "Profile picture removed successfully"}), 200

        # PUT flow
        if 'profile_pic' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400
        requested_file = request.files['profile_pic']
        if requested_file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        stored_path = upload_pictures(requested_file, g.user_id)
        url_path = url_for('static', filename=stored_path)
        profile.update_profile(g.user_id, {"profile_picture": url_path})

        return jsonify({"status": "ok"}), 200
    except Exception as e:
        logger.exception("update_profile_picture failed")
        return jsonify({"error": str(e)}), 409


@profile_bp.route("/upload_images", methods=["POST"])
@auth_guard
def upload_images():
    """
    Upload multiple images (field: 'images')
    """
    try:
        if 'images' not in request.files:
            return jsonify({"error": "No files uploaded or field name must be 'images'"}), 400

        files = request.files.getlist('images')
        if not files:
            return jsonify({"error": "No files uploaded"}), 400

        pool = current_app.config.get("CONNECTION_POOL")
        if not pool:
            return jsonify({"error": "Database connection pool is not available"}), 500

        profile = Profile(pool)
        image_urls = []
        for f in files:
            stored = upload_pictures(f, g.user_id, is_profile_picture=False)
            url_path = url_for('static', filename=stored)
            profile.insert_images(url_path, g.user_id)
            image_urls.append(url_path)

        return jsonify({"status": "ok", "image_paths": image_urls}), 200
    except Exception as e:
        logger.exception("upload_images failed")
        return jsonify({"error": str(e)}), 409


@profile_bp.route("/get_profile_pic/<username>", methods=["GET"])
@auth_guard
def get_user_profile_pic(username):
    """
    Return profile picture URL for <username> (or 'me').
    If blocked, deny access.
    """
    try:
        pool = current_app.config.get("CONNECTION_POOL")
        if not pool:
            return jsonify({"error": "Database connection pool is not available"}), 500

        profile = Profile(pool)
        user_crud = User(pool)

        my_username = user_crud.get_user_by('id', g.user_id, 'username')["username"]
        if username == "me" or my_username == username:
            data = profile.get_profile_by_user_id(g.user_id)
            return jsonify({"status": "ok", "result": data.get("profile_picture")}), 200

        other = user_crud.get_user_by_username(username=username)
        if not other:
            return jsonify({"error": "user not found"}), 404

        if Interactions(pool, g.user_id, other["id"]).is_blocked():
            return jsonify({"error": "You are blocked by this user"}), 403

        data = profile.get_profile_by_user_id(other["id"])
        return jsonify({"status": "ok", "result": data.get("profile_picture")}), 200
    except Exception as e:
        logger.exception("get_user_profile_pic failed")
        return jsonify({"error": str(e)}), 409


@profile_bp.route("/get_images/<username>", methods=["GET"])
@auth_guard
def get_images(username):
    """
    Return all image URLs for <username> (or 'me').
    """
    try:
        pool = current_app.config.get("CONNECTION_POOL")
        if not pool:
            return jsonify({"error": "Database connection pool is not available"}), 500

        profile = Profile(pool)
        user_crud = User(pool)

        my_username = user_crud.get_user_by('id', g.user_id, 'username')["username"]
        if username == "me" or my_username == username:
            imgs = profile.get_images(g.user_id)
            return jsonify({"result": imgs}), 200

        other = user_crud.get_user_by_username(username=username)
        if not other:
            return jsonify({"error": "user not found"}), 404

        if Interactions(pool, g.user_id, other["id"]).is_blocked():
            return jsonify({"error": "You are blocked by this user"}), 403

        imgs = profile.get_images(other["id"])
        return jsonify({"result": imgs}), 200
    except Exception as e:
        logger.exception("get_images failed")
        return jsonify({"error": str(e)}), 409


@profile_bp.route("/delete_image/<image_id>", methods=["DELETE"])
@auth_guard
def delete_image(image_id):
    """Delete an image owned by the logged-in user."""
    try:
        pool = current_app.config.get("CONNECTION_POOL")
        if not pool:
            return jsonify({"error": "Database connection pool is not available"}), 500

        profile = Profile(pool)

        if not image_id.isdigit():
            return jsonify({"error": "Invalid image ID format"}), 400

        if not profile.verify_image_ownership(g.user_id, image_id):
            return jsonify({"error": "Image not found or no permission"}), 404

        profile.delete_image(g.user_id, image_id)
        return jsonify({"status": "ok", "message": "Image deleted successfully"}), 200
    except Exception as e:
        logger.exception("delete_image failed")
        return jsonify({"error": str(e)}), 409
