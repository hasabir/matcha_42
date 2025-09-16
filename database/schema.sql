-- Matcha Project: SQL Schema for Mandatory Part

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verification_token TEXT, 
    verified BOOLEAN DEFAULT FALSE, 
    reset_token TEXT, --! need to remove this
    reset_password_token TEXT,
    active BOOLEAN DEFAULT FALSE,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- User Locations Table
CREATE TABLE user_locations (
    location_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    latitude DOUBLE PRECISION NOT NULL CHECK (latitude BETWEEN -90 AND 90),
    longitude DOUBLE PRECISION NOT NULL CHECK (longitude BETWEEN -180 AND 180),
    city VARCHAR(100),
    country VARCHAR(100),
    accuracy INTEGER,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_current_location UNIQUE(user_id)
);
CREATE INDEX idx_user_locations_geo ON user_locations USING GIST (
    ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
);

-- Profiles Table
CREATE TABLE IF NOT EXISTS profiles (
    profile_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,  
    bio TEXT,
    age INTEGER,
    gender TEXT,
    sexual_preferences TEXT,
    user_location TEXT,
    fame_rating INTEGER DEFAULT 0,
    profile_picture TEXT
);

-- Images Table
CREATE TABLE IF NOT EXISTS images (
    image_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE, 
    image_url TEXT NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tags Table
CREATE TABLE IF NOT EXISTS tags (
    tag_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tag_name TEXT UNIQUE NOT NULL
);

-- User Tags (Many-to-Many)
CREATE TABLE IF NOT EXISTS user_tags (
    user_id INT REFERENCES users(id) ON DELETE CASCADE,  
    tag_id INT REFERENCES tags(tag_id) ON DELETE CASCADE,  
    PRIMARY KEY (user_id, tag_id)
);

-- Likes Table
CREATE TABLE IF NOT EXISTS likes (
    liker_id INT REFERENCES users(id) ON DELETE CASCADE,  
    liked_id INT REFERENCES users(id) ON DELETE CASCADE,  
    liked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (liker_id, liked_id)
);

-- Connections Table
CREATE TABLE IF NOT EXISTS connections (
    user1_id INT REFERENCES users(id) ON DELETE CASCADE,  
    user2_id INT REFERENCES users(id) ON DELETE CASCADE,  --!needs to be changed to other_user
    connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user1_id, user2_id)
);

-- Visits Table
CREATE TABLE IF NOT EXISTS visits (
    viewer_id INT REFERENCES users(id) ON DELETE CASCADE,  
    viewed_id INT REFERENCES users(id) ON DELETE CASCADE,  
    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (viewer_id, viewed_id, viewed_at)
);

-- Blocks Table
CREATE TABLE IF NOT EXISTS blocks (
    blocker_id INT REFERENCES users(id) ON DELETE CASCADE,  
    blocked_id INT REFERENCES users(id) ON DELETE CASCADE,  
    blocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (blocker_id, blocked_id)
);

-- Reports Table
CREATE TABLE IF NOT EXISTS reports (
    report_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    reporter_id INT REFERENCES users(id) ON DELETE CASCADE,  
    reported_id INT REFERENCES users(id) ON DELETE CASCADE,  
    reason TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Conversations Table
CREATE TABLE IF NOT EXISTS conversations (
    conversation_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user1_id INT REFERENCES users(id) ON DELETE CASCADE,  
    user2_id INT REFERENCES users(id) ON DELETE CASCADE,  
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Messages Table
CREATE TABLE IF NOT EXISTS messages (
    message_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    conversation_id INT REFERENCES conversations(conversation_id) ON DELETE CASCADE,  
    sender_id INT REFERENCES users(id) ON DELETE CASCADE,  
    message_text TEXT NOT NULL,
    status BOOLEAN DEFAULT FALSE,  -- Consider renaming to "is_read" for clarity
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notifications Table
CREATE TABLE IF NOT EXISTS notifications (
    notification_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,  
    type TEXT NOT NULL,
    reference_id INT,  -- Changed from UUID to INT for consistency
    seen BOOLEAN DEFAULT FALSE,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);