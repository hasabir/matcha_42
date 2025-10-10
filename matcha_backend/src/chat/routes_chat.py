import os
import sys
import logging

from flask import Blueprint, flash, render_template, request, jsonify, current_app, g, send_file, url_for
from werkzeug.exceptions import BadRequestKeyError

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../../')))

from database.crud.matching_operations_crud import Matching
from database.crud.user_crud import User
from database.crud.profile_crud import Profile
from database.crud.interactions_crud import Interactions
from utils.validate_profile_data import validate_profile_data
from utils.security import auth_guard
from utils.fame_rating import calculate_fame_rating
from utils.manage_interactions import ManageInteractions
from utils.image_handler import upload_pictures
from src.chat import chat_bp



@chat_bp.route('/', methods=['GET'])
def chat_home():
    return render_template('home.html')