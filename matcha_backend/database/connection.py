"""
Database connection module for PostgreSQL
Handles connection pool management
"""
import os
import psycopg2
from psycopg2 import pool
import logging

logger = logging.getLogger(__name__)

# Global connection pool
connection_pool = None


def get_connection():
    """
    Get or create a PostgreSQL connection pool
    
    Returns:
        psycopg2.pool.SimpleConnectionPool: Database connection pool
    
    Raises:
        Exception: If database connection fails
    """
    global connection_pool
    
    if connection_pool is not None:
        return connection_pool
    
    try:
        # Get database credentials from environment variables
        db_host = os.environ.get('DB_HOST', 'localhost')
        db_port = os.environ.get('DB_PORT', '5432')
        db_name = os.environ.get('DB_NAME', 'matcha')
        db_user = os.environ.get('DB_USER', 'postgres')
        db_password = os.environ.get('DB_PASSWORD', 'postgres')
        
        # Create connection pool
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=20,
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        
        if connection_pool:
            logger.info(f"✅ Database connection pool created successfully (host: {db_host}, db: {db_name})")
            return connection_pool
        else:
            raise Exception("Failed to create connection pool")
            
    except psycopg2.OperationalError as e:
        logger.error(f"❌ Database connection error: {str(e)}")
        raise Exception(f"Could not connect to database: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Unexpected error creating connection pool: {str(e)}")
        raise


def get_db_connection():
    """
    Get a single connection from the pool
    
    Returns:
        psycopg2.connection: Database connection
    """
    global connection_pool
    
    if connection_pool is None:
        connection_pool = get_connection()
    
    try:
        return connection_pool.getconn()
    except Exception as e:
        logger.error(f"Error getting connection from pool: {str(e)}")
        raise


def return_db_connection(connection):
    """
    Return a connection to the pool
    
    Args:
        connection: Database connection to return
    """
    global connection_pool
    
    if connection_pool and connection:
        try:
            connection_pool.putconn(connection)
        except Exception as e:
            logger.error(f"Error returning connection to pool: {str(e)}")


def close_all_connections():
    """
    Close all connections in the pool
    """
    global connection_pool
    
    if connection_pool:
        try:
            connection_pool.closeall()
            logger.info("All database connections closed")
            connection_pool = None
        except Exception as e:
            logger.error(f"Error closing connections: {str(e)}")
