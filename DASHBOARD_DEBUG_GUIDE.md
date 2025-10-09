# Dashboard Data Fetching - Debugging Guide

## Issues Fixed

### 1. ✅ Missing `user_id` in Profile Response
**Problem**: The Chat component needs `user_id` but it wasn't being returned by the API.
**Fix**: Added `id` and `user_id` fields to `get_profile_data()` in `utils/profile_utils.py`

### 2. ✅ `update_user` Method Only Accepted Username
**Problem**: `routes_profile.py` was calling `update_user(user_data, username=None, user_id=g.user_id)` but the method only accepted `username`.
**Fix**: Updated `database/crud/user_crud.py` to accept both `username` and `user_id` parameters

### 3. ✅ Improved Empty Value Handling
**Problem**: Database fields with NULL or empty strings weren't being handled gracefully.
**Fix**: Changed all dictionary access to use `.get()` with defaults in `get_profile_data()`

### 4. ✅ Added Debug Logging
**Problem**: Hard to see what data is being returned by the API.
**Fix**: Added `console.log` in dashboard.js to show API responses

## Current Dashboard Display Issue

Based on the screenshot showing "Welcome back, xx xx!" with "Fame rating: 5", the likely causes are:

### Scenario 1: User has no first_name/last_name in database
**Check**: Open browser console and look for the log: `"Dashboard - API Response:"`
**Expected**: You should see the full response with all user data

**Solution if first_name/last_name are NULL**:
1. User needs to update their profile with these fields
2. Or the registration process should collect these fields

### Scenario 2: Profile Not Created Yet
**Check**: Console might show error about missing profile
**Solution**: User needs to complete profile creation at `/profile-step-one`

## Testing Steps

### 1. Check API Response
```javascript
// Open browser console (F12)
// Look for: "Dashboard - API Response:"
// Should show:
{
  result: {
    id: 1,
    username: "someuser",
    first_name: "John",  // This might be null or ""
    last_name: "Doe",    // This might be null or ""
    fame_rating: 5,
    profile_picture: null,
    active: false,
    last_seen: null,
    // ... other fields
  }
}
```

### 2. Check Database Directly
```sql
-- Check users table
SELECT id, username, first_name, last_name, email FROM users WHERE id = 1;

-- Check profiles table
SELECT user_id, bio, gender, age, fame_rating, profile_picture FROM profiles WHERE user_id = 1;
```

### 3. Test Profile Update
```bash
# Using curl or Postman
curl -X POST http://localhost:5000/api/profile/update_profile \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "bio": "Test bio",
    "age": 25
  }'
```

## Common Issues & Solutions

### Issue: "Welcome back, xx xx!" (Empty Name)
**Cause**: `first_name` and `last_name` are NULL or empty in database
**Solution**: 
1. Update profile with name fields
2. Check if registration form is saving these fields
3. Dashboard will fallback to username if names are empty

### Issue: Profile Picture Shows "Profile" Text
**Cause**: `profile_picture` field is NULL in database
**Solution**:
1. User needs to upload a profile picture
2. Use the `/api/profile/update_profile_picture` endpoint
3. Dashboard will show fallback avatar if no picture exists

### Issue: Stats Show 0 for Everything
**Cause**: 
- No interactions yet (likes, views, messages)
- Or API calls are failing
**Solution**:
1. Check browser console for errors
2. Verify all API endpoints are working:
   - `/api/profile/get_profile_vistors`
   - `/api/interactions/get_users/likers`
   - `/api/interactions/get_users/liked`
   - `/api/chat/unread_count`

### Issue: API Returns 401/403 Errors
**Cause**: Authentication token expired or invalid
**Solution**:
1. Sign in again
2. Check localStorage for `access_token`
3. Verify token is being sent in Authorization header

## Quick Fixes

### 1. Ensure User Has Profile Data
```javascript
// In browser console on dashboard page:
localStorage.getItem('access_token'); // Should show token

// Then manually update profile:
fetch('http://localhost:5000/api/profile/update_profile', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    first_name: 'John',
    last_name: 'Doe',
    bio: 'Test user',
    age: 25,
    gender: 'male',
    sexual_preferences: 'female'
  })
})
.then(r => r.json())
.then(console.log);
```

### 2. Check Profile Creation
If user has no profile yet, they need to visit `/profile-step-one` and complete the form.

### 3. Verify Backend is Running
```bash
cd /home/khaoula/matcha_1/matcha_backend
python3 app.py
# Should show: Running on http://0.0.0.0:5000
```

### 4. Check CORS Settings
Verify `app.py` has:
```python
CORS(app,
     supports_credentials=True,
     resources={r"/api/*": {"origins": ["http://localhost:3000"]}},
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
```

## API Endpoints to Verify

### Profile Endpoints
- ✅ `GET /api/profile/get_profile/me` - Get my profile
- ✅ `POST /api/profile/update_profile` - Update profile
- ✅ `GET /api/profile/get_profile_pic/me` - Get my profile picture
- ✅ `GET /api/profile/get_profile_vistors` - Get who viewed my profile

### Interactions Endpoints  
- ✅ `GET /api/interactions/get_users/likers` - Who liked me
- ✅ `GET /api/interactions/get_users/liked` - Who I liked

### Chat Endpoints
- ✅ `GET /api/chat/unread_count` - Unread message count

## Next Steps

1. **Check browser console** for the debug log
2. **Verify database has data** for the logged-in user
3. **Update profile** if first_name/last_name are empty
4. **Upload profile picture** if it's NULL
5. **Clear browser cache** and refresh if needed

## Production Recommendations

1. **Remove debug console.log** from dashboard.js before production
2. **Add proper error boundaries** to catch and display errors
3. **Add loading states** for all async operations
4. **Implement profile completion wizard** for new users
5. **Add default values** during user registration for first_name/last_name
