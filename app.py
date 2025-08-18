import database.connection as db
from flask import Flask
import os

app = Flask(__name__)
db.get_connection()

@app.route('/')
def index():
    return "Welcome to the Matcha API!"



if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)