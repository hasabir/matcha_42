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

# Sample data for generating realistic profiles
FIRST_NAMES_MALE = ['Ahmed', 'Yassine', 'Mehdi', 'Omar', 'Ali', 'Hassan', 'Karim', 'Amine', 'Youssef', 'Samir',
                     'Zakaria', 'Hamza', 'Adil', 'Rachid', 'Khalid', 'Jamal', 'Nabil', 'Tariq', 'Faisal', 'Ibrahim']
FIRST_NAMES_FEMALE = ['Khadija', 'Fatima', 'Sara', 'Leila', 'Amina', 'Nadia', 'Samira', 'Zineb', 'Salma', 'Mariam',
                       'Yasmine', 'Laila', 'Houda', 'Soukaina', 'Imane', 'Kenza', 'Rim', 'Meryem', 'Hanane', 'Aicha']
LAST_NAMES = ['Benali', 'Mahdi', 'Ziani', 'Amrani', 'Rahimi', 'El Khalfi', 'Alami', 'Bouazza', 'Cherkaoui', 'Idrissi',
              'Berradi', 'Tazi', 'Fassi', 'Ghazi', 'Nejjar', 'Sabri', 'Mansouri', 'Bakkali', 'Rami', 'Kadiri']

BIOS = [
    'Software engineer passionate about tech and travel 🚀',
    'Artist and coffee enthusiast ☕🎨',
    'Fitness trainer | Outdoor lover 🏋️‍♂️🏔️',
    'Bookworm and cat mom 📚🐱',
    'Musician and food lover 🎸🍕',
    'Photographer capturing life moments 📷✨',
    'Adventure seeker and nature lover 🌲🏕️',
    'Yoga instructor spreading positive vibes 🧘‍♀️✨',
    'Chef experimenting with new recipes 👨‍🍳🍜',
    'Marketing professional and cinema fan 🎬📊',
    'Runner and healthy lifestyle advocate 🏃‍♂️💪',
    'Graphic designer with creative vision 🎨💻',
    'Travel blogger exploring the world 🌍✈️',
    'Gamer and tech enthusiast 🎮💻',
    'Writer working on my first novel 📝📖',
    'Dance instructor living life to the fullest 💃🎶',
    'Engineer by day, DJ by night 🎧🔊',
    'Startup founder chasing dreams 🚀💼',
    'Teacher passionate about education 📚👩‍🏫',
    'Architect designing the future 🏛️📐'
]

CITIES = [
    ('Casablanca', 'Morocco', 33.5731, -7.5898),
    ('Rabat', 'Morocco', 33.9716, -6.8498),
    ('Marrakech', 'Morocco', 31.6295, -7.9811),
    ('Fes', 'Morocco', 34.0181, -5.0078),
    ('Tangier', 'Morocco', 35.7595, -5.8340),
    ('Agadir', 'Morocco', 30.4278, -9.5981),
]

def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(**DB_CONFIG)

def seed_database():
    """Seed the database with 500+ sample users and related data"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    NUM_USERS = 550  # Generate 550 users to exceed requirement
    
    try:
        # Clear existing data (in reverse order of dependencies)
        print("🗑️  Clearing existing data...")
        tables = [
            'notifications', 'messages', 'conversations', 'reports', 
            'blocks', 'visits', 'connections', 'likes', 'user_tags', 
            'tags', 'images', 'profiles', 'user_locations', 'users'
        ]
        for table in tables:
            cur.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE")
        
        # Common password hash for all users (password: "Password123!")
        password_hash = "$2b$12$yE8S6bP4M3LVNFKOiRKIb.Nb7qzc2vDyo.csWYw0LLGWkR1H5vhcy"
        
        # Generate users data
        print(f"👥 Generating {NUM_USERS} users...")
        users_batch = []
        for i in range(NUM_USERS):
            # Alternate between male and female
            is_male = i % 2 == 0
            first_name = random.choice(FIRST_NAMES_MALE if is_male else FIRST_NAMES_FEMALE)
            last_name = random.choice(LAST_NAMES)
            username = f"user{i+1}"
            email = f"{first_name.lower()}.{last_name.lower()}{i}@matcha.com"
            
            # 90% verified, 85% active
            verified = random.random() < 0.90
            active = random.random() < 0.85
            
            last_seen = datetime.now() - timedelta(hours=random.randint(0, 168))  # Last week
            
            users_batch.append((username, email, password_hash, first_name, last_name, 
                              verified, active, last_seen))
        
        # Batch insert users
        print("💾 Inserting users into database...")
        execute_values(cur, """
            INSERT INTO users (username, email, password, first_name, last_name, 
                             verified, active, last_seen)
            VALUES %s
            RETURNING id
        """, users_batch, page_size=100)
        user_ids = [row[0] for row in cur.fetchall()]
        print(f"✅ Inserted {len(user_ids)} users")
        
        # Insert user locations
        print("📍 Generating user locations...")
        locations_batch = []
        for user_id in user_ids:
            city_data = random.choice(CITIES)
            city, country, base_lat, base_lng = city_data
            
            # Add random offset within ~10km radius
            lat_offset = random.uniform(-0.09, 0.09)  # ~10km
            lng_offset = random.uniform(-0.09, 0.09)
            
            latitude = base_lat + lat_offset
            longitude = base_lng + lng_offset
            accuracy = random.randint(20, 200)
            
            locations_batch.append((user_id, latitude, longitude, city, country, accuracy))
        
        execute_values(cur, """
            INSERT INTO user_locations (user_id, latitude, longitude, city, country, accuracy)
            VALUES %s
        """, locations_batch, page_size=100)
        print(f"✅ Inserted {len(locations_batch)} locations")
        
        # Insert profiles
        print("👤 Generating user profiles...")
        profiles_batch = []
        genders = ['male', 'female']
        preferences_options = ['male', 'female', 'both']
        
        for i, user_id in enumerate(user_ids):
            bio = random.choice(BIOS)
            age = random.randint(18, 65)
            gender = genders[i % 2]  # Alternate gender
            
            # Sexual preferences based on gender for realistic matching
            if gender == 'male':
                sexual_pref = random.choice(['female', 'female', 'both'])  # More likely to prefer female
            else:
                sexual_pref = random.choice(['male', 'male', 'both'])  # More likely to prefer male
            
            fame_rating = random.randint(0, 100)
            
            profiles_batch.append((user_id, bio, age, gender, sexual_pref, fame_rating, None))
        
        execute_values(cur, """
            INSERT INTO profiles (user_id, bio, age, gender, sexual_preferences, fame_rating, profile_picture)
            VALUES %s
        """, profiles_batch, page_size=100)
        print(f"✅ Inserted {len(profiles_batch)} profiles")
        
        # Insert tags
        print("🏷️  Inserting tags...")
        tags_list = ['travel', 'music', 'sports', 'art', 'food', 'tech', 
                     'photography', 'reading', 'fitness', 'cinema', 'gaming', 'yoga',
                     'hiking', 'cooking', 'dancing', 'writing', 'fashion', 'volunteering']
        execute_values(cur, "INSERT INTO tags (tag_name) VALUES %s", 
                      [(tag,) for tag in tags_list])
        
        # Get tag IDs
        cur.execute("SELECT tag_id, tag_name FROM tags")
        tags_dict = {name: id for id, name in cur.fetchall()}
        tag_ids_list = list(tags_dict.values())
        print(f"✅ Inserted {len(tags_list)} tags")
        
        # Insert user tags (interests) - each user gets 2-5 random tags
        print("🎯 Assigning tags to users...")
        user_tags_batch = []
        for user_id in user_ids:
            num_tags = random.randint(2, 5)
            user_tag_ids = random.sample(tag_ids_list, num_tags)
            for tag_id in user_tag_ids:
                user_tags_batch.append((user_id, tag_id))
        
        execute_values(cur, "INSERT INTO user_tags (user_id, tag_id) VALUES %s",
                      user_tags_batch, page_size=100)
        print(f"✅ Assigned {len(user_tags_batch)} tag relationships")
        
        # Insert likes - Generate realistic interaction patterns
        print("💖 Generating likes...")
        likes_batch = []
        connections_set = set()
        
        # Each user likes 3-15 other random users
        for user_id in user_ids[:400]:  # First 400 users actively like
            num_likes = random.randint(3, 15)
            potential_likes = [uid for uid in user_ids if uid != user_id]
            liked_users = random.sample(potential_likes, min(num_likes, len(potential_likes)))
            
            for liked_id in liked_users:
                likes_batch.append((user_id, liked_id, 
                                  datetime.now() - timedelta(days=random.randint(0, 30))))
                
                # Check for mutual likes to create connections
                if (liked_id, user_id) in [(l[0], l[1]) for l in likes_batch]:
                    connections_set.add(tuple(sorted([user_id, liked_id])))
        
        execute_values(cur, """
            INSERT INTO likes (liker_id, liked_id, liked_at)
            VALUES %s
        """, likes_batch, page_size=100)
        print(f"✅ Inserted {len(likes_batch)} likes")
        
        # Insert connections (matched users from mutual likes)
        print("🤝 Creating connections from mutual likes...")
        connections_batch = [
            (user1, user2, datetime.now() - timedelta(days=random.randint(0, 20)))
            for user1, user2 in list(connections_set)[:150]  # Limit to 150 connections
        ]
        
        if connections_batch:
            execute_values(cur, """
                INSERT INTO connections (user1_id, other_user_id, connected_at)
                VALUES %s
            """, connections_batch, page_size=100)
            print(f"✅ Inserted {len(connections_batch)} connections")
        
        # Insert visits (profile views) - More realistic patterns
        print("👁️  Generating profile visits...")
        visits_batch = []
        
        # Each user visits 5-20 profiles
        for user_id in user_ids[:450]:  # First 450 users actively browse
            num_visits = random.randint(5, 20)
            potential_visits = [uid for uid in user_ids if uid != user_id]
            visited_users = random.sample(potential_visits, min(num_visits, len(potential_visits)))
            
            for visited_id in visited_users:
                visits_batch.append((user_id, visited_id,
                                   datetime.now() - timedelta(hours=random.randint(1, 720))))
        
        execute_values(cur, """
            INSERT INTO visits (visitor_id, visited_id, visited_at)
            VALUES %s
        """, visits_batch, page_size=100)
        print(f"✅ Inserted {len(visits_batch)} profile visits")
        
        # Insert conversations for some connected users
        print("💬 Creating conversations...")
        conversations_batch = []
        for user1, user2, _ in connections_batch[:50]:  # 50 conversations
            conversations_batch.append((user1, user2))
        
        if conversations_batch:
            execute_values(cur, """
                INSERT INTO conversations (user1_id, user2_id)
                VALUES %s
                RETURNING conversation_id
            """, conversations_batch)
            conv_ids = [row[0] for row in cur.fetchall()]
            print(f"✅ Inserted {len(conv_ids)} conversations")
            
            # Insert sample messages for some conversations
            print("📨 Adding messages to conversations...")
            messages_batch = []
            sample_messages = [
                "Hey! How are you doing?",
                "Hi! I'm great, thanks! Love your profile 😊",
                "Want to grab coffee sometime?",
                "Thanks for the like!",
                "What are your hobbies?",
                "I love traveling too!",
                "That sounds interesting!",
                "Would love to hear more about that",
            ]
            
            for conv_id in conv_ids[:30]:  # First 30 conversations get messages
                num_messages = random.randint(1, 5)
                sender = conversations_batch[conv_ids.index(conv_id)][random.randint(0, 1)]
                
                for _ in range(num_messages):
                    message_text = random.choice(sample_messages)
                    status = random.choice([True, False])
                    created = datetime.now() - timedelta(hours=random.randint(1, 240))
                    messages_batch.append((conv_id, sender, message_text, status, created))
            
            if messages_batch:
                execute_values(cur, """
                    INSERT INTO messages (conversation_id, sender_id, message_text, status, created_at)
                    VALUES %s
                """, messages_batch, page_size=100)
                print(f"✅ Inserted {len(messages_batch)} messages")
        
        # Insert sample notifications
        print("🔔 Generating notifications...")
        notifications_batch = []
        notification_types = ['like', 'visit', 'match', 'message']
        
        # Generate 200 random notifications
        for _ in range(200):
            user_id = random.choice(user_ids)
            notif_type = random.choice(notification_types)
            reference_id = random.choice([uid for uid in user_ids if uid != user_id])
            seen = random.choice([True, False, False])  # More unseen
            received = datetime.now() - timedelta(hours=random.randint(1, 168))
            
            notifications_batch.append((user_id, notif_type, reference_id, seen, received))
        
        execute_values(cur, """
            INSERT INTO notifications (user_id, type, reference_id, seen, received_at)
            VALUES %s
        """, notifications_batch, page_size=100)
        print(f"✅ Inserted {len(notifications_batch)} notifications")
        
        conn.commit()
        print("\n" + "="*70)
        print("✅ DATABASE SEEDED SUCCESSFULLY!")
        print("="*70)
        print(f"\n📊 Summary:")
        print(f"   👥 Users: {len(user_ids)}")
        print(f"   📍 Locations: {len(locations_batch)}")
        print(f"   👤 Profiles: {len(profiles_batch)}")
        print(f"   🏷️  Tags: {len(tags_list)}")
        print(f"   🎯 User-Tag relationships: {len(user_tags_batch)}")
        print(f"   💖 Likes: {len(likes_batch)}")
        print(f"   🤝 Connections: {len(connections_batch)}")
        print(f"   👁️  Profile visits: {len(visits_batch)}")
        if conversations_batch:
            print(f"   💬 Conversations: {len(conv_ids)}")
            print(f"   📨 Messages: {len(messages_batch) if messages_batch else 0}")
        print(f"   🔔 Notifications: {len(notifications_batch)}")
        print(f"\n🔑 Password for all users: Password123!")
        print(f"\n📝 Sample users to test:")
        print(f"   • user1 → user10 (most active users)")
        print(f"   • Most users are verified (90%) and active (85%)")
        print(f"   • Users distributed across 6 Moroccan cities")
        print(f"   • Realistic interaction patterns (likes, visits, matches)")
        print(f"\n🎯 Defense Requirements:")
        print(f"   ✅ Required: 500 profiles minimum")
        print(f"   ✅ Actual: {len(user_ids)} profiles")
        print(f"   ✅ Status: READY FOR DEFENSE")
        print("="*70 + "\n")
        
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