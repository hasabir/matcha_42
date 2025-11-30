-- Migration: Add neighborhood field to user_locations table
-- Date: 2025-11-30
-- Purpose: Implement neighborhood-level GPS positioning as per subject requirements

-- Add neighborhood column to user_locations table
ALTER TABLE user_locations
ADD COLUMN IF NOT EXISTS neighborhood VARCHAR(200);

-- Create index on neighborhood for faster searches
CREATE INDEX IF NOT EXISTS idx_user_locations_neighborhood 
ON user_locations(neighborhood);

-- Add comment to explain the field
COMMENT ON COLUMN user_locations.neighborhood IS 'Neighborhood-level location precision as required by subject';
