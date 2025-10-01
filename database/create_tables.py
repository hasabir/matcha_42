import psycopg2
import os

def create_tables(connection_pool):
    connection = None
    
    try:
        # Get connection from pool
        connection = connection_pool.getconn()
        cursor = connection.cursor()
        
        # Read schema file
        schema_file = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_file, 'r') as file:
            schema = file.read()
        
        # Execute schema
        cursor.execute(schema)
        connection.commit()  # Fixed: commit on connection, not cursor
        print("Tables created successfully.")
        
    except Exception as e:
        print(f"Error creating tables: {e}")
        if connection:
            connection.rollback()
    finally:
        # Return connection to pool
        if connection:
            connection_pool.putconn(connection)