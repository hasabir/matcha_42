-- SQL script to fix profile picture paths
-- Run this with: psql -U <username> -d <database> -f fix_profile_paths.sql

-- Show current paths before update
SELECT user_id, profile_picture 
FROM profiles 
WHERE profile_picture IS NOT NULL;

-- Step 1: Fix double /static/static/ by removing ALL /static/ prefixes
UPDATE profiles
SET profile_picture = SUBSTRING(profile_picture FROM 9)
WHERE profile_picture LIKE '/static/static/%';

-- Step 2: Remove single /static/ prefix (we'll add it back when serving)
UPDATE profiles
SET profile_picture = SUBSTRING(profile_picture FROM 9)
WHERE profile_picture LIKE '/static/%' AND profile_picture NOT LIKE '/static/static/%';

-- Step 3: Fix folder typo: pofile_picture -> profile_picture  
UPDATE profiles
SET profile_picture = REPLACE(profile_picture, '/pofile_picture/', '/profile_picture/')
WHERE profile_picture LIKE '%/pofile_picture/%';

-- Step 4: Fix folder typo without leading slash
UPDATE profiles
SET profile_picture = REPLACE(profile_picture, 'pofile_picture/', 'profile_picture/')
WHERE profile_picture LIKE '%pofile_picture/%';

-- Show updated paths
SELECT user_id, profile_picture 
FROM profiles 
WHERE profile_picture IS NOT NULL;

-- Summary
SELECT 
    COUNT(*) as total_profiles_with_pictures,
    COUNT(CASE WHEN profile_picture LIKE '%/static/static/%' THEN 1 END) as still_has_double_static,
    COUNT(CASE WHEN profile_picture LIKE '%/pofile_picture/%' THEN 1 END) as still_has_typo
FROM profiles 
WHERE profile_picture IS NOT NULL;
