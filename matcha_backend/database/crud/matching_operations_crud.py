"""
Matching operations CRUD module
Handles matching between users based on mutual likes
"""
import logging
from ..dbmanager import DBManager

logger = logging.getLogger(__name__)


class Matching(DBManager):
    """Handle matching operations between users"""
    
    def __init__(self, connection_pool):
        super().__init__(connection_pool)
    
    def are_matched(self, user_id, other_user_id):
        """
        Check if two users are matched (mutual likes)
        
        Args:
            user_id: First user ID
            other_user_id: Second user ID
        
        Returns:
            bool: True if users have mutual likes
        """
        try:
            # Check if both users have liked each other
            query = """
                SELECT COUNT(*) as count FROM likes l1
                WHERE l1.liker_id = %s AND l1.liked_id = %s
                AND EXISTS (
                    SELECT 1 FROM likes l2
                    WHERE l2.liker_id = %s AND l2.liked_id = %s
                )
            """
            result = self.execute(query, (user_id, other_user_id, other_user_id, user_id), fetch=True)
            return result[0]['count'] > 0 if result else False
        except Exception as e:
            logger.error(f"Error checking if users are matched: {str(e)}")
            return False
    
    def create_match(self, user_id, other_user_id):
        """
        Create a match record when two users like each other
        
        Args:
            user_id: First user ID
            other_user_id: Second user ID
        
        Returns:
            bool: True if match was created successfully
        """
        conn = None
        try:
            # Ensure IDs are in a consistent order (smaller ID first)
            user_1 = min(user_id, other_user_id)
            user_2 = max(user_id, other_user_id)
            
            # Check if match already exists
            existing = self.select(
                'connections',
                where='user1_id = %s AND user2_id = %s',
                where_params=(user_1, user_2)
            )
            
            if existing:
                logger.debug(f"Match already exists between {user_1} and {user_2}")
                return False
            
            # Insert match record using direct connection
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = """
                INSERT INTO connections (user1_id, user2_id, connected_at)
                VALUES (%s, %s, NOW())
            """
            cursor.execute(query, (user_1, user_2))
            conn.commit()
            
            # Create conversation for the match
            from database.crud.chat_crud import Chat
            chat_crud = Chat(self.connection_pool)
            conversation_id = chat_crud.get_or_create_conversation(user_1, user_2)
            
            logger.info(f"✅ Match created between {user_1} and {user_2}, conversation: {conversation_id}")
            return True
            
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"❌ Error creating match: {str(e)}")
            return False
        finally:
            if conn:
                self._return_connection(conn)
    
    def unmatche(self, user_id, other_user_id):
        """
        Remove a match between two users (unmatch/unmatche)
        
        Args:
            user_id: First user ID
            other_user_id: Second user ID
        
        Returns:
            int: Number of rows deleted
        """
        try:
            # Ensure IDs are in a consistent order
            user_1 = min(user_id, other_user_id)
            user_2 = max(user_id, other_user_id)
            
            # Delete connection record
            return self.delete(
                'connections',
                where='user1_id = %s AND user2_id = %s',
                where_params=(user_1, user_2)
            )
        except Exception as e:
            logger.error(f"Error unmatching users: {str(e)}")
            return 0
    
    def get_matched_users(self, user_id):
        """
        Get all users that are matched with the given user
        
        Args:
            user_id: User ID to get matches for
        
        Returns:
            list: List of matched user IDs
        """
        try:
            query = """
                SELECT 
                    CASE 
                        WHEN user1_id = %s THEN user2_id
                        ELSE user1_id
                    END as matched_user_id
                FROM connections
                WHERE user1_id = %s OR user2_id = %s
            """
            result = self.execute(query, (user_id, user_id, user_id), fetch=True)
            return [row['matched_user_id'] for row in result] if result else []
        except Exception as e:
            logger.error(f"Error getting matched users: {str(e)}")
            return []
    
    def get_match_details(self, user_id, other_user_id):
        """
        Get match details between two users
        
        Args:
            user_id: First user ID
            other_user_id: Second user ID
        
        Returns:
            dict: Match details or None
        """
        try:
            user_1 = min(user_id, other_user_id)
            user_2 = max(user_id, other_user_id)
            
            result = self.select(
                'connections',
                where='user1_id = %s AND user2_id = %s',
                where_params=(user_1, user_2)
            )
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error getting match details: {str(e)}")
            return None
    
    def check_and_create_match(self, user_id, other_user_id):
        """
        Check if a like creates a match and create it if so
        
        Args:
            user_id: User who liked
            other_user_id: User who was liked
        
        Returns:
            bool: True if a new match was created
        """
        try:
            # Check if other user has already liked this user
            if self.are_matched(user_id, other_user_id):
                # They're already matched, no need to create again
                return False
            
            # Check if this like creates a new match
            query = """
                SELECT COUNT(*) as count FROM likes
                WHERE liker_id = %s AND liked_id = %s
            """
            result = self.execute(query, (other_user_id, user_id), fetch=True)
            
            if result and result[0]['count'] > 0:
                # Other user has liked back, create match
                self.create_match(user_id, other_user_id)
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking and creating match: {str(e)}")
            return False
