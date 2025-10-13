# create_user_profile.py

Automated user profile creation script for Matcha dating app testing.

## Usage

```bash
# Create a specific profile
python3 create_user_profile.py alice

# Create all sample profiles
python3 create_user_profile.py all

# Interactive mode
python3 create_user_profile.py
```

## Sample Profiles

- **alice** - Female, 28, New York
- **bob** - Male, 30, Los Angeles  
- **charlie** - Non-binary, 26, London
- **diana** - Female, 32, San Francisco
- **ethan** - Male, 27, Paris

All profiles use password: `Password123!`

## Requirements

- PostgreSQL database running
- Database schema loaded
- Python packages: `psycopg2-binary`, `pyyaml`
- Config file: `build/config.yml`

## Features

Creates complete profiles with:
- ✅ User account (username, email, password)
- ✅ Profile (bio, age, gender, preferences)
- ✅ Interests/tags
- ✅ GPS location
- ✅ Default profile picture

## Documentation

See full docs at: `/USER_PROFILE_CREATION_GUIDE.md`
