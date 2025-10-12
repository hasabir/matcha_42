# User Authentication Flow with Conditional Redirects

This document describes the implementation of user authentication flow with conditional redirects based on user state and profile completion status.

## Overview

The authentication system now supports conditional redirects based on:
1. Whether it's the user's first login
2. Whether the user has completed their profile setup
3. Whether the user is authenticated (for logo clicks)

## Database Changes

### Users Table
Added `first_login` boolean column to track if it's the user's first login:
```sql
ALTER TABLE users ADD COLUMN first_login BOOLEAN DEFAULT TRUE;
```

## API Endpoints

### 1. POST /api/auth/login
Enhanced login endpoint that now returns redirect information.

**Request:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "jwt_token",
  "redirect_to": "setupProfile|home", 
  "first_login": boolean,
  "profile_completed": boolean
}
```

**Redirect Logic:**
- If `first_login` is `true` OR `profile_completed` is `false` → redirect to `setupProfile`
- If `first_login` is `false` AND `profile_completed` is `true` → redirect to `home`

### 2. GET /api/auth/profile-status
Get detailed profile status for authenticated users.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "first_login": boolean,
  "profile_completed": boolean,
  "profile_has_essentials": boolean,
  "redirect_to": "setupProfile|home",
  "should_show_setup": boolean,
  "profile_details": {
    "profile_exists": boolean,
    "has_essentials": boolean,
    "has_images": boolean,
    "has_interests": boolean,
    "is_completed": boolean,
    "image_count": number,
    "interest_count": number
  }
}
```

### 3. GET /api/auth/logo-redirect
Handle logo click redirects based on authentication status.

**Headers (Optional):**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "redirect_to": "landing|home"
}
```

**Logic:**
- If user is authenticated (valid token) → redirect to `home`
- If user is not authenticated (no token/invalid token) → redirect to `landing`

## Profile Completion Criteria

A profile is considered "completed" when:
1. **Profile exists** in the database
2. **Essential fields are filled:**
   - `bio` (not null, not empty)
   - `age` (not null, not empty)
   - `gender` (not null, not empty)  
   - `sexual_preferences` (not null, not empty)
3. **Has at least one image** uploaded

## Authentication Flow Scenarios

### 1. First Sign-Up/Sign-In
```
User registers → Email verification → First login → first_login=true → Redirect to /setupProfile
```

### 2. Subsequent Logins (Incomplete Profile)
```
User logs in → first_login=false, profile_completed=false → Redirect to /setupProfile
```

### 3. Subsequent Logins (Complete Profile)
```
User logs in → first_login=false, profile_completed=true → Redirect to /home
```

### 4. Logo Click (Authenticated User)
```
User clicks logo → Valid token → Redirect to /home
```

### 5. Logo Click (Unauthenticated User)
```
User clicks logo → No token/Invalid token → Redirect to /landing
```

## Implementation Details

### Backend Changes
1. **Database Schema:** Added `first_login` column to users table
2. **User Model:** Added methods for profile completion checking
3. **Profile Model:** Added `is_profile_completed()` and `get_profile_completion_status()` methods
4. **Auth Routes:** Enhanced with conditional redirect logic

### First Login Tracking
- `first_login` is set to `TRUE` by default for new users
- Set to `FALSE` after the first successful login
- Only updates from `TRUE` to `FALSE`, never back to `TRUE`

### Profile Completion Logic
- Checks essential profile fields (bio, age, gender, sexual_preferences)
- Verifies at least one image is uploaded
- Returns detailed status for frontend use

## Testing Results

✅ **First Login Flow:** New user redirects to setupProfile  
✅ **Subsequent Login (Incomplete):** Redirects to setupProfile  
✅ **Subsequent Login (Complete):** Redirects to home  
✅ **Logo Click (Authenticated):** Redirects to home  
✅ **Logo Click (Unauthenticated):** Redirects to landing  
✅ **Profile Status Endpoint:** Returns accurate completion status  
✅ **First Login Flag:** Properly updates after first login  

## Frontend Integration

The frontend should:
1. **After login:** Check the `redirect_to` field and navigate accordingly
2. **Logo clicks:** Call `/api/auth/logo-redirect` and navigate based on response
3. **Profile setup:** Use `/api/auth/profile-status` to show progress and determine completion
4. **Session management:** Handle token refresh and authentication state properly

## Error Handling

- **Invalid/Expired Tokens:** Return 401 with appropriate error message
- **Missing Authorization:** Return 401 for protected endpoints
- **Database Errors:** Return 500 with error details
- **User Not Found:** Return 404 for profile status requests

## Security Considerations

- All profile status endpoints require valid JWT authentication
- Logo redirect endpoint gracefully handles missing/invalid tokens
- No sensitive user data exposed in redirect responses
- Token expiration properly handled with appropriate HTTP status codes