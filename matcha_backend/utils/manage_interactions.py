import logging

from database.crud.interactions_crud import Interactions
from database.crud.matching_operations_crud import Matching
from database.crud.profile_crud import Profile


logger = logging.getLogger(__name__)
class ManageInteractions():
    def __init__(self, connection_pool, intractions_crud):
        self.connection_pool = connection_pool
        self.interactions_crud = intractions_crud

    def connect_users(self, user_id, other_user_id):
        """
        Create a match/connection between two users.
        This is called when both users have liked each other.
        
        Args:
            user_id: First user ID
            other_user_id: Second user ID
        
        Returns:
            bool: True if match was created successfully
        """
        try:
            matching_crud = Matching(self.connection_pool)
            match_created = matching_crud.create_match(user_id, other_user_id)
            
            if match_created:
                # Increment matches count for both users
                profile_crud = Profile(self.connection_pool)
                profile_crud.increment_matches_count(user_id)
                profile_crud.increment_matches_count(other_user_id)
                logger.info(f"✅ Match created via connect_users: {user_id} ↔ {other_user_id}")
                return True
            else:
                logger.debug(f"Match already exists between {user_id} and {other_user_id}")
                return False
        except Exception as e:
            logger.error(f"❌ Error in connect_users: {e}")
            return False

    def check_action(self, user_id, liked_id):
        """
        Check what action should be taken when a user likes/dislikes another user.
        
        Returns:
            str: "match" if mutual like creates a match, "like" for new like, "dislike" for unlike
        """
        liked_users = self.interactions_crud.get_user_likes()
        logger.debug(f"👉👉👉👉{liked_users}👈👈👈👈")
        
        # Check if user has already liked this person
        if not liked_users or liked_id not in liked_users:
            # New like - check if it creates a match
            if self.interactions_crud.is_liked_by():
                # It's a mutual like! Create match and increment counters
                matching_crud = Matching(self.connection_pool)
                match_created = matching_crud.create_match(user_id, liked_id)
                
                if match_created:
                    # Increment matches count for both users
                    profile_crud = Profile(self.connection_pool)
                    profile_crud.increment_matches_count(user_id)
                    profile_crud.increment_matches_count(liked_id)
                    logger.info(f"✅ Match created between {user_id} and {liked_id}")
                
                return "match"
            return "like"
        
        # User is unliking/disliking - remove from matches if they were matched
        matching_crud = Matching(self.connection_pool)
        matched_users_ids = matching_crud.get_matched_users(user_id)
        
        if matched_users_ids and liked_id in matched_users_ids:
            # Remove the match and decrement counters
            matching_crud.unmatche(user_id, liked_id)
            profile_crud = Profile(self.connection_pool)
            profile_crud.decrement_matches_count(user_id)
            profile_crud.decrement_matches_count(liked_id)
            logger.info(f"🔄 Unmatched {user_id} and {liked_id}")
        
        return "dislike"
