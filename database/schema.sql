-- Matcha Project: SQL Schema for Mandatory Part

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    location TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verification_token TEXT,
    reset_token TEXT,  -- Fixed typo: was "rest_token"
    reset_password_token TEXT,
    active BOOLEAN DEFAULT FALSE,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Profiles Table
CREATE TABLE IF NOT EXISTS profiles (
    profile_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,  -- Fixed: INT instead of UUID
    bio TEXT,
    age INTEGER,
    gender TEXT,
    sexual_preferences TEXT,
    location TEXT, -- Consider separate latitude/longitude columns if you need precise coordinates
    fame_rating INTEGER DEFAULT 0,
    profile_picture TEXT
);

-- Images Table
CREATE TABLE IF NOT EXISTS images (
    image_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,  -- Fixed: INT instead of UUID
    image_url TEXT NOT NULL,
    is_profile_picture BOOLEAN DEFAULT FALSE,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tags Table
CREATE TABLE IF NOT EXISTS tags (
    tag_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tag_name TEXT UNIQUE NOT NULL
);

-- User Tags (Many-to-Many)
CREATE TABLE IF NOT EXISTS user_tags (
    user_id INT REFERENCES users(id) ON DELETE CASCADE,  -- Fixed: INT instead of UUID
    tag_id INT REFERENCES tags(tag_id) ON DELETE CASCADE,  -- Fixed: INT instead of UUID
    PRIMARY KEY (user_id, tag_id)
);

-- Likes Table
CREATE TABLE IF NOT EXISTS likes (
    liker_id INT REFERENCES users(id) ON DELETE CASCADE,  -- Fixed: INT instead of UUID
    liked_id INT REFERENCES users(id) ON DELETE CASCADE,  -- Fixed: INT instead of UUID
    liked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (liker_id, liked_id)
);

-- Connections Table
CREATE TABLE IF NOT EXISTS connections (
    user1_id INT REFERENCES users(id) ON DELETE CASCADE,  -- Fixed: INT instead of UUID
    user2_id INT REFERENCES users(id) ON DELETE CASCADE,  -- Fixed: INT instead of UUID
    connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user1_id, user2_id)
);

-- Visits Table
CREATE TABLE IF NOT EXISTS visits (
    viewer_id INT REFERENCES users(id) ON DELETE CASCADE,  -- Fixed: INT instead of UUID
    viewed_id INT REFERENCES users(id) ON DELETE CASCADE,  -- Fixed: INT instead of UUID
    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (viewer_id, viewed_id, viewed_at)
);

-- Blocks Table
CREATE TABLE IF NOT EXISTS blocks (
    blocker_id INT REFERENCES users(id) ON DELETE CASCADE,  -- Fixed: INT instead of UUID
    blocked_id INT REFERENCES users(id) ON DELETE CASCADE,  -- Fixed: INT instead of UUID
    blocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (blocker_id, blocked_id)
);

-- Reports Table
CREATE TABLE IF NOT EXISTS reports (
    report_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    reporter_id INT REFERENCES users(id) ON DELETE CASCADE,  -- Fixed: INT instead of UUID
    reported_id INT REFERENCES users(id) ON DELETE CASCADE,  -- Fixed: INT instead of UUID
    reason TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Conversations Table
CREATE TABLE IF NOT EXISTS conversations (
    conversation_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user1_id INT REFERENCES users(id) ON DELETE CASCADE,  -- Fixed: INT instead of UUID
    user2_id INT REFERENCES users(id) ON DELETE CASCADE,  -- Fixed: INT instead of UUID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Messages Table
CREATE TABLE IF NOT EXISTS messages (
    message_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    conversation_id INT REFERENCES conversations(conversation_id) ON DELETE CASCADE,  -- Fixed: INT instead of UUID
    sender_id INT REFERENCES users(id) ON DELETE CASCADE,  -- Fixed: INT instead of UUID
    message_text TEXT NOT NULL,
    status BOOLEAN DEFAULT FALSE,  -- Consider renaming to "is_read" for clarity
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notifications Table
CREATE TABLE IF NOT EXISTS notifications (
    notification_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,  -- Fixed: INT instead of UUID
    type TEXT NOT NULL,
    reference_id INT,  -- Changed from UUID to INT for consistency
    seen BOOLEAN DEFAULT FALSE,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);