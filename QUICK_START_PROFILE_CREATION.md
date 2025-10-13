# Quick Start: Create User Profile

## ✨ I've created a powerful profile creation tool for you!

### 📁 Location
```
/matcha_backend/create_user_profile.py
```

### 🚀 Quick Start

#### Step 1: Activate Backend Environment
```bash
cd /home/khaoula/matcha_1/matcha_backend
source venv/bin/activate  # or your virtual environment
```

#### Step 2: Create a Profile
```bash
# Create Alice's profile
python3 create_user_profile.py alice

# Or create all 5 sample profiles
python3 create_user_profile.py all

# Or use interactive mode
python3 create_user_profile.py
```

### 👥 Available Sample Profiles

| Username | Gender | Age | Location | Interests |
|----------|--------|-----|----------|-----------|
| **alice** | Female | 28 | New York, USA | Hiking, Travel, Coffee, Photography |
| **bob** | Male | 30 | Los Angeles, USA | Coding, Fitness, Gaming, Music |
| **charlie** | Non-binary | 26 | London, UK | Art, Cooking, Music, Photography |
| **diana** | Female | 32 | San Francisco, USA | Yoga, Hiking, Reading, Cooking |
| **ethan** | Male | 27 | Paris, France | Music, Movies, Gaming, Travel |

### 🔑 Login Credentials
**All profiles use the same password:**
```
Password: Password123!
```

Examples:
- Email: `alice@example.com`, Password: `Password123!`
- Email: `bob@example.com`, Password: `Password123!`
- etc.

### 📝 What Gets Created

For each profile, the script creates:
1. ✅ **User account** (username, email, password)
2. ✅ **Profile** (bio, age, gender, preferences)
3. ✅ **Interests/Tags** (e.g., Hiking, Travel, Cooking)
4. ✅ **Location** (GPS coordinates, city, country)
5. ✅ **Default profile picture path**

### 🎯 Example Output

```bash
$ python3 create_user_profile.py alice

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

============================================================
```

### 🎨 Interactive Mode

Run without arguments for interactive prompts:

```bash
python3 create_user_profile.py
```

You'll see:
```
============================================================
  🎭 Matcha User Profile Creator
============================================================

📋 Available sample profiles:
------------------------------------------------------------

🔹 ALICE
   Name: Alice Johnson
   Age: 28, Gender: Female
   Interests: Hiking, Travel, Coffee...
   Location: New York, USA

🔹 BOB
   Name: Bob Smith
   Age: 30, Gender: Male
   Interests: Coding, Fitness, Gaming...
   Location: Los Angeles, USA

... (more profiles)

------------------------------------------------------------

Options:
  1. Create a specific profile (enter name)
  2. Create all profiles (enter 'all')
  3. Custom profile (enter 'custom')
  4. Exit (enter 'exit')

Your choice: _
```

### 🔧 Custom Profile Creation

Choose 'custom' in interactive mode:

```
Your choice: custom

🎨 Custom Profile Creator
------------------------------------------------------------
Username: john
Email: john@example.com
Password: MySecret123!
First name: John
Last name: Doe
Bio: Passionate about technology and travel
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

### 🎪 Alternative: Use the Web Interface

If you prefer, you can create profiles through the web interface:

1. **Register a new user:**
   ```
   http://localhost:3000/register
   ```

2. **Verify email** (click link in email)

3. **Complete profile setup:**
   ```
   http://localhost:3000/profile-step-one
   ```

4. **Fill in:**
   - Gender
   - Sexual preferences
   - Bio
   - Age & Location
   - Interests
   - Upload photos

5. **Click "Next"** → Profile created!

### 📊 Database Check

After creating profiles, verify in database:

```bash
# Connect to database
psql -U your_user -d matcha_db

# Check users
SELECT id, username, email, verified, active FROM users;

# Check profiles
SELECT profile_id, user_id, gender, age, fame_rating FROM profiles;

# Check tags
SELECT u.username, t.tag_name 
FROM users u
JOIN user_tags ut ON u.id = ut.user_id
JOIN tags t ON ut.tag_id = t.tag_id
ORDER BY u.username;

# Check locations
SELECT u.username, ul.city, ul.country, ul.latitude, ul.longitude
FROM users u
JOIN user_locations ul ON u.id = ul.user_id;
```

### 🧪 Test Scenarios

#### Scenario 1: Create and Login
```bash
# Create Alice
python3 create_user_profile.py alice

# Login at http://localhost:3000/signin
# Email: alice@example.com
# Password: Password123!
```

#### Scenario 2: Create Multiple for Matching
```bash
# Create all profiles
python3 create_user_profile.py all

# Now you have 5 users in different locations
# Test matching algorithm, distance calculation, etc.
```

#### Scenario 3: Test Like/Match Flow
```bash
# Create Alice and Bob
python3 create_user_profile.py alice
python3 create_user_profile.py bob

# Login as Alice → Like Bob's profile
# Login as Bob → Like Alice's profile
# Check if connection (match) is created
```

### ⚠️ Important Notes

1. **Database must be running** before using the script
2. **Schema must be loaded** (tables must exist)
3. **Config file** must be present at `build/config.yml`
4. **Virtual environment** should be activated
5. **Dependencies** must be installed (`psycopg2`, `pyyaml`, etc.)

### 🐛 Troubleshooting

**Error: "ModuleNotFoundError: No module named 'psycopg2'"**
```bash
pip install psycopg2-binary pyyaml
```

**Error: "username or email already exists"**
```bash
# Delete existing user first
psql -U your_user -d matcha_db -c "DELETE FROM users WHERE username='alice';"
```

**Error: "Database connection pool is not available"**
```bash
# Check if database is running
sudo systemctl status postgresql

# Check config file
cat build/config.yml
```

### 🎉 Success!

Once profiles are created, you can:
- ✅ Login with any profile
- ✅ View dashboard
- ✅ Browse other profiles
- ✅ Test matching algorithm
- ✅ Test like/match/chat features

### 📚 Full Documentation

For complete details, see:
```
/home/khaoula/matcha_1/USER_PROFILE_CREATION_GUIDE.md
```

---

## 🚀 TL;DR - Just Do This

```bash
cd /home/khaoula/matcha_1/matcha_backend
source venv/bin/activate  # or your venv
python3 create_user_profile.py all
```

Then login at `http://localhost:3000/signin` with:
- Email: `alice@example.com`
- Password: `Password123!`

**Done!** 🎊

---

Date: December 2024
