import psycopg2
import os
from psycopg2 import pool 

def get_connection():
    try:
        print(os.environ.get('DB_USER'), os.environ.get('DB_PASSWORD'), os.environ.get('DB_HOST'), os.environ.get('DB_PORT'), os.environ.get('DB_NAME'))
        connection = pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            user=os.environ.get('DB_USER'),
            password= os.environ.get('DB_PASSWORD'),
            host=os.environ.get('DB_HOST'),
            port=os.environ.get('DB_PORT'),
            database=os.environ.get('DB_NAME')
        )
        print("Database connection established successfully : ", connection)
        return connection
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None