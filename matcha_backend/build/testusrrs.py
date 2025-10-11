from flask import Flask
from werkzeug.security import generate_password_hash
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime, timedelta
import random
import os

app = Flask(__name__)

# Database configuration - reads from environment variables
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'matcha_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
    'host': os.getenv('DB_HOST', 'db'),  # Use 'db' for Docker, 'localhost' for local
    'port': int(os.getenv('DB_PORT', 5432))
}

def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(**DB_CONFIG)

def seed_database():
    """Seed the database with sample users and related data"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Clear existing data (in reverse order of dependencies)
        print("Clearing existing data...")
        tables = [
            'notifications', 'messages', 'conversations', 'reports', 
            'blocks', 'visits', 'connections', 'likes', 'user_tags', 
            'tags', 'images', 'profiles', 'user_locations', 'users'
        ]
        for table in tables:
            cur.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE")
        
        # Common password hash for all users (password: "Password123!")
        password_hash = "$2b$12$yE8S6bP4M3LVNFKOiRKIb.Nb7qzc2vDyo.csWYw0LLGWkR1H5vhcy"
        
        # Sample users data
        users_data = [
            {
                'username': 'test1',
                'email': 'yassine.rahmi@matcha.com',
                'first_name': 'Yassine',
                'last_name': 'Rahimi',
                'verified': True,
                'active': True
            },
            {
                'username': 'test2',
                'email': 'khadija.mahdi@matcha.com',
                'first_name': 'Khadija',
                'last_name': 'Mahdi',
                'verified': True,
                'active': True
            },
            {
                'username': 'test3',
                'email': 'ahmed.benali@matcha.com',
                'first_name': 'Ahmed',
                'last_name': 'Benali',
                'verified': True,
                'active': True
            },
            {
                'username': 'test4',
                'email': 'sara.elkhalfi@matcha.com',
                'first_name': 'Sara',
                'last_name': 'El Khalfi',
                'verified': True,
                'active': False
            },
            {
                'username': 'test5',
                'email': 'mehdi.ziani@matcha.com',
                'first_name': 'Mehdi',
                'last_name': 'Ziani',
                'verified': False,
                'active': False
            },
            {
                'username': 'test6',
                'email': 'leila.amrani@matcha.com',
                'first_name': 'Leila',
                'last_name': 'Amrani',
                'verified': True,
                'active': True
            }
        ]
        
        # Insert users
        print("Inserting users...")
        user_ids = []
        for user in users_data:
            cur.execute("""
                INSERT INTO users (username, email, password, first_name, last_name, 
                                 verified, active, last_seen)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                user['username'], user['email'], password_hash,
                user['first_name'], user['last_name'], user['verified'],
                user['active'], datetime.now() - timedelta(hours=random.randint(0, 48))
            ))
            user_ids.append(cur.fetchone()[0])
        
        # Insert user locations (Casablanca area)
        print("Inserting user locations...")
        locations_data = [
            (user_ids[0], 33.5731, -7.5898, 'Casablanca', 'Morocco', 50),
            (user_ids[1], 33.5892, -7.6031, 'Casablanca', 'Morocco', 100),
            (user_ids[2], 33.5650, -7.5950, 'Casablanca', 'Morocco', 75),
            (user_ids[3], 33.5800, -7.6100, 'Casablanca', 'Morocco', 120),
            (user_ids[4], 33.5720, -7.5850, 'Casablanca', 'Morocco', 60),
            (user_ids[5], 33.5950, -7.6200, 'Casablanca', 'Morocco', 90)
        ]
        execute_values(cur, """
            INSERT INTO user_locations (user_id, latitude, longitude, city, country, accuracy)
            VALUES %s
        """, locations_data)
        
        # Insert profiles
        print("Inserting profiles...")
        profiles_data = [
            (user_ids[0], 'Software engineer passionate about tech and travel 🚀', 28, 'male', 'women', 42, None),
            (user_ids[1], 'Artist and coffee enthusiast ☕🎨', 26, 'female', 'men', 38, None),
            (user_ids[2], 'Fitness trainer | Outdoor lover 🏋️‍♂️🏔️', 30, 'male', 'women', 55, None),
            (user_ids[3], 'Bookworm and cat mom 📚🐱', 25, 'female', 'everyone', 31, None),
            (user_ids[4], 'Musician and food lover 🎸🍕', 27, 'male', 'women', 18, None),
            (user_ids[5], 'Photographer capturing life moments 📷✨', 29, 'female', 'men', 47, None)
        ]
        execute_values(cur, """
            INSERT INTO profiles (user_id, bio, age, gender, sexual_preferences, fame_rating, profile_picture)
            VALUES %s
        """, profiles_data)
        
        # Insert tags
        print("Inserting tags...")
        tags_list = ['travel', 'music', 'sports', 'art', 'food', 'tech', 
                     'photography', 'reading', 'fitness', 'cinema']
        execute_values(cur, "INSERT INTO tags (tag_name) VALUES %s", 
                      [(tag,) for tag in tags_list])
        
        # Get tag IDs
        cur.execute("SELECT tag_id, tag_name FROM tags")
        tags_dict = {name: id for id, name in cur.fetchall()}
        
        # Insert user tags (interests)
        print("Inserting user tags...")
        user_tags_data = [
            (user_ids[0], [tags_dict['tech'], tags_dict['travel'], tags_dict['music']]),
            (user_ids[1], [tags_dict['art'], tags_dict['food'], tags_dict['photography']]),
            (user_ids[2], [tags_dict['fitness'], tags_dict['sports'], tags_dict['travel']]),
            (user_ids[3], [tags_dict['reading'], tags_dict['cinema'], tags_dict['art']]),
            (user_ids[4], [tags_dict['music'], tags_dict['food'], tags_dict['cinema']]),
            (user_ids[5], [tags_dict['photography'], tags_dict['art'], tags_dict['travel']])
        ]
        for user_id, tag_ids in user_tags_data:
            execute_values(cur, "INSERT INTO user_tags (user_id, tag_id) VALUES %s",
                          [(user_id, tag_id) for tag_id in tag_ids])
        
        # Insert likes (create some mutual likes for matching)
        print("Inserting likes...")
        likes_data = [
            (user_ids[0], user_ids[1]),  # Mutual like
            (user_ids[1], user_ids[0]),  # Mutual like
            (user_ids[2], user_ids[3]),
            (user_ids[3], user_ids[2]),  # Mutual like
            (user_ids[0], user_ids[5]),
            (user_ids[5], user_ids[0]),  # Mutual like
        ]
        execute_values(cur, """
            INSERT INTO likes (liker_id, liked_id, liked_at)
            VALUES %s
        """, [(l[0], l[1], datetime.now() - timedelta(days=random.randint(1, 7))) 
              for l in likes_data])
        
        # Insert connections (matched users)
        print("Inserting connections...")
        connections_data = [
            (user_ids[0], user_ids[1]),
            (user_ids[2], user_ids[3]),
            (user_ids[0], user_ids[5])
        ]
        execute_values(cur, """
            INSERT INTO connections (user1_id, user2_id, connected_at)
            VALUES %s
        """, [(c[0], c[1], datetime.now() - timedelta(days=random.randint(1, 5))) 
              for c in connections_data])
        
        # Insert visits (profile views)
        print("Inserting visits...")
        visits_data = [
            (user_ids[0], user_ids[2]),
            (user_ids[1], user_ids[3]),
            (user_ids[2], user_ids[5]),
            (user_ids[3], user_ids[0]),
            (user_ids[4], user_ids[1]),
            (user_ids[5], user_ids[4])
        ]
        execute_values(cur, """
            INSERT INTO visits (visitor_id, visited_id, visited_at)
            VALUES %s
        """, [(v[0], v[1], datetime.now() - timedelta(hours=random.randint(1, 72))) 
              for v in visits_data])
        
        # Insert sample conversations
        print("Inserting conversations...")
        cur.execute("""
            INSERT INTO conversations (user1_id, user2_id)
            VALUES (%s, %s), (%s, %s), (%s, %s)
            RETURNING conversation_id
        """, (user_ids[0], user_ids[1], user_ids[2], user_ids[3], user_ids[0], user_ids[5]))
        conv_ids = [row[0] for row in cur.fetchall()]
        
        # Insert sample messages
        print("Inserting messages...")
        messages_data = [
            (conv_ids[0], user_ids[0], "Hey! How are you doing?", True),
            (conv_ids[0], user_ids[1], "Hi! I'm great, thanks! Love your profile 😊", True),
            (conv_ids[1], user_ids[2], "Hey Sara! Want to grab coffee sometime?", False),
            (conv_ids[2], user_ids[5], "Hi Yassine! Thanks for the like!", True)
        ]
        execute_values(cur, """
            INSERT INTO messages (conversation_id, sender_id, message_text, status, created_at)
            VALUES %s
        """, [(m[0], m[1], m[2], m[3], datetime.now() - timedelta(hours=random.randint(1, 24))) 
              for m in messages_data])
        
        # Insert sample notifications
        print("Inserting notifications...")
        notifications_data = [
            (user_ids[1], 'like', user_ids[0], False),
            (user_ids[0], 'match', user_ids[1], True),
            (user_ids[3], 'visit', user_ids[2], False),
            (user_ids[5], 'message', user_ids[0], False)
        ]
        execute_values(cur, """
            INSERT INTO notifications (sender_id, type, receiver_id , seen, received_at)
            VALUES %s
        """, [(n[0], n[1], n[2], n[3], datetime.now() - timedelta(hours=random.randint(1, 12))) 
              for n in notifications_data])
        
        conn.commit()
        print("\n✅ Database seeded successfully!")
        print(f"\n📊 Created {len(user_ids)} users with:")
        print(f"   - Profiles and locations")
        print(f"   - {len(tags_list)} tags")
        print(f"   - Likes and connections")
        print(f"   - Profile visits")
        print(f"   - {len(conv_ids)} conversations with messages")
        print(f"   - Notifications")
        print(f"\n🔑 All users password: Password123!")
        print("\n👤 Created users:")
        for i, user in enumerate(users_data):
            print(f"   {i+1}. {user['username']} ({user['email']}) - "
                  f"{'✓ verified' if user['verified'] else '✗ not verified'}, "
                  f"{'✓ active' if user['active'] else '✗ inactive'}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    with app.app_context():
        print("🌱 Starting database seeding...")
        print(f"📡 Connecting to: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}")
        seed_database()
        
        
# docker exec -it matcha_backend python3 /app/build/testusrrs.py