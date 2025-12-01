import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_pictures(file, user_id, is_profile_pic=True):
    """
    Upload and save user pictures
    
    Args:
        file: The file object from request.files
        user_id: The ID of the user uploading the picture
        is_profile_pic: Boolean indicating if this is a profile picture (default: True)
    
    Returns:
        str: The relative path to the saved image
    
    Raises:
        ValueError: If file validation fails
    """
    if not file:
        raise ValueError("No file provided")
    
    if file.filename == '':
        raise ValueError("No file selected")
    
    if not allowed_file(file.filename):
        raise ValueError(f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}")
    
    # Generate unique filename
    filename = secure_filename(file.filename)
    file_ext = filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
    
    # Create user directory if it doesn't exist
    user_dir = os.path.join('profiles', str(user_id))
    full_user_dir = os.path.join('static', user_dir)
    os.makedirs(full_user_dir, exist_ok=True)
    
    # Save file
    file_path = os.path.join(user_dir, unique_filename)
    full_file_path = os.path.join('static', file_path)
    
    try:
        # Validate it's actually an image by opening with PIL
        img = Image.open(file)
        img.verify()
        
        # Reopen and save (verify() closes the file)
        file.seek(0)
        img = Image.open(file)
        
        # Optionally resize large images
        max_dimension = 2000
        if img.width > max_dimension or img.height > max_dimension:
            img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
        
        img.save(full_file_path)
        
    except Exception as e:
        raise ValueError(f"Invalid image file: {str(e)}")
    
    return file_path
