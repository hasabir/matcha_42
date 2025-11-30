-- Migration: Prevent duplicate profile view notifications
-- This creates an index to help prevent duplicate unseen profile_view notifications

-- Drop the index if it already exists
DROP INDEX IF EXISTS idx_unique_unseen_profile_view;

-- Step 1: Clean up existing duplicate notifications
-- Keep only the most recent notification for each (user_id, type, reference_id) combination
-- where seen = FALSE and type = 'profile_view'
DELETE FROM notifications
WHERE notification_id IN (
    SELECT notification_id
    FROM (
        SELECT notification_id,
               ROW_NUMBER() OVER (
                   PARTITION BY user_id, type, reference_id 
                   ORDER BY received_at DESC
               ) as rn
        FROM notifications
        WHERE seen = FALSE AND type = 'profile_view'
    ) t
    WHERE t.rn > 1
);

-- Step 2: Create a partial unique index to prevent duplicate unseen profile_view notifications
-- This allows only one unseen notification per (user_id, type, reference_id) combination
-- Once a notification is marked as seen, new ones can be created
CREATE UNIQUE INDEX idx_unique_unseen_profile_view 
ON notifications (user_id, type, reference_id) 
WHERE seen = FALSE AND type = 'profile_view';

-- Add a comment to the index
COMMENT ON INDEX idx_unique_unseen_profile_view IS 
'Prevents duplicate unseen profile_view notifications from the same viewer';
