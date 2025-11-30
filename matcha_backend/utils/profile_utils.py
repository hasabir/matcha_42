"""
Profile utility functions
Helper functions for profile management and data retrieval
"""
import logging
from datetime import datetime, timezone
from database.crud.profile_crud import Profile
from database.crud.user_crud import User
from database.crud.location_crud import Location

logger = logging.getLogger(__name__)


def get_profile_data(connection_pool, user_id, include_sensitive=False):
    """
    Get comprehensive profile data for a user
    
    Args:
        connection_pool: Database connection pool
        user_id: User ID to fetch profile for
        include_sensitive: Whether to include sensitive data like email (default: False)
    
    Returns:
        dict: Profile data including user info, profile details, images, etc.
    """
    try:
        profile_crud = Profile(connection_pool)
        user_crud = User(connection_pool)
        location_crud = Location(connection_pool)
        
        # Get basic profile data
        profile = profile_crud.get_profile_by_user_id(user_id)
        
        # Get user data - exclude password always
        if include_sensitive:
            user = user_crud.get_user_by('id', user_id, 'username, first_name, last_name, email, active, last_seen')
        else:
            # Exclude email and other sensitive data when viewing other users
            user = user_crud.get_user_by('id', user_id, 'username, first_name, last_name, active, last_seen')
        
        # Get user images
        images = profile_crud.get_images(user_id)
        
        # Get user tags/interests
        tags = profile_crud.get_user_interests(user_id)
        
        # Get user location
        location = location_crud.get_user_location(user_id)
        
        # Combine all data - flatten user data to top level
        profile_data = {
            **(profile if profile else {}),
            # Ensure user_id is always present
            'user_id': user_id,
            # Flatten user fields to top level for frontend compatibility
            'username': user.get('username') if user else None,
            'first_name': user.get('first_name') if user else None,
            'last_name': user.get('last_name') if user else None,
            'active': user.get('active') if user else False,
            'last_seen': user.get('last_seen') if user else None,
            'images': images if images else [],
            'tags': tags if tags else [],
            # Add location fields directly to profile data for easier access
            'city': location.get('city') if location else None,
            'country': location.get('country') if location else None,
            'latitude': location.get('latitude') if location else None,
            'longitude': location.get('longitude') if location else None,
        }
        
        # Only include email if sensitive data is requested
        if include_sensitive and user:
            profile_data['email'] = user.get('email')
        
        return profile_data
        
    except Exception as e:
        logger.error(f"Error getting profile data for user {user_id}: {str(e)}")
        raise


def houres_between_dates(past_date):
    """
    Calculate hours between a past date and now
    
    Args:
        past_date: Past datetime to compare
    
    Returns:
        int: Number of hours between past_date and now
    """
    if not past_date:
        return None
    
    try:
        # Ensure past_date is timezone-aware
        if past_date.tzinfo is None:
            past_date = past_date.replace(tzinfo=timezone.utc)
        
        # Get current time in UTC
        now = datetime.now(timezone.utc)
        
        # Calculate difference
        time_diff = now - past_date
        
        # Return hours
        hours = int(time_diff.total_seconds() / 3600)
        return hours
        
    except Exception as e:
        logger.error(f"Error calculating hours between dates: {str(e)}")
        return None


def format_last_seen(last_seen_datetime):
    """
    Format last seen datetime into a human-readable string
    
    Args:
        last_seen_datetime: DateTime object
    
    Returns:
        str: Human-readable last seen string
    """
    if not last_seen_datetime:
        return "Never"
    
    hours = houres_between_dates(last_seen_datetime)
    
    if hours is None:
        return "Unknown"
    
    if hours < 1:
        return "Just now"
    elif hours < 24:
        return f"{hours} hours ago"
    elif hours < 48:
        return "Yesterday"
    else:
        days = hours // 24
        return f"{days} days ago"
