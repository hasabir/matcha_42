#!/usr/bin/env python3
"""
Script to create a complete user profile for testing
This creates:
- User account
- Profile with bio, gender, age, etc.
- Sample interests/tags
- Sample location
- Sample profile picture
"""

import sys
import os
import psycopg2
from psycopg2 import pool
import yaml
from utils.security import SecurityUtils
from datetime import datetime

# Load config
def load_config():
    with open("build/config.yml", "r") as f:
        return yaml.safe_load(f)

def create_connection_pool(config):
    db_config = config['database']
    return psycopg2.pool.SimpleConnectionPool(
        1, 10,
        host=db_config['host'],
        port=db_config['port'],
        database=db_config['dbname'],
        user=db_config['user'],
        password=db_config['password']
    )

def create_user_profile(pool, user_data, profile_data, interests=None, location=None):
    """Create a complete user profile"""
    conn = pool.getconn()
    try:
        cursor = conn.cursor()
        
        # 1. Create user account
        print(f"\n📝 Creating user account: {user_data['username']}...")
        hashed_password = SecurityUtils.password_hash(user_data['password'])
        
        cursor.execute("""
            INSERT INTO users (username, email, password, first_name, last_name, verified, active, first_login)
            VALUES (%s, %s, %s, %s, %s, TRUE, TRUE, FALSE)
            RETURNING id
        """, (
            user_data['username'],
            user_data['email'],
            hashed_password,
            user_data.get('first_name', user_data['username'].capitalize()),
            user_data.get('last_name', 'User')
        ))
        
        user_id = cursor.fetchone()[0]
        print(f"✅ User created with ID: {user_id}")
        
        # 2. Create profile
        print(f"\n👤 Creating profile...")
        cursor.execute("""
            INSERT INTO profiles (user_id, bio, age, gender, sexual_preferences, fame_rating, profile_picture)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING profile_id
        """, (
            user_id,
            profile_data['bio'],
            profile_data['age'],
            profile_data['gender'],
            profile_data['sexual_preferences'],
            profile_data.get('fame_rating', 5),
            profile_data.get('profile_picture', '/static/profiles/default.jpg')
        ))
        
        profile_id = cursor.fetchone()[0]
        print(f"✅ Profile created with ID: {profile_id}")
        
        # 3. Add interests/tags
        if interests:
            print(f"\n🏷️  Adding interests: {', '.join(interests)}...")
            for interest in interests:
                # Insert or get tag
                cursor.execute("""
                    INSERT INTO tags (tag_name) VALUES (%s)
                    ON CONFLICT (tag_name) DO UPDATE SET tag_name = EXCLUDED.tag_name
                    RETURNING tag_id
                """, (interest,))
                tag_id = cursor.fetchone()[0]
                
                # Link to user
                cursor.execute("""
                    INSERT INTO user_tags (user_id, tag_id)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                """, (user_id, tag_id))
            print(f"✅ Added {len(interests)} interests")
        
        # 4. Add location
        if location:
            print(f"\n📍 Setting location...")
            cursor.execute("""
                INSERT INTO user_locations (user_id, latitude, longitude, city, country, accuracy)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE SET
                    latitude = EXCLUDED.latitude,
                    longitude = EXCLUDED.longitude,
                    city = EXCLUDED.city,
                    country = EXCLUDED.country,
                    accuracy = EXCLUDED.accuracy,
                    last_updated = CURRENT_TIMESTAMP
            """, (
                user_id,
                location['latitude'],
                location['longitude'],
                location.get('city', 'Unknown'),
                location.get('country', 'Unknown'),
                location.get('accuracy', 100)
            ))
            print(f"✅ Location set: {location.get('city')}, {location.get('country')}")
        
        conn.commit()
        print(f"\n🎉 Profile created successfully!")
        print(f"   Username: {user_data['username']}")
        print(f"   Email: {user_data['email']}")
        print(f"   Password: {user_data['password']}")
        print(f"   User ID: {user_id}")
        print(f"   Profile ID: {profile_id}")
        
        return user_id, profile_id
        
    except psycopg2.IntegrityError as e:
        conn.rollback()
        print(f"❌ Error: {e}")
        print("   This username or email might already exist.")
        return None, None
    except Exception as e:
        conn.rollback()
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return None, None
    finally:
        cursor.close()
        pool.putconn(conn)


# Predefined sample profiles
SAMPLE_PROFILES = {
    "alice": {
        "user": {
            "username": "alice",
            "email": "alice@example.com",
            "password": "Password123!",
            "first_name": "Alice",
            "last_name": "Johnson"
        },
        "profile": {
            "bio": "Adventure seeker and coffee enthusiast. Love hiking on weekends and trying new restaurants. Looking for someone to share experiences with!",
            "age": 28,
            "gender": "Female",
            "sexual_preferences": "Men",
            "fame_rating": 7
        },
        "interests": ["Hiking", "Travel", "Coffee", "Photography", "Reading"],
        "location": {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "city": "New York",
            "country": "USA",
            "accuracy": 50
        }
    },
    "bob": {
        "user": {
            "username": "bob",
            "email": "bob@example.com",
            "password": "Password123!",
            "first_name": "Bob",
            "last_name": "Smith"
        },
        "profile": {
            "bio": "Tech enthusiast and fitness lover. Passionate about coding and staying active. Always up for a good conversation or a run in the park.",
            "age": 30,
            "gender": "Male",
            "sexual_preferences": "Women",
            "fame_rating": 6
        },
        "interests": ["Coding", "Fitness", "Gaming", "Music", "Travel"],
        "location": {
            "latitude": 34.0522,
            "longitude": -118.2437,
            "city": "Los Angeles",
            "country": "USA",
            "accuracy": 50
        }
    },
    "charlie": {
        "user": {
            "username": "charlie",
            "email": "charlie@example.com",
            "password": "Password123!",
            "first_name": "Charlie",
            "last_name": "Davis"
        },
        "profile": {
            "bio": "Artist and foodie. Love exploring new cuisines and creating art. Looking for someone creative and spontaneous to share life's moments with.",
            "age": 26,
            "gender": "Non-binary",
            "sexual_preferences": "All",
            "fame_rating": 8
        },
        "interests": ["Art", "Cooking", "Music", "Photography", "Travel"],
        "location": {
            "latitude": 51.5074,
            "longitude": -0.1278,
            "city": "London",
            "country": "UK",
            "accuracy": 50
        }
    },
    "diana": {
        "user": {
            "username": "diana",
            "email": "diana@example.com",
            "password": "Password123!",
            "first_name": "Diana",
            "last_name": "Martinez"
        },
        "profile": {
            "bio": "Yoga instructor and nature lover. Passionate about wellness and mindfulness. Seeking someone who values balance and inner peace.",
            "age": 32,
            "gender": "Female",
            "sexual_preferences": "Both",
            "fame_rating": 7
        },
        "interests": ["Yoga", "Hiking", "Reading", "Cooking", "Volunteering"],
        "location": {
            "latitude": 37.7749,
            "longitude": -122.4194,
            "city": "San Francisco",
            "country": "USA",
            "accuracy": 50
        }
    },
    "ethan": {
        "user": {
            "username": "ethan",
            "email": "ethan@example.com",
            "password": "Password123!",
            "first_name": "Ethan",
            "last_name": "Wilson"
        },
        "profile": {
            "bio": "Music producer and concert goer. Love discovering new bands and attending live shows. Looking for someone who shares my passion for music!",
            "age": 27,
            "gender": "Male",
            "sexual_preferences": "Women",
            "fame_rating": 6
        },
        "interests": ["Music", "Movies", "Gaming", "Travel", "Sports"],
        "location": {
            "latitude": 48.8566,
            "longitude": 2.3522,
            "city": "Paris",
            "country": "France",
            "accuracy": 50
        }
    }
}


def main():
    print("=" * 60)
    print("  🎭 Matcha User Profile Creator")
    print("=" * 60)
    
    # Load config
    try:
        config = load_config()
        db_pool = create_connection_pool(config)
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return
    
    # Check if argument provided
    if len(sys.argv) > 1:
        profile_name = sys.argv[1].lower()
        if profile_name in SAMPLE_PROFILES:
            sample = SAMPLE_PROFILES[profile_name]
            create_user_profile(
                db_pool,
                sample["user"],
                sample["profile"],
                sample.get("interests"),
                sample.get("location")
            )
        else:
            print(f"❌ Unknown profile: {profile_name}")
            print(f"   Available profiles: {', '.join(SAMPLE_PROFILES.keys())}")
    else:
        # Interactive mode
        print("\n📋 Available sample profiles:")
        print("-" * 60)
        for name, data in SAMPLE_PROFILES.items():
            user = data["user"]
            profile = data["profile"]
            print(f"\n🔹 {name.upper()}")
            print(f"   Name: {user['first_name']} {user['last_name']}")
            print(f"   Age: {profile['age']}, Gender: {profile['gender']}")
            print(f"   Interests: {', '.join(data.get('interests', [])[:3])}...")
            print(f"   Location: {data['location']['city']}, {data['location']['country']}")
        
        print("\n" + "-" * 60)
        print("\nOptions:")
        print("  1. Create a specific profile (enter name)")
        print("  2. Create all profiles (enter 'all')")
        print("  3. Custom profile (enter 'custom')")
        print("  4. Exit (enter 'exit')")
        
        choice = input("\nYour choice: ").strip().lower()
        
        if choice == "exit":
            print("👋 Goodbye!")
            return
        
        elif choice == "all":
            print("\n📦 Creating all sample profiles...")
            for name, data in SAMPLE_PROFILES.items():
                print(f"\n{'=' * 60}")
                create_user_profile(
                    db_pool,
                    data["user"],
                    data["profile"],
                    data.get("interests"),
                    data.get("location")
                )
            print(f"\n{'=' * 60}")
            print("✅ All profiles created!")
        
        elif choice == "custom":
            print("\n🎨 Custom Profile Creator")
            print("-" * 60)
            
            user_data = {
                "username": input("Username: ").strip(),
                "email": input("Email: ").strip(),
                "password": input("Password: ").strip(),
                "first_name": input("First name: ").strip(),
                "last_name": input("Last name: ").strip()
            }
            
            profile_data = {
                "bio": input("Bio: ").strip(),
                "age": int(input("Age: ").strip()),
                "gender": input("Gender (Female/Male/Non-binary/Other): ").strip(),
                "sexual_preferences": input("Sexual preferences (Women/Men/Both/All): ").strip()
            }
            
            interests_input = input("Interests (comma-separated): ").strip()
            interests = [i.strip() for i in interests_input.split(",")] if interests_input else []
            
            add_location = input("Add location? (y/n): ").strip().lower()
            location = None
            if add_location == 'y':
                location = {
                    "latitude": float(input("Latitude: ").strip()),
                    "longitude": float(input("Longitude: ").strip()),
                    "city": input("City: ").strip(),
                    "country": input("Country: ").strip()
                }
            
            create_user_profile(db_pool, user_data, profile_data, interests, location)
        
        elif choice in SAMPLE_PROFILES:
            sample = SAMPLE_PROFILES[choice]
            create_user_profile(
                db_pool,
                sample["user"],
                sample["profile"],
                sample.get("interests"),
                sample.get("location")
            )
        else:
            print(f"❌ Invalid choice: {choice}")
    
    db_pool.closeall()
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
