#!/usr/bin/env python3
"""
Migration runner for adding neighborhood field to user_locations table
Run this to add neighborhood-level GPS positioning support
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import database.connection as connection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_neighborhood_migration():
    """Execute the neighborhood field migration"""
    try:
        # Get database connection
        conn_pool = connection.get_connection()
        conn = conn_pool.getconn()
        cursor = conn.cursor()
        
        logger.info("Starting neighborhood field migration...")
        
        # Read migration SQL file
        migration_file = os.path.join(os.path.dirname(__file__), 'add_neighborhood_field.sql')
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        # Execute migration
        cursor.execute(migration_sql)
        conn.commit()
        
        logger.info("✅ Successfully added neighborhood field to user_locations table")
        
        # Verify the column was added
        cursor.execute("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_name = 'user_locations' AND column_name = 'neighborhood'
        """)
        
        result = cursor.fetchone()
        if result:
            logger.info(f"✅ Verified: neighborhood column exists - {result}")
        else:
            logger.warning("⚠️ Warning: Could not verify neighborhood column")
        
        cursor.close()
        conn_pool.putconn(conn)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        if 'conn' in locals():
            conn.rollback()
            cursor.close()
            conn_pool.putconn(conn)
        return False

if __name__ == '__main__':
    success = run_neighborhood_migration()
    sys.exit(0 if success else 1)
