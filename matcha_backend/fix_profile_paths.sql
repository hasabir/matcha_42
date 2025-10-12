-- Fix profile picture paths in the database
-- Add /static/ prefix if missing

UPDATE profiles 
SET profile_picture = '/static/' || profile_picture 
WHERE profile_picture IS NOT NULL 
  AND profile_picture NOT LIKE '/static/%'
  AND profile_picture != '';

-- Also fix image paths in the images table if it exists
UPDATE images 
SET image_path = '/static/' || image_path 
WHERE image_path IS NOT NULL 
  AND image_path NOT LIKE '/static/%'
  AND image_path != '';

SELECT 'Profile paths fixed!' AS status;
