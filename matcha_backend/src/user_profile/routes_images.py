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

@profile_bp.route("/upload_images", methods=["POST"])
@auth_guard
def upload_images():
    """Upload multiple images (field: 'images') - Up to 5 photos allowed"""
    try:
        if 'images' not in request.files:
            return jsonify({"error": "No files uploaded or field name must be 'images'"}), 400

        files = request.files.getlist('images')
        if not files or all(f.filename == '' for f in files):
            return jsonify({"error": "No files uploaded"}), 400

        pool = current_app.config.get("CONNECTION_POOL")
        if not pool:
            return jsonify({"error": "Database connection pool is not available"}), 500

        profile = Profile(pool)
        
        # Check current image count and limit to 5 total
        existing_images = profile.get_images(g.user_id)
        current_count = len(existing_images)
        
        if current_count + len(files) > 5:
            return jsonify({"error": f"Cannot upload {len(files)} photos. Maximum 5 photos allowed. You currently have {current_count}."}), 400

        image_urls = []
        for f in files:
            if f and f.filename != '':
                stored = upload_pictures(f, g.user_id, is_profile_picture=False)
                url_path = url_for('static', filename=stored)
                profile.insert_images(url_path, g.user_id)
                image_urls.append(url_path)
        
        if not image_urls:
            return jsonify({"error": "No valid images were processed"}), 400
            
        # If this is the user's first photo, set it as profile picture
        current_profile = profile.get_profile_by_user_id(g.user_id)
        if current_count == 0 and image_urls and (not current_profile or not current_profile.get("profile_picture")):
            profile.update_profile(g.user_id, {"profile_picture": image_urls[0]})
            logger.info(f"Set first image as profile picture: {image_urls[0]}")

        return jsonify({"status": "ok", "image_paths": image_urls}), 200
    except Exception as e:
        logger.exception("upload_images failed")
        return jsonify({"error": str(e)}), 409

@profile_bp.route("/get_images/<username>", methods=["GET"])
@auth_guard
def get_images(username):
    """Return all image URLs for username"""
    try:
        pool = current_app.config.get("CONNECTION_POOL")
        if not pool:
            return jsonify({"error": "Database connection pool not available"}), 500

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

@profile_bp.route("/delete_image", methods=["DELETE", "OPTIONS"])
@auth_guard
def delete_image_by_path():
    """Delete an image by path for the logged-in user."""
    try:
        # Handle CORS preflight
        if request.method == "OPTIONS":
            return "", 200
            
        pool = current_app.config.get("CONNECTION_POOL")
        if not pool:
            return jsonify({"error": "Database connection pool is not available"}), 500

        data = request.get_json()
        if not data or 'image_path' not in data:
            return jsonify({"error": "No image path provided"}), 400

        image_path = data['image_path']
        logger.info(f"Attempting to delete image: {image_path} for user {g.user_id}")

        profile = Profile(pool)
        
        # Get current profile to check if deleting profile picture
        current_profile = profile.get_profile_by_user_id(g.user_id)
        current_profile_pic = current_profile.get("profile_picture") if current_profile else None
        is_deleting_profile_pic = (current_profile_pic == image_path)
        
        # Get user's images and find the one matching the path
        user_images = profile.get_user_images(g.user_id)
        logger.info(f"Found {len(user_images)} images for user {g.user_id}")
        
        for idx, img in enumerate(user_images):
            logger.info(f"Image {idx}: ID={img.get('image_id')}, Path={img.get('image_path')}")
        
        image_to_delete = None
        
        for img in user_images:
            img_path = img.get('image_path', '')
            # More comprehensive path matching
            if (img_path == image_path or 
                img_path.endswith(image_path.split('/')[-1]) or
                image_path.endswith(img_path.split('/')[-1]) or
                img_path.replace('/static/', '') == image_path.replace('/static/', '') or
                img_path.split('/')[-1] == image_path.split('/')[-1]):
                image_to_delete = img
                logger.info(f"Found matching image: {img}")
                break
        
        if not image_to_delete:
            logger.warning(f"Image not found. Requested: {image_path}, Available images: {[img.get('image_path') for img in user_images]}")
            return jsonify({"error": "Image not found"}), 404

        # Delete the image using the image ID
        image_id = image_to_delete.get('image_id')
        if not image_id:
            return jsonify({"error": "Image ID not found"}), 400

        # Delete from database
        profile.delete_image(g.user_id, image_id)
        
        # If we deleted the profile picture, update it
        if is_deleting_profile_pic:
            # Get remaining images after deletion
            remaining_images = profile.get_images(g.user_id)
            if remaining_images:
                # Set the first remaining image as new profile picture
                profile.update_profile(g.user_id, {"profile_picture": remaining_images[0]})
                logger.info(f"Updated profile picture to: {remaining_images[0]}")
            else:
                # No images left, clear profile picture
                profile.update_profile(g.user_id, {"profile_picture": None})
                logger.info("Cleared profile picture - no images remaining")
        
        # Try to delete the physical file as well
        try:
            # Convert URL path to file system path
            if image_path.startswith('/static/'):
                file_path = os.path.join(current_app.static_folder, image_path[8:])
            elif image_path.startswith('static/'):
                file_path = os.path.join(current_app.static_folder, image_path[7:])
            else:
                file_path = os.path.join(current_app.static_folder, image_path.lstrip('/'))
            
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted physical file: {file_path}")
        except Exception as file_error:
            logger.warning(f"Could not delete physical file {image_path}: {file_error}")
        
        logger.info(f"Successfully deleted image ID {image_id} for user {g.user_id}")
        
        return jsonify({"status": "ok", "message": "Image deleted successfully"}), 200
    except Exception as e:
        logger.exception("delete_image_by_path failed")
        return jsonify({"error": str(e)}), 409

@profile_bp.route("/get_profile_pic/<username>", methods=["GET"])
@auth_guard
def get_user_profile_pic(username):
    """Return profile picture URL for username"""
    try:
        pool = current_app.config.get("CONNECTION_POOL")
        if not pool:
            return jsonify({"error": "Database connection pool not available"}), 500

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
