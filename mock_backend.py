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
            "bio": "This is a test user profile with interests in technology and music",
            "gender": "Male",
            "sexual_preferences": "Women", 
            "age": 25,
            "city": "Test City",
            "country": "Test Country",
            "fame_rating": 85,
            "latitude": 40.7128,
            "longitude": -74.0060,
            "accuracy": 10
        },
        "images": [],
        "profile_picture": None,
        "interests": ["Technology", "Music", "Travel", "Gaming"],
        "profile_views": [],
        "likes_received": [],
        "connections": [],
        "location_history": []
    },
    "alice_smith": {
        "username": "alice_smith",
        "email": "alice@example.com",
        "first_name": "Alice",
        "last_name": "Smith",
        "has_profile": True,
        "profile": {
            "bio": "Love hiking and outdoor adventures! Looking for someone to explore the world with.",
            "gender": "Female",
            "sexual_preferences": "Men",
            "age": 23,
            "city": "Test City",
            "country": "Test Country", 
            "fame_rating": 92,
            "latitude": 40.7589,
            "longitude": -73.9851,
            "accuracy": 15
        },
        "images": ["/static/uploads/alice1.jpg", "/static/uploads/alice2.jpg"],
        "profile_picture": "/static/uploads/alice1.jpg",
        "interests": ["Travel", "Hiking", "Photography", "Music"],
        "profile_views": [],
        "likes_received": [],
        "connections": [],
        "location_history": []
    },
    "bob_jones": {
        "username": "bob_jones", 
        "email": "bob@example.com",
        "first_name": "Bob",
        "last_name": "Jones",
        "has_profile": True,
        "profile": {
            "bio": "Software developer by day, musician by night. Let's code and create music together!",
            "gender": "Male",
            "sexual_preferences": "Both",
            "age": 28,
            "city": "Tech Valley",
            "country": "Test Country",
            "fame_rating": 78,
            "latitude": 40.6892,
            "longitude": -74.0445,
            "accuracy": 12
        },
        "images": ["/static/uploads/bob1.jpg"],
        "profile_picture": "/static/uploads/bob1.jpg", 
        "interests": ["Technology", "Music", "Gaming", "Cooking"],
        "profile_views": [],
        "likes_received": [],
        "connections": [],
        "location_history": []
    },
    "charlie_brown": {
        "username": "charlie_brown",
        "email": "charlie@example.com",
        "first_name": "Charlie",
        "last_name": "Brown",
        "has_profile": True,
        "profile": {
            "bio": "Artist and creative soul. I paint, I dance, I live life to the fullest!",
            "gender": "Non-binary",
            "sexual_preferences": "All",
            "age": 26,
            "city": "Art District",
            "country": "Test Country",
            "fame_rating": 88,
            "latitude": 40.7311,
            "longitude": -73.9897,
            "accuracy": 18
        },
        "images": ["/static/uploads/charlie1.jpg", "/static/uploads/charlie2.jpg", "/static/uploads/charlie3.jpg"],
        "profile_picture": "/static/uploads/charlie1.jpg",
        "interests": ["Art", "Dancing", "Music", "Travel", "Photography"],
        "profile_views": [],
        "likes_received": [],
        "connections": [],
        "location_history": []
    },
    "diana_wilson": {
        "username": "diana_wilson",
        "email": "diana@example.com",
        "first_name": "Diana",
        "last_name": "Wilson",
        "has_profile": True,
        "profile": {
            "bio": "Fitness enthusiast and nutrition coach. Health is wealth!",
            "gender": "Female", 
            "sexual_preferences": "Women",
            "age": 30,
            "city": "Wellness Town",
            "country": "Test Country",
            "fame_rating": 95,
            "latitude": 40.8176,
            "longitude": -73.9782,
            "accuracy": 8
        },
        "images": ["/static/uploads/diana1.jpg", "/static/uploads/diana2.jpg"],
        "profile_picture": "/static/uploads/diana1.jpg",
        "interests": ["Fitness", "Health", "Cooking", "Travel", "Reading"],
        "profile_views": [],
        "likes_received": [],
        "connections": [],
        "location_history": []
    },
    "erik_larson": {
        "username": "erik_larson",
        "email": "erik@example.com", 
        "first_name": "Erik",
        "last_name": "Larson",
        "has_profile": True,
        "profile": {
            "bio": "Adventure seeker and travel blogger. Next destination: everywhere!",
            "gender": "Male",
            "sexual_preferences": "Women",
            "age": 32,
            "city": "Adventure Bay",
            "country": "Far Country",
            "fame_rating": 73,
            "latitude": 41.8781,
            "longitude": -87.6298,
            "accuracy": 25
        },
        "images": ["/static/uploads/erik1.jpg"],
        "profile_picture": "/static/uploads/erik1.jpg",
        "interests": ["Travel", "Adventure", "Photography", "Writing", "Hiking"],
        "profile_views": [],
        "likes_received": [],
        "connections": [],
        "location_history": []
    }
}

# Mock interaction data
mock_interactions = {
    "likes": [],
    "blocks": [],
    "visits": [],
    "reports": []
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
    
    # Set first uploaded image as profile picture if user has no profile picture
    if not user_data["profile_picture"] and uploaded_paths:
        user_data["profile_picture"] = uploaded_paths[0]
        print(f"🖼️ Set profile picture to: {uploaded_paths[0]}")
    
    # Simulate processing delay
    time.sleep(0.5)
    
    return jsonify({
        "status": "ok",
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

@app.route("/api/profile/get_profile_pic/<username>", methods=["GET"])
@mock_auth_required
def get_profile_pic(username):
    """Mock endpoint for getting user profile picture"""
    if username == "me":
        user_data = mock_users["test_user"]
        return jsonify({"status": "ok", "result": user_data["profile_picture"]})
    else:
        return jsonify({"status": "ok", "result": None})

@app.route("/api/profile/delete_image", methods=["DELETE", "OPTIONS"])
@mock_auth_required
def delete_image():
    """Mock endpoint for deleting an image"""
    # Handle CORS preflight
    if request.method == "OPTIONS":
        return "", 200
        
    data = request.get_json()
    if not data or 'image_path' not in data:
        return jsonify({"error": "No image path provided"}), 400
    
    image_path = data['image_path']
    print(f"🗑️ Delete image request: {image_path}")
    
    # Remove from mock user data
    user_data = mock_users["test_user"]
    
    # Find and remove the image (handle different path formats)
    image_found = False
    for i, img in enumerate(user_data["images"]):
        if (img == image_path or 
            img.endswith(image_path.split('/')[-1]) or 
            image_path.endswith(img.split('/')[-1]) or
            img.replace('/static/', '') == image_path.replace('/static/', '')):
            
            removed_image = user_data["images"].pop(i)
            image_found = True
            print(f"✅ Removed image: {removed_image}")
            
            # If it was the profile picture, update to next available image
            if user_data["profile_picture"] == removed_image:
                user_data["profile_picture"] = user_data["images"][0] if user_data["images"] else None
                print(f"🖼️ Updated profile picture to: {user_data['profile_picture']}")
            
            # Try to delete actual file
            try:
                filename = removed_image.replace("/static/uploads/", "")
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                if os.path.exists(filepath):
                    os.remove(filepath)
                    print(f"🗑️ Deleted file: {filepath}")
            except Exception as e:
                print(f"⚠️ Could not delete file: {e}")
            
            break
    
    if image_found:
        return jsonify({"status": "ok", "message": "Image deleted successfully"})
    else:
        print(f"❌ Image not found in user data. Available images: {user_data['images']}")
        return jsonify({"error": "Image not found"}), 404

@app.route("/api/profile/get_profile_vistors", methods=["GET"])
@mock_auth_required
def get_profile_visitors():
    """Mock endpoint for profile visitors"""
    user_data = mock_users["test_user"]
    visitors = user_data.get("profile_views", [])
    return jsonify({"result": visitors})

@app.route("/api/interactions/who_liked_me", methods=["GET"])
@mock_auth_required
def who_liked_me():
    """Mock endpoint for who liked me"""
    user_data = mock_users["test_user"]
    likes = user_data.get("likes_received", [])
    return jsonify(likes)

@app.route("/api/interactions/my_connections", methods=["GET"])
@mock_auth_required
def my_connections():
    """Mock endpoint for connections/matches"""
    user_data = mock_users["test_user"]
    connections = user_data.get("connections", [])
    return jsonify(connections)

@app.route("/api/profile/get_fame_rating", methods=["GET"])
@mock_auth_required
def get_fame_rating():
    """Mock endpoint for fame rating"""
    user_data = mock_users["test_user"]
    fame_rating = user_data["profile"].get("fame_rating", 50)
    return jsonify({"fame_rating": fame_rating})

@app.route("/api/profile/update_profile", methods=["POST", "PATCH"])
@mock_auth_required
def update_profile():
    """Mock endpoint for updating profile information"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    user_data = mock_users["test_user"]
    
    # Update user basic info
    if "first_name" in data:
        user_data["first_name"] = data["first_name"]
    if "last_name" in data:
        user_data["last_name"] = data["last_name"]
    if "email" in data:
        user_data["email"] = data["email"]
    
    # Update profile data
    profile_fields = ["bio", "gender", "sexual_preferences", "age", "location", "city", "country"]
    for field in profile_fields:
        if field in data:
            user_data["profile"][field] = data[field]
    
    # Update GPS coordinates
    if "lat" in data and "lng" in data:
        user_data["profile"]["latitude"] = data["lat"]
        user_data["profile"]["longitude"] = data["lng"]
        if "accuracy" in data:
            user_data["profile"]["accuracy"] = data["accuracy"]
        
        # Log location update
        user_data["location_history"].append({
            "latitude": data["lat"],
            "longitude": data["lng"],
            "accuracy": data.get("accuracy", 0),
            "timestamp": time.time(),
            "method": "manual_update"
        })
    
    print(f"🔄 Profile updated: {data}")
    
    return jsonify({"status": "ok", "message": "Profile updated successfully"})

@app.route("/api/profile/set_location", methods=["POST"])
@mock_auth_required
def set_location():
    """Mock endpoint for setting GPS location"""
    data = request.get_json()
    if not data or "latitude" not in data or "longitude" not in data:
        return jsonify({"error": "Latitude and longitude required"}), 400
    
    user_data = mock_users["test_user"]
    user_data["profile"]["latitude"] = data["latitude"]
    user_data["profile"]["longitude"] = data["longitude"]
    user_data["profile"]["accuracy"] = data.get("accuracy", 0)
    
    # Log location update
    user_data["location_history"].append({
        "latitude": data["latitude"],
        "longitude": data["longitude"],
        "accuracy": data.get("accuracy", 0),
        "timestamp": time.time(),
        "method": "gps_update"
    })
    
    print(f"📍 Location set: {data['latitude']}, {data['longitude']}")
    
    return jsonify({"status": "ok", "message": "Location updated successfully"})

@app.route("/api/profile/get_user_tags", methods=["GET"])
@mock_auth_required
def get_user_tags():
    """Mock endpoint for getting user interests/tags"""
    user_data = mock_users["test_user"]
    interests = user_data.get("interests", [])
    # Format as expected by frontend
    formatted_tags = [{"tag": tag} for tag in interests]
    return jsonify({"result": formatted_tags})

@app.route("/api/profile/add_tags", methods=["POST"])
@mock_auth_required
def add_tags():
    """Mock endpoint for adding interest tags"""
    data = request.get_json()
    if not data or "tags" not in data:
        return jsonify({"error": "Tags required"}), 400
    
    user_data = mock_users["test_user"]
    new_tags = data["tags"]
    current_interests = user_data.get("interests", [])
    
    # Add new tags (avoid duplicates)
    for tag in new_tags:
        if tag not in current_interests:
            current_interests.append(tag)
    
    user_data["interests"] = current_interests
    print(f"🏷️ Tags added: {new_tags}")
    
    return jsonify({"status": "ok", "message": "Tags added successfully"})

@app.route("/api/interactions/like/<username>", methods=["POST"])
@mock_auth_required
def like_user(username):
    """Mock endpoint for liking a user"""
    print(f"💖 Like action for user: {username}")
    
    # Simulate match check
    is_match = False  # You could add logic here for mutual likes
    
    return jsonify({
        "status": "ok", 
        "message": f"Liked {username}",
        "match": is_match
    })

@app.route("/api/interactions/unlike/<username>", methods=["POST"])
@mock_auth_required
def unlike_user(username):
    """Mock endpoint for unliking a user"""
    print(f"💔 Unlike action for user: {username}")
    
    return jsonify({
        "status": "ok", 
        "message": f"Unliked {username}"
    })

@app.route("/api/interactions/block/<username>", methods=["POST"])
@mock_auth_required
def block_user(username):
    """Mock endpoint for blocking a user"""
    print(f"🚫 Block action for user: {username}")
    
    return jsonify({
        "status": "ok", 
        "message": f"Blocked {username}"
    })

@app.route("/api/interactions/report", methods=["POST"])
@mock_auth_required
def report_user():
    """Mock endpoint for reporting a user"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Report data required"}), 400
    
    print(f"🚨 Report submitted: {data}")
    
    return jsonify({
        "status": "ok", 
        "message": "Report submitted successfully"
    })

# ========== BROWSING & MATCHING SYSTEM ==========

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in kilometers using Haversine formula"""
    from math import radians, cos, sin, asin, sqrt
    
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r

def is_orientation_compatible(user_gender, user_preferences, target_gender, target_preferences):
    """Check if two users are sexually compatible based on orientation"""
    # Handle bisexual/all preferences
    if user_preferences in ["Both", "All"] or target_preferences in ["Both", "All"]:
        return True
    
    # Handle unspecified preferences (considered bisexual)
    if not user_preferences or not target_preferences:
        return True
        
    # Check compatibility
    user_attracted_to_target = (
        (user_preferences == "Men" and target_gender == "Male") or
        (user_preferences == "Women" and target_gender == "Female") or
        (user_preferences == "All")
    )
    
    target_attracted_to_user = (
        (target_preferences == "Men" and user_gender == "Male") or
        (target_preferences == "Women" and user_gender == "Female") or  
        (target_preferences == "All")
    )
    
    return user_attracted_to_target and target_attracted_to_user

def calculate_common_tags(user_interests, target_interests):
    """Calculate number of common interests between users"""
    if not user_interests or not target_interests:
        return 0
    return len(set(user_interests) & set(target_interests))

def calculate_match_score(current_user, target_user):
    """Calculate overall match score based on multiple factors"""
    score = 0
    
    # Distance factor (closer = higher score, max 40 points)
    user_profile = current_user["profile"]
    target_profile = target_user["profile"]
    
    if user_profile.get("latitude") and user_profile.get("longitude") and \
       target_profile.get("latitude") and target_profile.get("longitude"):
        distance = calculate_distance(
            user_profile["latitude"], user_profile["longitude"],
            target_profile["latitude"], target_profile["longitude"]
        )
        # Closer users get higher scores (max 40 points for same location)
        distance_score = max(0, 40 - (distance * 2))
        score += distance_score
    
    # Common interests factor (max 30 points)
    common_tags = calculate_common_tags(
        current_user.get("interests", []),
        target_user.get("interests", [])
    )
    interest_score = min(30, common_tags * 6)  # 6 points per common interest
    score += interest_score
    
    # Fame rating factor (max 30 points)
    fame_score = min(30, target_profile.get("fame_rating", 50) * 0.3)
    score += fame_score
    
    return round(score, 1)

@app.route("/api/browse/suggestions", methods=["GET"])
@mock_auth_required
def get_suggestions():
    """Get personalized user suggestions based on matching criteria"""
    
    # Get query parameters for filtering and sorting
    min_age = request.args.get('min_age', type=int)
    max_age = request.args.get('max_age', type=int)  
    max_distance = request.args.get('max_distance', type=float, default=100.0)
    min_fame = request.args.get('min_fame', type=int)
    max_fame = request.args.get('max_fame', type=int)
    common_tags = request.args.get('common_tags', '').split(',') if request.args.get('common_tags') else []
    sort_by = request.args.get('sort_by', 'match_score')  # match_score, age, distance, fame_rating, common_tags
    sort_order = request.args.get('sort_order', 'desc')  # asc, desc
    
    current_user = mock_users["test_user"]
    current_profile = current_user["profile"]
    
    suggestions = []
    
    # Process all other users
    for username, user in mock_users.items():
        if username == "test_user":  # Skip self
            continue
            
        target_profile = user["profile"]
        
        # 1. Check sexual orientation compatibility
        if not is_orientation_compatible(
            current_profile.get("gender", ""),
            current_profile.get("sexual_preferences", ""),
            target_profile.get("gender", ""),
            target_profile.get("sexual_preferences", "")
        ):
            continue
            
        # 2. Apply age filter
        if min_age and target_profile.get("age", 0) < min_age:
            continue
        if max_age and target_profile.get("age", 0) > max_age:
            continue
            
        # 3. Apply fame rating filter  
        if min_fame and target_profile.get("fame_rating", 0) < min_fame:
            continue
        if max_fame and target_profile.get("fame_rating", 0) > max_fame:
            continue
            
        # 4. Calculate distance and apply distance filter
        distance = None
        if current_profile.get("latitude") and current_profile.get("longitude") and \
           target_profile.get("latitude") and target_profile.get("longitude"):
            distance = calculate_distance(
                current_profile["latitude"], current_profile["longitude"],
                target_profile["latitude"], target_profile["longitude"]
            )
            if distance > max_distance:
                continue
        
        # 5. Apply common tags filter
        user_common_tags = calculate_common_tags(
            current_user.get("interests", []),
            user.get("interests", [])
        )
        if common_tags and not any(tag in user.get("interests", []) for tag in common_tags):
            continue
            
        # 6. Calculate match score
        match_score = calculate_match_score(current_user, user)
        
        # Build suggestion object
        suggestion = {
            "username": username,
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "age": target_profile.get("age"),
            "gender": target_profile.get("gender"),
            "bio": target_profile.get("bio"),
            "city": target_profile.get("city"),
            "country": target_profile.get("country"),
            "fame_rating": target_profile.get("fame_rating"),
            "interests": user.get("interests", []),
            "profile_picture": user.get("profile_picture"),
            "images": user.get("images", []),
            "distance": round(distance, 1) if distance else None,
            "common_interests": user_common_tags,
            "match_score": match_score,
            "compatibility_reasons": []
        }
        
        # Add compatibility reasons for better UX
        if distance and distance < 10:
            suggestion["compatibility_reasons"].append("Very close location")
        elif distance and distance < 50:
            suggestion["compatibility_reasons"].append("Same area")
            
        if user_common_tags >= 3:
            suggestion["compatibility_reasons"].append("Many shared interests")
        elif user_common_tags >= 1:
            suggestion["compatibility_reasons"].append("Some shared interests")
            
        if target_profile.get("fame_rating", 0) >= 90:
            suggestion["compatibility_reasons"].append("High fame rating")
            
        suggestions.append(suggestion)
    
    # 7. Sort suggestions
    reverse_sort = sort_order == 'desc'
    
    if sort_by == 'age':
        suggestions.sort(key=lambda x: x['age'] or 0, reverse=reverse_sort)
    elif sort_by == 'distance':
        suggestions.sort(key=lambda x: x['distance'] or float('inf'), reverse=reverse_sort)
    elif sort_by == 'fame_rating':
        suggestions.sort(key=lambda x: x['fame_rating'] or 0, reverse=reverse_sort)
    elif sort_by == 'common_tags':
        suggestions.sort(key=lambda x: x['common_interests'], reverse=reverse_sort)
    else:  # default: match_score
        suggestions.sort(key=lambda x: x['match_score'], reverse=reverse_sort)
    
    print(f"🔍 Generated {len(suggestions)} suggestions with filters: age({min_age}-{max_age}), distance(<{max_distance}km), fame({min_fame}-{max_fame}), sort_by({sort_by})")
    
    return jsonify({
        "status": "ok",
        "suggestions": suggestions,
        "total": len(suggestions),
        "filters_applied": {
            "min_age": min_age,
            "max_age": max_age, 
            "max_distance": max_distance,
            "min_fame": min_fame,
            "max_fame": max_fame,
            "common_tags": common_tags,
            "sort_by": sort_by,
            "sort_order": sort_order
        }
    })

@app.route("/api/browse/filters", methods=["GET"])
@mock_auth_required 
def get_filter_options():
    """Get available filter options for browsing"""
    
    # Calculate ranges from all users
    ages = [user["profile"].get("age", 0) for user in mock_users.values() if user.get("profile")]
    fame_ratings = [user["profile"].get("fame_rating", 0) for user in mock_users.values() if user.get("profile")]
    all_interests = set()
    cities = set()
    
    for user in mock_users.values():
        if user.get("interests"):
            all_interests.update(user["interests"])
        if user.get("profile", {}).get("city"):
            cities.add(user["profile"]["city"])
    
    return jsonify({
        "age_range": {
            "min": min(ages) if ages else 18,
            "max": max(ages) if ages else 100
        },
        "fame_rating_range": {
            "min": min(fame_ratings) if fame_ratings else 0,
            "max": max(fame_ratings) if fame_ratings else 100
        },
        "available_interests": sorted(list(all_interests)),
        "available_cities": sorted(list(cities)),
        "sort_options": [
            {"value": "match_score", "label": "Best Match"},
            {"value": "distance", "label": "Distance"}, 
            {"value": "age", "label": "Age"},
            {"value": "fame_rating", "label": "Fame Rating"},
            {"value": "common_tags", "label": "Common Interests"}
        ]
    })

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
        "endpoints": {
            "Profile Management": [
                "GET /api/profile/my_profile",
                "GET /api/profile/get_profile/me",
                "POST /api/profile/update_profile",
                "GET /api/profile/get_fame_rating"
            ],
            "Photo Management": [
                "POST /api/profile/upload_images",
                "DELETE /api/profile/delete_image",
                "GET /api/profile/get_images/<username>", 
                "GET /api/profile/get_profile_pic/<username>"
            ],
            "Location & GPS": [
                "POST /api/profile/set_location"
            ],
            "Interests/Tags": [
                "GET /api/profile/get_user_tags",
                "POST /api/profile/add_tags"
            ],
            "Social Features": [
                "GET /api/profile/get_profile_vistors",
                "GET /api/interactions/who_liked_me",
                "GET /api/interactions/my_connections"
            ],
            "Interactions": [
                "POST /api/interactions/like/<username>",
                "POST /api/interactions/unlike/<username>",
                "POST /api/interactions/block/<username>",
                "POST /api/interactions/report"
            ],
            "Browsing & Matching": [
                "GET /api/browse/suggestions",
                "GET /api/browse/filters"
            ]
        },
        "features_implemented": {
            "profile_creation": True,
            "photo_upload_up_to_5": True,
            "profile_picture_management": True,
            "gps_positioning": True,
            "location_modification": True,
            "interest_tags": True,
            "fame_rating": True,
            "profile_views_tracking": True,
            "likes_tracking": True,
            "user_blocking": True,
            "user_reporting": True,
            "profile_modification": True,
            "smart_matching_algorithm": True,
            "sexual_orientation_filtering": True,
            "geographic_prioritization": True,
            "common_interests_matching": True,
            "fame_rating_consideration": True,
            "advanced_filtering": True,
            "multiple_sorting_options": True
        }
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use environment variable or default to 5000
    print("🚀 Starting Mock Matcha Backend Server...")
    print("📁 Upload folder:", os.path.abspath(UPLOAD_FOLDER))
    print("🌐 CORS enabled for http://localhost:3000")
    print(f"🔗 Health check: http://localhost:{port}/")
    print(f"🌟 Running on port {port}")
    print("=" * 50)
    
    app.run(host="0.0.0.0", port=port, debug=False)