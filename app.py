import database.connection as connection
from database.create_tables import create_tables
from flask import Flask
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.config_manager import ConfigManager


app = Flask(__name__)


# current_file_dir = os.path.dirname(os.path.abspath(__file__))
# config_file_path = "build/config.yml"
# config = ConfigManager(config_file_path)


# print(f"------> Config loaded from {config_file_path}")
connection_pool = connection.get_connection()
create_tables(connection_pool)
print("------> Tables created successfully")

@app.teardown_appcontext
def close_pool(exception=None):
    if connection_pool:
        connection_pool.closeall()


@app.route('/')
def index():
    return "Welcome to the Matcha API!"



if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)