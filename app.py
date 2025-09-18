import database.connection as connection
from database.create_tables import create_tables
from flask import Flask, g
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.config_manager import ConfigManager
from flask_cors import CORS 
from src.auth import auth_bp
from src.user_profile import profile_bp
from flask_bcrypt import Bcrypt
from flask_mail import Mail
import jwt
# from src.search import search_bp
from src.interactions import interactions_bp
# from src.chat import chat_bp
# from src.notification import notifications_bp
from docs import docs_bp


if __name__ == '__main__':
    app = Flask(__name__)
    config = ConfigManager('build/config.yml')
    app_config = config.load_config('build/config.yml')
    app.config.update(app_config)
    app.config['BCRYPT'] = Bcrypt(app)
    app.config['JWT_ACCESS_TOKEN'] = os.environ.get('JWT_ACCESS_TOKEN')
    app.config['JWT_REFRESH_TOKEN'] = os.environ.get('JWT_REFRESH_TOKEN')
    app.config['SMTP_SECRET_KEY'] = os.environ["SMTP_SECRET_KEY"]
    mail = Mail(app)

    
    CORS(app, 
        supports_credentials=True,  # ← THIS allows cookies to be sent/received
        # origins=['http://localhost:3000'],
        allow_headers=['Authorization', 'Content-Type']  # What headers to accept
    )
    
    connection_pool = connection.get_connection()
    create_tables(connection_pool)
    app.config["CONNECTION_POOL"] = connection_pool
    with app.app_context():
        connection = getattr(g, '_database_connection', None)  # Get connection from 'g'
    if connection is not None:
        connection_pool.putconn(connection)
            
            

    app.register_blueprint(docs_bp, url_prefix='/api/docs')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(profile_bp, url_prefix='/api/profile')
    # app.register_blueprint(search_bp, url_prefix='/api/search')
    app.register_blueprint(interactions_bp, url_prefix='/api/interactions')
    # app.register_blueprint(messaging_bp, url_prefix='/api/chat')
    # app.register_blueprint(notifications_bp, url_prefix='/api/notifications')

    app.run(host='0.0.0.0', port=5000, debug=True)