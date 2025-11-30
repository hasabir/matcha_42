#!/usr/bin/env python3
"""
Migration to normalize country names in user_locations table
Maps local language names (like 'maroc') to standard English names (like 'Morocco')
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from database.connection import get_connection
from utils.ip_geolocation import normalize_country_name

def normalize_existing_countries():
    """Normalize all country names in the database"""
    conn = None
    try:
        pool = get_connection()
        conn = pool.getconn()
        cur = conn.cursor()
        
        print("🔄 Starting country name normalization...")
        
        # Get all unique countries
        cur.execute("SELECT DISTINCT country FROM user_locations WHERE country IS NOT NULL")
        countries = cur.fetchall()
        
        print(f"📊 Found {len(countries)} unique country names")
        
        # Track changes
        changes_made = 0
        
        for (old_country,) in countries:
            new_country = normalize_country_name(old_country)
            
            if old_country != new_country:
                print(f"   '{old_country}' -> '{new_country}'")
                
                # Update all records with this country name
                cur.execute(
                    "UPDATE user_locations SET country = %s WHERE country = %s",
                    (new_country, old_country)
                )
                
                changes_made += cur.rowcount
                print(f"   ✅ Updated {cur.rowcount} records")
            else:
                print(f"   ✓ '{old_country}' already normalized")
        
        conn.commit()
        
        print(f"\n✅ Migration completed successfully!")
        print(f"   Total records updated: {changes_made}")
        
        # Show final state
        print("\n📋 Current country names in database:")
        cur.execute("SELECT DISTINCT country FROM user_locations WHERE country IS NOT NULL ORDER BY country")
        for (country,) in cur.fetchall():
            print(f"   - {country}")
        
        cur.close()
        pool.putconn(conn)
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if conn:
            conn.rollback()
        raise

if __name__ == "__main__":
    normalize_existing_countries()
