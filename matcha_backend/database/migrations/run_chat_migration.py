#!/usr/bin/env python3
import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from database.connection import get_connection

def run_migration():
    """Run the is_read migration"""
    conn = None
    try:
        pool = get_connection()
        conn = pool.getconn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Read and execute migration file
        migration_file = os.path.join(os.path.dirname(__file__), 'add_is_read_to_messages.sql')
        with open(migration_file, 'r') as f:
            sql = f.read()
            cur.execute(sql)
        
        conn.commit()
        print("✅ Migration completed successfully!")
        print("   - Added is_read column to messages table")
        print("   - Added status column to messages table")
        print("   - Created user_online_status table")
        print("   - Created typing_status table")
        
        cur.close()
        pool.putconn(conn)
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if conn:
            conn.rollback()
        raise

if __name__ == "__main__":
    run_migration()
