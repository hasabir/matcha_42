#!/usr/bin/env python3
"""
Migration script to fix profile picture paths in the database.
Fixes:
1. /static/static/ -> /static/
2. /pofile_picture/ -> /profile_picture/
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database.connection as connection
from database.crud.profile_crud import Profile

def fix_profile_picture_paths():
    """Fix all profile picture paths in the database."""
    try:
        pool = connection.get_connection()
        profile_crud = Profile(pool)
        
        # Get all profiles
        profiles = profile_crud.get_all_profiles()
        
        if not profiles:
            print("No profiles found in database.")
            return
        
        fixed_count = 0
        for profile in profiles:
            user_id = profile.get('user_id')
            pic_path = profile.get('profile_picture')
            
            if not pic_path:
                continue
            
            original_path = pic_path
            modified = False
            
            # Fix double /static/
            if '/static/static/' in pic_path:
                pic_path = pic_path.replace('/static/static/', '/static/')
                modified = True
                print(f"User {user_id}: Fixed double /static/")
            
            # Fix typo in folder name
            if '/pofile_picture/' in pic_path:
                pic_path = pic_path.replace('/pofile_picture/', '/profile_picture/')
                modified = True
                print(f"User {user_id}: Fixed folder name typo")
            
            if modified:
                profile_crud.update_profile(user_id, {'profile_picture': pic_path})
                print(f"User {user_id}: Updated path")
                print(f"  FROM: {original_path}")
                print(f"  TO:   {pic_path}")
                fixed_count += 1
        
        print(f"\n✅ Migration complete! Fixed {fixed_count} profile picture paths.")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if pool:
            pool.closeall()

if __name__ == '__main__':
    print("Starting profile picture path migration...")
    print("-" * 60)
    fix_profile_picture_paths()
