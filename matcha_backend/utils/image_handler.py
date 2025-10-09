from werkzeug.utils import secure_filename
import os





def check_allowed_file(filename):
    alload_extentions = {'png', 'jpg', 'jpeg'}
    if not( '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in alload_extentions):
        if '.' in filename and \
           filename.rsplit('.', 1)[1].lower() == "php":
            raise Exception("Unsupported type! But \"php\"? seriously?!")
        raise Exception("Unsupported type")




def upload_pictures(requested_file, user_id, is_profile_picture=True):
    try:
        # if (not requested_file\
        #     or requested_file.filename == '')\
        #     and is_profile_picture:
        #     return "profiles/default_profile.jpg"
        if is_profile_picture:
            user_folder = f"profiles/{user_id}/profile_picture/"
        else:
            user_folder = f"profiles/{user_id}/images"
        file_name = requested_file.filename
        check_allowed_file(filename=file_name)
        filename = secure_filename(file_name)
        # Create full path for saving
        full_path = os.path.join("static", user_folder)
        os.makedirs(full_path, exist_ok=True)
        file_path = os.path.join(full_path, filename)
        requested_file.save(file_path)
        # Return path relative to static folder (without 'static/' prefix)
        return os.path.join(user_folder, filename)
    except Exception as e:
        raise Exception(e)

