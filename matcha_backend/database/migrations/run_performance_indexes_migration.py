#!/usr/bin/env python3
"""
Migration script to add performance indexes for the matching algorithm.
Run this script to optimize database queries for browse/suggestions endpoint.
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from database.connection import get_connection_pool
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_migration():
    """Add performance indexes to optimize matching queries"""
    logger.info("🚀 Starting performance indexes migration...")
    
    connection_pool = get_connection_pool()
    if not connection_pool:
        logger.error("❌ Failed to get database connection pool")
        return False
    
    try:
        with connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                # Read the migration SQL file
                migration_file = os.path.join(
                    os.path.dirname(__file__),
                    'add_performance_indexes.sql'
                )
                
                logger.info(f"📄 Reading migration file: {migration_file}")
                with open(migration_file, 'r') as f:
                    sql_script = f.read()
                
                # Execute the migration
                logger.info("⚙️  Executing migration...")
                cursor.execute(sql_script)
                conn.commit()
                
                logger.info("✅ Performance indexes migration completed successfully!")
                
                # Verify indexes were created
                cursor.execute("""
                    SELECT indexname 
                    FROM pg_indexes 
                    WHERE tablename IN ('profiles', 'user_locations')
                    ORDER BY indexname;
                """)
                indexes = cursor.fetchall()
                
                logger.info(f"📊 Current indexes on profiles and user_locations tables:")
                for idx in indexes:
                    logger.info(f"   - {idx['indexname']}")
                
                return True
                
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
