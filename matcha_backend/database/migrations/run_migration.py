#!/usr/bin/env python3
"""
Database Migration Script
Adds matches_count column to profiles table if it doesn't exist
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from database.connection import get_connection

def run_migration():
    """Add matches_count column to profiles table"""
    pool = get_connection()
    conn = pool.getconn()
    cur = conn.cursor()
    
    try:
        print("🔄 Running migration: Add matches_count column...")
        
        # Add matches_count column if it doesn't exist
        cur.execute("""
            ALTER TABLE profiles 
            ADD COLUMN IF NOT EXISTS matches_count INTEGER DEFAULT 0;
        """)
        conn.commit()
        print("✅ matches_count column added successfully")
        
        # Verify the column exists
        cur.execute("""
            SELECT column_name, data_type, column_default 
            FROM information_schema.columns 
            WHERE table_name='profiles' AND column_name='matches_count';
        """)
        result = cur.fetchone()
        
        if result:
            print(f"✅ Verified: Column '{result[0]}' exists with type '{result[1]}' and default '{result[2]}'")
        else:
            print("❌ ERROR: Column was not created!")
            return False
            
        # Show current columns in profiles table
        print("\n📋 Current columns in profiles table:")
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name='profiles'
            ORDER BY ordinal_position;
        """)
        columns = cur.fetchall()
        for col in columns:
            print(f"   - {col[0]}: {col[1]}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error running migration: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        pool.putconn(conn)

if __name__ == "__main__":
    success = run_migration()
    if success:
        print("\n🎉 Migration completed successfully!")
        print("👉 You can now restart the backend: ./restart_backend.sh")
        sys.exit(0)
    else:
        print("\n💥 Migration failed!")
        sys.exit(1)
