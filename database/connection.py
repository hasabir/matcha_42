import psycopg2
import os


def get_connection():

    try:
        connection = psycopg2.connect(
            user=os.environ.get('DB_USER'),
            password= os.environ.get('DB_PASSWORD'),
            host=os.environ.get('DB_HOST'),
            port=os.environ.get('DB_PORT'),
            database=os.environ.get('DB_NAME')
        )
        return connection
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None