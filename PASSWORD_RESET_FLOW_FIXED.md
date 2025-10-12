# Password Reset Flow - Complete Fix

## Problem
When users requested a password reset:
1. They entered their username on the forgot password page
2. They received an email with a verification link
3. Clicking the link showed "Missing token" error instead of the reset password form

## Root Cause
1. **Wrong email template**: The forgot password flow was using `send_verification_email()` which sent a link to `/verify/{token}` (for email verification) instead of `/confirm_email_reset/{token}` (for password reset)
2. **Missing parameters**: The backend redirect to the reset password page only included the token, but the frontend form required both token AND username
3. **Token not decoded**: The backend wasn't decoding the token to get the email and look up the username before redirecting

## Solution Implemented

### Backend Changes

#### 1. Created `send_reset_password_email()` method in `email_service.py`
- New method specifically for password reset emails
- Uses `password-reset` salt (different from email verification)
- Sends HTML email with proper "Reset Password" branding
- Links to backend endpoint: `/api/auth/confirm_email_reset/{token}`
- Token contains the user's email address

#### 2. Added `confirm_reset_token()` method in `email_service.py`
- Validates password reset tokens using `password-reset` salt
- Returns the email address from the decoded token
- Handles expiration (1 hour timeout)

#### 3. Updated `forgot_password()` in `routes_password.py`
- Changed from: `mail_service.send_verification_email(user['email'], "reset_password")`
- Changed to: `mail_service.send_reset_password_email(user['email'], user['username'])`

#### 4. Fixed `confirm_email_reset()` in `routes_password.py`
- Now decodes the token to get the email: `email = mail_service.confirm_reset_token(token)`
- Looks up user by email: `user = user_crud.get_user_by_email(email=email)`
- Verifies token matches what's stored in database
- Redirects to frontend with BOTH token and username: `/reset-password?token={token}&username={username}`

### Frontend Changes

#### 1. Updated `ressetpassword.js`
- Added `missingParams` check for both token and username
- Shows helpful error message with link back to forgot password page if parameters missing
- Displays username prominently: "Resetting password for: **username**"
- Removed manual username input field (comes from URL now)
- Better error handling and user feedback

#### 2. Updated `ressetpassword.css`
- Added `.rp-subtitle` styling for the username display
- Consistent styling with the rest of the app

## Complete Password Reset Flow (Fixed)

### Step 1: User Request
1. User goes to `/forgot-password`
2. Enters their username
3. Frontend POSTs to `/api/auth/forgot_password`
4. Backend looks up user, generates token with `send_reset_password_email()`
5. Token (containing email) stored in `reset_password_token` column
6. Email sent with link to: `http://localhost:5000/api/auth/confirm_email_reset/{token}`

### Step 2: Email Click
1. User clicks "Reset Password" button in email
2. Browser goes to: `/api/auth/confirm_email_reset/{token}`
3. Backend decodes token → gets email
4. Backend looks up user by email
5. Backend verifies token matches database
6. Backend redirects to: `http://localhost:3000/reset-password?token={token}&username={username}`

### Step 3: Password Reset
1. Frontend shows reset form with username pre-filled
2. User enters new password (twice for confirmation)
3. Frontend POSTs to `/api/auth/reset_password` with:
   - `token`: The reset token
   - `username`: The username from URL
   - `new_password`: New password
4. Backend verifies token matches user's stored token
5. Backend updates password, clears `reset_password_token`
6. User redirected to sign-in page

## Security Features
- Token contains signed email, can't be tampered with
- Token expires after 1 hour
- Token is single-use (cleared after password reset)
- Different salt for password reset vs email verification
- No user enumeration (always returns 200 for forgot password)
- Token must match what's in database (even if signature is valid)

## Testing
To test the complete flow:
```bash
# 1. Start backend
cd matcha_backend
python app.py

# 2. Start frontend
cd matcha-frontend
npm start

# 3. Test flow
# - Go to http://localhost:3000/forgot-password
# - Enter a valid username
# - Check your email
# - Click "Reset Password" button
# - Should see reset password form with username
# - Enter new password
# - Should redirect to sign-in page
```

## Files Modified
- `/matcha_backend/utils/email_service.py` - Added `send_reset_password_email()` and `confirm_reset_token()`
- `/matcha_backend/src/auth/routes_password.py` - Fixed `forgot_password()` and `confirm_email_reset()`
- `/matcha-frontend/src/components/ressetpassword.js` - Better error handling and parameter validation
- `/matcha-frontend/src/components/ressetpassword.css` - Added subtitle styling

## Key Differences: Email Verification vs Password Reset

| Feature | Email Verification | Password Reset |
|---------|-------------------|----------------|
| Salt | `email-confirm` | `password-reset` |
| Token Column | `verification_token` | `reset_password_token` |
| Email Method | `send_verification_email()` | `send_reset_password_email()` |
| Confirm Method | `confirm_email()` | `confirm_reset_token()` |
| Backend Endpoint | `/api/auth/confirm_email/{token}` | `/api/auth/confirm_email_reset/{token}` |
| Frontend Redirect | `/profile-step-one` (after login) | `/reset-password?token=x&username=y` |
| Final Action | Mark user as verified, auto-login | Update password, redirect to sign-in |

## Date
December 2024
