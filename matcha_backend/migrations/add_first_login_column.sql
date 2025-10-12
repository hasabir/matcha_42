-- Migration: Add first_login column to users table
-- This tracks if it's the user's first login to determine redirect behavior

-- Add first_login column (defaults to TRUE for new users)
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS first_login BOOLEAN DEFAULT TRUE;

-- For existing users, set first_login to FALSE (assuming they've already logged in)
-- New registrations will have first_login = TRUE by default
UPDATE users 
SET first_login = FALSE 
WHERE verified = TRUE AND active = TRUE;

-- Show the updated users table structure
\d users;