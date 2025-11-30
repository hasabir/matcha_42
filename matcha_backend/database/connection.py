"""
Database connection module for PostgreSQL
Handles connection pool management
"""
import os
import psycopg2
from psycopg2 import pool
import logging
import time

logger = logging.getLogger(__name__)

# Global connection pool
connection_pool = None


def get_connection():
    """
    Get or create a PostgreSQL connection pool with retry logic
    
    Returns:
        psycopg2.pool.SimpleConnectionPool: Database connection pool
    
    Raises:
        Exception: If database connection fails after all retries
    """
    global connection_pool
    
    if connection_pool is not None:
        return connection_pool
    
    # Get database credentials from environment variables
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = os.environ.get('DB_PORT', '5432')
    db_name = os.environ.get('DB_NAME', 'db')
    db_user = os.environ.get('DB_USER', 'admin')
    db_password = os.environ.get('DB_PASSWORD', 'admin')
    
    # Retry logic for Docker container startup
    max_retries = 30
    retry_delay = 2  # seconds
    
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"🔄 Attempting to connect to database (attempt {attempt}/{max_retries})...")
            
            # Create connection pool
            connection_pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=20,
                host=db_host,
                port=db_port,
                database=db_name,
                user=db_user,
                password=db_password,
                connect_timeout=5
            )
            
            if connection_pool:
                logger.info(f"✅ Database connection pool created successfully (host: {db_host}, db: {db_name})")
                return connection_pool
            else:
                raise Exception("Failed to create connection pool")
                
        except psycopg2.OperationalError as e:
            error_msg = str(e)
            
            # Check if it's a DNS resolution error or connection refused
            if "could not translate host name" in error_msg or "Name or service not known" in error_msg:
                logger.warning(f"⏳ DNS resolution failed for host '{db_host}' (attempt {attempt}/{max_retries}). Retrying in {retry_delay}s...")
            elif "Connection refused" in error_msg:
                logger.warning(f"⏳ Database not ready yet (attempt {attempt}/{max_retries}). Retrying in {retry_delay}s...")
            else:
                logger.warning(f"⏳ Database connection error: {error_msg} (attempt {attempt}/{max_retries}). Retrying in {retry_delay}s...")
            
            if attempt < max_retries:
                time.sleep(retry_delay)
            else:
                logger.error(f"❌ Database connection failed after {max_retries} attempts")
                raise Exception(f"Could not connect to database after {max_retries} attempts: {str(e)}")
                
        except Exception as e:
            logger.error(f"❌ Unexpected error creating connection pool: {str(e)}")
            if attempt < max_retries:
                logger.warning(f"⏳ Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
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
