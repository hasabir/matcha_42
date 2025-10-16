"""
Database table creation module
Initializes the database schema from schema.sql
"""
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def create_tables(connection_pool):
    """
    Create all database tables from schema.sql
    
    Args:
        connection_pool: PostgreSQL connection pool
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not connection_pool:
        logger.error("❌ No connection pool provided")
        return False
    
    conn = None
    try:
        # Get connection from pool
        conn = connection_pool.getconn()
        cursor = conn.cursor()
        
        # Get the schema.sql file path
        current_dir = Path(__file__).parent
        schema_file = current_dir / 'schema.sql'
        
        if not schema_file.exists():
            logger.error(f"❌ Schema file not found at: {schema_file}")
            return False
        
        # Read and execute schema.sql
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        # Execute the schema
        cursor.execute(schema_sql)
        conn.commit()
        
        logger.info("✅ Database tables created successfully")
        
        cursor.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating tables: {str(e)}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        # Return connection to pool
        if conn and connection_pool:
            try:
                connection_pool.putconn(conn)
            except Exception as e:
                logger.error(f"Error returning connection to pool: {str(e)}")


def drop_all_tables(connection_pool):
    """
    Drop all tables (use with caution!)
    
    Args:
        connection_pool: PostgreSQL connection pool
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not connection_pool:
        logger.error("❌ No connection pool provided")
        return False
    
    conn = None
    try:
        conn = connection_pool.getconn()
        cursor = conn.cursor()
        
        # List of tables to drop in order (respecting foreign keys)
        tables = [
            'notifications', 'messages', 'conversations', 'reports', 'blocks',
            'visits', 'connections', 'likes', 'user_tags', 'tags', 'images',
            'profiles', 'user_locations', 'users'
        ]
        
        for table in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
        
        conn.commit()
        logger.info("✅ All tables dropped successfully")
        
        cursor.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error dropping tables: {str(e)}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        if conn and connection_pool:
            try:
                connection_pool.putconn(conn)
            except Exception as e:
                logger.error(f"Error returning connection to pool: {str(e)}")


def reset_database(connection_pool):
    """
    Drop all tables and recreate them (use with caution!)
    
    Args:
        connection_pool: PostgreSQL connection pool
    
    Returns:
        bool: True if successful, False otherwise
    """
    logger.warning("⚠️  Resetting database - all data will be lost!")
    
    if drop_all_tables(connection_pool):
        return create_tables(connection_pool)
    return False
