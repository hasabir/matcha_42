#!/usr/bin/env python3
"""
Mock Matcha Backend Server
A simple Flask server that mimics the Matcha backend for testing photo upload functionality
without requiring full database setup.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import time
import json
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"], supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"])

# Mock data storage (in production this would be in a database)
mock_users = {
    "test_user": {
        "username": "test_user",
        "email": "test@example.com", 
        "first_name": "Test",
        "last_name": "User",
        "has_profile": True,
        "profile": {
            "bio": "This is a test user profile",
            "gender": "male",
            "sexual_preferences": "female",
            "age": 25,
            "city": "Test City",
            "country": "Test Country",
            "fame_rating": 85
        },
        "images": [],
        "profile_picture": None
    }
}

# Create uploads directory
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def mock_auth_required(f):
    """Mock authentication decorator"""
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Invalid token format or signature"}), 403
        
        # For testing, accept any non-empty token
        token = auth_header.split(' ')[1]
        if not token or token == "undefined":
            return jsonify({"error": "Invalid token"}), 403
            
        return f(*args, **kwargs)
    decorated.__name__ = f.__name__
    return decorated

@app.route("/api/profile/my_profile", methods=["GET", "HEAD"])
@mock_auth_required
def my_profile():
    """Mock endpoint for getting current user profile"""
    user_data = mock_users["test_user"]
    return jsonify({
        "username": user_data["username"],
        "email": user_data["email"], 
        "first_name": user_data["first_name"],
        "last_name": user_data["last_name"],
        "has_profile": user_data["has_profile"]
    })

@app.route("/api/profile/get_profile/me", methods=["GET"])
@mock_auth_required  
def get_profile_me():
    """Mock endpoint for getting full profile data"""
    user_data = mock_users["test_user"]
    profile = user_data["profile"].copy()
    profile.update({
        "username": user_data["username"],
        "email": user_data["email"],
        "first_name": user_data["first_name"], 
        "last_name": user_data["last_name"],
        "images": user_data["images"],
        "profile_picture": user_data["profile_picture"]
    })
    
    return jsonify({"result": profile})

@app.route("/api/profile/upload_images", methods=["POST"])
@mock_auth_required
def upload_images():
    """Mock endpoint for uploading multiple images"""
    print("📤 Upload images request received")
    
    if 'images' not in request.files:
        return jsonify({"error": "No images provided"}), 400
    
    files = request.files.getlist('images')
    if not files or all(f.filename == '' for f in files):
        return jsonify({"error": "No files selected"}), 400
    
    uploaded_paths = []
    
    for file in files:
        if file and file.filename != '' and allowed_file(file.filename):
            # Generate unique filename
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
            
            try:
                file.save(filepath)
                # Return path relative to static folder for frontend
                relative_path = f"/static/uploads/{unique_filename}"
                uploaded_paths.append(relative_path)
                print(f"✅ Saved file: {relative_path}")
            except Exception as e:
                print(f"❌ Error saving file {filename}: {e}")
                continue
    
    if not uploaded_paths:
        return jsonify({"error": "No valid images were uploaded"}), 400
    
    # Add to mock user data
    user_data = mock_users["test_user"]
    user_data["images"].extend(uploaded_paths)
    
    # Simulate processing delay
    time.sleep(0.5)
    
    return jsonify({
        "message": f"Successfully uploaded {len(uploaded_paths)} images",
        "image_paths": uploaded_paths
    })

@app.route("/api/profile/get_images/<username>", methods=["GET"])
@mock_auth_required
def get_images(username):
    """Mock endpoint for getting user images"""
    if username == "me":
        user_data = mock_users["test_user"]
        return jsonify({"result": user_data["images"]})
    else:
        return jsonify({"result": []})

@app.route("/api/profile/delete_image", methods=["DELETE"])
@mock_auth_required
def delete_image():
    """Mock endpoint for deleting an image"""
    data = request.get_json()
    if not data or 'image_path' not in data:
        return jsonify({"error": "No image path provided"}), 400
    
    image_path = data['image_path']
    print(f"🗑️ Delete image request: {image_path}")
    
    # Remove from mock user data
    user_data = mock_users["test_user"]
    if image_path in user_data["images"]:
        user_data["images"].remove(image_path)
        
        # If it was the profile picture, update to next available image
        if user_data["profile_picture"] == image_path:
            user_data["profile_picture"] = user_data["images"][0] if user_data["images"] else None
        
        # Try to delete actual file
        try:
            filename = image_path.replace("/static/uploads/", "")
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"✅ Deleted file: {filepath}")
        except Exception as e:
            print(f"⚠️ Could not delete file: {e}")
        
        return jsonify({"message": "Image deleted successfully"})
    else:
        return jsonify({"error": "Image not found"}), 404

@app.route("/api/profile/get_profile_vistors", methods=["GET"])
@mock_auth_required
def get_profile_visitors():
    """Mock endpoint for profile visitors"""
    return jsonify({"result": []})

@app.route("/api/interactions/who_liked_me", methods=["GET"])
@mock_auth_required
def who_liked_me():
    """Mock endpoint for who liked me"""
    return jsonify([])

@app.route("/api/interactions/my_connections", methods=["GET"])
@mock_auth_required
def my_connections():
    """Mock endpoint for connections"""
    return jsonify([])

@app.route("/static/uploads/<filename>")
def uploaded_file(filename):
    """Serve uploaded files"""
    from flask import send_from_directory
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "running",
        "message": "Mock Matcha Backend is running!",
        "endpoints": [
            "POST /api/profile/upload_images",
            "DELETE /api/profile/delete_image", 
            "GET /api/profile/my_profile",
            "GET /api/profile/get_profile/me"
        ]
    })

if __name__ == "__main__":
    port = 5001  # Use port 5001 to avoid conflicts
    print("🚀 Starting Mock Matcha Backend Server...")
    print("📁 Upload folder:", os.path.abspath(UPLOAD_FOLDER))
    print("🌐 CORS enabled for http://localhost:3000")
    print(f"🔗 Health check: http://localhost:{port}/")
    print("=" * 50)
    
    app.run(host="0.0.0.0", port=port, debug=True)