-- Migration: Add matches_count column if it doesn't exist
-- This ensures the database schema matches the application requirements

-- Add matches_count column to profiles table
ALTER TABLE profiles 
ADD COLUMN IF NOT EXISTS matches_count INTEGER DEFAULT 0;

-- Verify the column exists
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'profiles' AND column_name = 'matches_count';
