# User Profile Creation Guide

## Overview
This guide explains how to create user profiles for testing your Matcha dating application. You can create profiles through:
1. **Python Script** (Backend) - For quick database population
2. **Web Interface** (Frontend) - Through the ProfileStepOne component

---

## Method 1: Python Script (Quick & Easy)

### Script Location
```
/matcha_backend/create_user_profile.py
```

### Prerequisites
- Backend must be configured (database connection in `build/config.yml`)
- Database must be created and schema loaded

### Usage

#### Option 1: Create a Specific Sample Profile
```bash
cd matcha_backend
python create_user_profile.py alice
```

Available sample profiles:
- `alice` - Female, 28, Adventure seeker
- `bob` - Male, 30, Tech enthusiast
- `charlie` - Non-binary, 26, Artist and foodie
- `diana` - Female, 32, Yoga instructor
- `ethan` - Male, 27, Music producer

#### Option 2: Interactive Mode
```bash
python create_user_profile.py
```

This will show you:
1. List of available sample profiles
2. Options to create one, all, or custom profile
3. Interactive prompts for custom profile creation

#### Option 3: Create All Sample Profiles
```bash
python create_user_profile.py all
```

Or in interactive mode, choose option "all"

### Sample Profile: Alice

**User Data:**
```json
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "Password123!",
  "first_name": "Alice",
  "last_name": "Johnson"
}
```

**Profile Data:**
```json
{
  "bio": "Adventure seeker and coffee enthusiast...",
  "age": 28,
  "gender": "Female",
  "sexual_preferences": "Men",
  "fame_rating": 7
}
```

**Additional Data:**
- **Interests**: Hiking, Travel, Coffee, Photography, Reading
- **Location**: New York, USA (40.7128°N, 74.0060°W)

### Script Output

```
============================================================
  🎭 Matcha User Profile Creator
============================================================

📝 Creating user account: alice...
✅ User created with ID: 42

👤 Creating profile...
✅ Profile created with ID: 42

🏷️  Adding interests: Hiking, Travel, Coffee, Photography, Reading...
✅ Added 5 interests

📍 Setting location...
✅ Location set: New York, USA

🎉 Profile created successfully!
   Username: alice
   Email: alice@example.com
   Password: Password123!
   User ID: 42
   Profile ID: 42
```

---

## Method 2: Web Interface (User Flow)

### Navigate to Profile Setup
After registration and email verification, users are redirected to:
```
http://localhost:3000/profile-step-one
```

### Profile Setup Fields

#### 1. Gender Selection
- Female
- Male
- Non-binary
- Other

#### 2. Sexual Preferences
- Women
- Men
- Both
- All

#### 3. Bio
Multi-line text area for personal description:
- Minimum: A few sentences
- Maximum: ~500 characters
- Example: "Adventure seeker and coffee enthusiast. Love hiking on weekends..."

#### 4. Age
- Number input
- Minimum: 18
- Maximum: 120
- Example: 28

#### 5. Location
Text input for city/country:
- Format: "City, Country"
- GPS button available for auto-detection
- Example: "New York, USA"
- GPS shows: "Detected: 40.7128, -74.0060 (±50m)"

#### 6. Interests (Tags)
Select from predefined options:
- Hiking
- Reading
- Cooking
- Travel
- Music
- Art
- Sports
- Movies
- Gaming
- Volunteering

#### 7. Photos
Upload up to 5 photos:
- **Formats**: JPG, PNG, GIF, WebP
- **Size**: Max 5MB per file
- **Primary Photo**: One must be set as profile picture
- **Actions**: Set as Profile, Remove

### Submission Flow

When user clicks "Next":

1. **Validate** - Client-side validation checks all required fields
2. **Create Profile** - POST to `/api/profile/create_profile`
   ```javascript
   FormData: {
     profile_pic: <File>,
     bio: "...",
     gender: "Female",
     sexual_preferences: "Men",
     age: 28
   }
   ```

3. **Upload Additional Images** - POST to `/api/profile/upload_images`
   ```javascript
   FormData: {
     images: [<File>, <File>, ...]
   }
   ```

4. **Add Tags** - POST to `/api/profile/add_tags`
   ```json
   {
     "tags": ["Hiking", "Travel", "Coffee"]
   }
   ```

5. **Set Location** - POST to `/api/profile/set_location`
   ```json
   {
     "latitude": 40.7128,
     "longitude": -74.0060,
     "accuracy": 50
   }
   ```

6. **Redirect** - Navigate to `/home` (or `/dashboard`)

---

## Database Structure

### Tables Involved

#### 1. `users` Table
```sql
- id (PRIMARY KEY)
- username (UNIQUE)
- email (UNIQUE)
- password (hashed)
- first_name
- last_name
- verified (TRUE after email verification)
- active (TRUE after profile setup)
- first_login (FALSE after profile setup)
- created_at
- last_seen
```

#### 2. `profiles` Table
```sql
- profile_id (PRIMARY KEY)
- user_id (FOREIGN KEY → users.id)
- bio
- age
- gender
- sexual_preferences
- fame_rating (default: 5)
- profile_picture (URL path)
```

#### 3. `user_locations` Table
```sql
- location_id (PRIMARY KEY)
- user_id (FOREIGN KEY, UNIQUE)
- latitude
- longitude
- city
- country
- accuracy
- last_updated
```

#### 4. `tags` Table
```sql
- tag_id (PRIMARY KEY)
- tag_name (UNIQUE)
```

#### 5. `user_tags` Table (Many-to-Many)
```sql
- user_id (FOREIGN KEY → users.id)
- tag_id (FOREIGN KEY → tags.tag_id)
- PRIMARY KEY (user_id, tag_id)
```

#### 6. `images` Table
```sql
- image_id (PRIMARY KEY)
- user_id (FOREIGN KEY → users.id)
- image_url (path to image)
- added_at
```

---

## API Endpoints

### 1. Create Profile
```http
POST /api/profile/create_profile
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

FormData:
  - profile_pic: <File>
  - bio: string
  - gender: string
  - sexual_preferences: string
  - age: number
```

**Response:**
```json
{
  "status": "ok"
}
```

### 2. Upload Images
```http
POST /api/profile/upload_images
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

FormData:
  - images: <File[]>
```

### 3. Add Tags
```http
POST /api/profile/add_tags
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "tags": ["Hiking", "Travel", "Music"]
}
```

### 4. Set Location
```http
POST /api/profile/set_location
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "latitude": 40.7128,
  "longitude": -74.0060,
  "accuracy": 50
}
```

---

## Testing Profiles

### Quick Test Setup

1. **Create multiple profiles** for matching tests:
```bash
cd matcha_backend
python create_user_profile.py all
```

This creates 5 diverse profiles:
- Different genders
- Different sexual preferences
- Different locations
- Different interests
- Different ages

2. **Login credentials** (all profiles):
```
Password: Password123!

Profiles:
- alice@example.com
- bob@example.com
- charlie@example.com
- diana@example.com
- ethan@example.com
```

### Test Scenarios

#### Scenario 1: Matching Algorithm
- **Alice** (Female, 28, likes Men) in New York
- **Bob** (Male, 30, likes Women) in Los Angeles
- **Diana** (Female, 32, likes Both) in San Francisco

Test:
- Who appears in Alice's discover page?
- Who appears in Bob's discover page?
- Distance calculations
- Interest matching

#### Scenario 2: Profile Viewing
- Login as Alice
- View Bob's profile
- Check visit tracking
- Check profile picture display
- Verify bio and interests display

#### Scenario 3: Like & Match
- Alice likes Bob
- Bob likes Alice
- Check if connection is created
- Test chat availability

---

## Custom Profile Creation

### Using the Script

```bash
python create_user_profile.py custom
```

Follow prompts:
```
Username: john
Email: john@example.com
Password: Password123!
First name: John
Last name: Doe
Bio: Passionate about technology and travel...
Age: 29
Gender: Male
Sexual preferences: Women
Interests (comma-separated): Technology, Travel, Reading, Music
Add location? (y/n): y
Latitude: 51.5074
Longitude: -0.1278
City: London
Country: UK
```

### Programmatically

```python
from create_user_profile import create_user_profile, create_connection_pool, load_config

config = load_config()
db_pool = create_connection_pool(config)

user_data = {
    "username": "john",
    "email": "john@example.com",
    "password": "Password123!",
    "first_name": "John",
    "last_name": "Doe"
}

profile_data = {
    "bio": "Passionate about technology and travel...",
    "age": 29,
    "gender": "Male",
    "sexual_preferences": "Women",
    "fame_rating": 5
}

interests = ["Technology", "Travel", "Reading", "Music"]

location = {
    "latitude": 51.5074,
    "longitude": -0.1278,
    "city": "London",
    "country": "UK",
    "accuracy": 50
}

user_id, profile_id = create_user_profile(
    db_pool,
    user_data,
    profile_data,
    interests,
    location
)
```

---

## Validation Rules

### Username
- Unique
- Alphanumeric and underscores only
- 3-30 characters

### Email
- Unique
- Valid email format
- Domain must be reachable (for verification)

### Password
- Minimum 8 characters
- Must include: uppercase, lowercase, number, special character

### Bio
- Minimum: Non-empty
- Maximum: 1000 characters

### Age
- Minimum: 18
- Maximum: 120

### Gender
- Must be one of: Female, Male, Non-binary, Other

### Sexual Preferences
- Must be one of: Women, Men, Both, All

### Location
- Latitude: -90 to 90
- Longitude: -180 to 180

### Images
- Formats: JPG, PNG, GIF, WebP
- Maximum size: 5MB per file
- Maximum count: 5 images total

---

## Troubleshooting

### Error: "username or email already exists"
```bash
# Solution: Use a different username/email or delete existing user
# Check existing users:
psql -U your_user -d matcha_db -c "SELECT id, username, email FROM users;"

# Delete user if needed:
psql -U your_user -d matcha_db -c "DELETE FROM users WHERE username='alice';"
```

### Error: "profile already created"
```bash
# Solution: A profile already exists for this user
# Check existing profiles:
psql -U your_user -d matcha_db -c "SELECT * FROM profiles WHERE user_id = 42;"

# Update instead of create, or delete existing profile:
psql -U your_user -d matcha_db -c "DELETE FROM profiles WHERE user_id = 42;"
```

### Error: "Image upload failed"
- Check file permissions on `/matcha_backend/static/profiles/`
- Ensure directory exists
- Check file size (< 5MB)
- Verify file format (JPG, PNG, GIF, WebP)

### Error: "GPS location not available"
- Grant browser location permission
- Use HTTPS (or localhost)
- Fallback to manual entry

---

## Best Practices

### For Development
1. **Use sample profiles** for quick testing
2. **Create diverse profiles** for matching algorithm tests
3. **Use realistic data** for better testing
4. **Clean database** between test runs if needed

### For Production
1. **Remove sample profiles** before deployment
2. **Implement rate limiting** on profile creation
3. **Add image moderation** for uploaded photos
4. **Validate user age** with proper verification
5. **Implement location privacy** settings

---

## Quick Reference

### Create one profile:
```bash
python create_user_profile.py alice
```

### Create all profiles:
```bash
python create_user_profile.py all
```

### Interactive mode:
```bash
python create_user_profile.py
```

### Login credentials:
```
All profiles: Password123!
```

### Test URLs:
```
Profile Setup: http://localhost:3000/profile-step-one
Dashboard: http://localhost:3000/dashboard
```

---

## Date
December 2024

## Status
✅ Working and Tested
