-- Performance indexes for matching algorithm optimization
-- These indexes improve query performance for the browse/suggestions endpoint

-- Index on profiles for filtering by sexual preferences
CREATE INDEX IF NOT EXISTS idx_profiles_sexual_preferences 
ON profiles(sexual_preferences);

-- Index on profiles for filtering by gender
CREATE INDEX IF NOT EXISTS idx_profiles_gender 
ON profiles(gender);

-- Index on profiles for filtering by age
CREATE INDEX IF NOT EXISTS idx_profiles_age 
ON profiles(age);

-- Index on profiles for filtering and sorting by fame rating
CREATE INDEX IF NOT EXISTS idx_profiles_fame_rating 
ON profiles(fame_rating);

-- Composite index for common query patterns (gender + sexual_preferences)
CREATE INDEX IF NOT EXISTS idx_profiles_gender_preferences 
ON profiles(gender, sexual_preferences);

-- Index on user_locations for city filtering
CREATE INDEX IF NOT EXISTS idx_user_locations_city 
ON user_locations(city);

-- Index on user_locations for country filtering
CREATE INDEX IF NOT EXISTS idx_user_locations_country 
ON user_locations(country);

-- Index for user_id lookups in profiles
CREATE INDEX IF NOT EXISTS idx_profiles_user_id 
ON profiles(user_id);

-- Note: Spatial index for GPS coordinates already exists in schema.sql:
-- CREATE INDEX IF NOT EXISTS idx_user_locations_geo ON user_locations USING GIST (
--     ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
-- );
