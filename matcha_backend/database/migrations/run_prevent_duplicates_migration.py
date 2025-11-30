#!/usr/bin/env python3
"""
Migration script to prevent duplicate profile view notifications
"""
import psycopg2
from psycopg2 import pool
import os
import sys
import yaml

def run_migration():
    """Run the prevent duplicate notifications migration"""
    # Load config from YAML
    config_path = os.path.join(
        os.path.dirname(__file__),
        '../../build/config.yml'
    )
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    try:
        # Create connection pool
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            1, 10,
            user=config.get("database", {}).get("user"),
            password=config.get("database", {}).get("password"),
            host=config.get("database", {}).get("host"),
            port=config.get("database", {}).get("port"),
            database=config.get("database", {}).get("name")
        )
        
        if not connection_pool:
            print("❌ Failed to create connection pool")
            return False
        
        # Get connection
        conn = connection_pool.getconn()
        cursor = conn.cursor()
        
        print("🔄 Running migration: Prevent duplicate notifications...")
        
        # Read migration SQL
        migration_path = os.path.join(
            os.path.dirname(__file__),
            'prevent_duplicate_notifications.sql'
        )
        
        with open(migration_path, 'r') as f:
            migration_sql = f.read()
        
        # Execute migration
        cursor.execute(migration_sql)
        conn.commit()
        
        print("✅ Migration completed successfully!")
        print("   - Created partial unique index on notifications table")
        print("   - Duplicate unseen profile_view notifications will now be prevented")
        
        # Clean up
        cursor.close()
        connection_pool.putconn(conn)
        connection_pool.closeall()
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        if conn:
            conn.rollback()
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
