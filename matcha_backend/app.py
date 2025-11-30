from gevent import monkey
monkey.patch_all()

import database.connection as connection
from database.create_tables import create_tables
from flask import Flask, g, request, jsonify
import os
import sys
import threading
import time
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env file
load_dotenv()

from utils.socket_events import register_socket_events
from utils.config_manager import ConfigManager
from flask_cors import CORS 
from src.auth import auth_bp
from src.user_profile import profile_bp
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from src.search import search_bp
from src.browse import browse_bp
from src.interactions import interactions_bp
from src.chat import chat_bp
from src.notifications import notifications_bp
from src.chat.events_chat import register_chat_socket_events
from docs import docs_bp
from flask_socketio import SocketIO
from utils.redis_manager import redis_manager
from utils.notification_worker import process_notifications





if __name__ == '__main__':
    app = Flask(__name__)
    
    # Load configuration
    config = ConfigManager('build/config.yml')
    app_config = config.load_config('build/config.yml')
    app.config.update(app_config)
    
    # Check email mode
    use_console_email = os.environ.get('MAIL_USE_CONSOLE', 'false').lower() == 'true'
    if use_console_email:
        print("=" * 80)
        print("📧 CONSOLE EMAIL MODE ENABLED")
        print("   Verification emails will print to this terminal")
        print("   No SMTP configuration needed for testing")
        print("=" * 80)
    
    # Override email settings from environment variables
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 465))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'false').lower() == 'true'
    app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'true').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', app.config.get('MAIL_USERNAME', ''))
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', app.config.get('MAIL_PASSWORD', ''))
    
    # Add SMTP timeout to prevent hanging (10 seconds)
    app.config['MAIL_DEFAULT_TIMEOUT'] = 10
    app.config['MAIL_MAX_EMAILS'] = None
    app.config['MAIL_ASCII_ATTACHMENTS'] = False
    
    # Set up configs
    app.config['BCRYPT'] = Bcrypt(app)
    app.config['JWT_ACCESS_TOKEN'] = os.environ.get('JWT_ACCESS_TOKEN')
    app.config['JWT_REFRESH_TOKEN'] = os.environ.get('JWT_REFRESH_TOKEN')
    app.config['SMTP_SECRET_KEY'] = os.environ.get("SMTP_SECRET_KEY")
    app.config['REDIS_HOST'] = os.environ.get('REDIS_HOST', 'redis')
    app.config['REDIS_PORT'] = int(os.environ.get('REDIS_PORT', 6379))
    app.config['REDIS_DB'] = int(os.environ.get('REDIS_DB', 0))
    
    # Initialize Mail
    mail = Mail(app)
    
    # Initialize Redis Manager
    redis_manager.init_app(app)
    
    # Create ONLY ONE SocketIO instance with proper configuration
    socketio = SocketIO(
        app, 
        cors_allowed_origins="*",
        message_queue=f"redis://{app.config['REDIS_HOST']}:{app.config['REDIS_PORT']}/{app.config['REDIS_DB']}",
        async_mode='gevent',
        # Add ping configuration to keep connections alive
        ping_interval=25,  # Send ping every 25 seconds
        ping_timeout=60,   # Wait 60 seconds for pong before disconnecting
        # Allow reconnections
        allow_upgrades=True,
        # Increase max HTTP buffer size
        max_http_buffer_size=1e8,
        # Log level for debugging
        logger=True,
        engineio_logger=True
    )
    
    app.config["SOCKETIO"] = socketio
    
    # Register socket events
    register_socket_events(socketio)
    register_chat_socket_events(socketio)
    
    # Enable CORS for local dev (frontend @ 3000)
    CORS(
        app,
        supports_credentials=True,
        origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
        allow_headers=["Content-Type", "Authorization"],
        expose_headers=["Content-Type"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    )

    @app.before_request
    def handle_preflight():
        if request.method == 'OPTIONS':
            return ('', 204)

    # Ensure preflight requests succeed quickly
    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get("Origin")
        if origin in {"http://localhost:3000", "http://127.0.0.1:3000"}:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Vary"] = "Origin"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        return response
    
    # Set up database
    connection_pool = connection.get_connection()
    create_tables(connection_pool)
    app.config["CONNECTION_POOL"] = connection_pool
    
    # Clean up any existing connection in g
    with app.app_context():
        conn = getattr(g, '_database_connection', None)
        if conn is not None:
            connection_pool.putconn(conn)
    
    # Start background notification worker
    worker_thread = threading.Thread(
        target=process_notifications,
        args=(socketio, app),
        daemon=True
    )
    worker_thread.start()
    print("✅ Notification worker started")
    
    # Register blueprints
    app.register_blueprint(docs_bp, url_prefix='/api/docs')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(profile_bp, url_prefix='/api/profile')
    app.register_blueprint(search_bp, url_prefix='/api/search')
    app.register_blueprint(browse_bp, url_prefix='/api/browse')
    app.register_blueprint(interactions_bp, url_prefix='/api/interactions')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
    
    # Admin endpoint for one-time migration
    @app.route('/api/admin/normalize_profiles', methods=['POST'])
    def normalize_profiles():
        """Normalize gender and sexual preferences in all profiles"""
        try:
            from database.crud.profile_crud import Profile
            profile_crud = Profile(app.config['CONNECTION_POOL'])
            
            # Mapping dictionaries
            GENDER_MAP = {
                'Male': 'male', 'Female': 'female', 'Non-binary': 'other',
                'Nonbinary': 'other', 'Other': 'other',
                'male': 'male', 'female': 'female', 'other': 'other'
            }
            PREFERENCE_MAP = {
                'Men': 'male', 'Man': 'male', 'Male': 'male',
                'Women': 'female', 'Woman': 'female', 'Female': 'female',
                'Both': 'both', 'All': 'both', 'Everyone': 'both', 'Bisexual': 'both',
                'male': 'male', 'female': 'female', 'both': 'both'
            }
            
            conn = app.config['CONNECTION_POOL'].getconn()
            cur = conn.cursor()
            
            # Get all profiles
            cur.execute("""
                SELECT p.profile_id, p.user_id, u.username, 
                       p.gender, p.sexual_preferences
                FROM profiles p
                JOIN users u ON p.user_id = u.id
            """)
            
            profiles = cur.fetchall()
            updates = []
            updated_count = 0
            
            for row in profiles:
                profile_id, user_id, username, current_gender, current_pref = row
                
                new_gender = GENDER_MAP.get(current_gender, current_gender)
                new_pref = PREFERENCE_MAP.get(current_pref, current_pref)
                
                if current_gender != new_gender or current_pref != new_pref:
                    cur.execute("""
                        UPDATE profiles
                        SET gender = %s, sexual_preferences = %s
                        WHERE profile_id = %s
                    """, (new_gender, new_pref, profile_id))
                    
                    updates.append(f"{username}: {current_gender}→{new_gender}, {current_pref}→{new_pref}")
                    updated_count += 1
            
            conn.commit()
            app.config['CONNECTION_POOL'].putconn(conn)
            
            return jsonify({
                'status': 'success',
                'checked': len(profiles),
                'updated': updated_count,
                'updates': updates
            }), 200
            
        except Exception as e:
            logging.exception("Error normalizing profiles")
            return jsonify({'error': str(e)}), 500
    
    # Run the app with SocketIO (ONLY THIS LINE)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)