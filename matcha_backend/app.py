from gevent import monkey
monkey.patch_all()

import database.connection as connection
from database.create_tables import create_tables
from flask import Flask, g
import os
import sys
import threading
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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
from src.chat.events_chat import register_chat_events
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
    
    # Create ONLY ONE SocketIO instance
    socketio = SocketIO(
        app, 
        cors_allowed_origins="*",
        message_queue=f"redis://{app.config['REDIS_HOST']}:{app.config['REDIS_PORT']}/{app.config['REDIS_DB']}",
        async_mode='gevent'
    )
    
    app.config["SOCKETIO"] = socketio
    
    # Register socket events
    register_socket_events(socketio)
    register_chat_events(socketio)
    
    # Enable CORS
    CORS(app, 
        supports_credentials=True,
        origins=["http://localhost:3000"],
        allow_headers=["Content-Type", "Authorization"],
        expose_headers=["Content-Type"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )
    
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
    
    # Run the app with SocketIO (ONLY THIS LINE)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)