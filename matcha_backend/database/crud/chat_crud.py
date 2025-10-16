import logging
from ..dbmanager import DBManager
from psycopg2 import sql

logger = logging.getLogger(__name__)



class Chat(DBManager):
    def __init__(self, connection_pool):
        super().__init__(connection_pool)
        
    def create_message(self, sender_id, receiver_id, content):
        """Create a new chat message"""
        try:
            # Validate input
            if not content or not content.strip():
                logger.error("Message content cannot be empty")
                return None
            
            # Trim content to reasonable length
            max_length = 5000  # Adjust as needed
            content = content.strip()[:max_length]
            
            data = {
                'sender_id': sender_id,
                'receiver_id': receiver_id,
                'message_text': content,
            }
            
            result = self.insert('messages', data)
            logger.info(f"Message created: {sender_id} -> {receiver_id}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error creating message: {e}")
            return None
    
    def get_conversation(self, user1_id, user2_id, limit=50, offset=0):
            """Get messages between two users, ordered by most recent first"""
            try:
                # Use regular string query with proper parameterization
                query = """
                    SELECT 
                        id,
                        sender_id,
                        receiver_id,
                        message_text,
                        created_at,
                    FROM messages
                    WHERE (sender_id = %s AND receiver_id = %s)
                    OR (sender_id = %s AND receiver_id = %s)
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                """
                
                params = (user1_id, user2_id, user2_id, user1_id, limit, offset)
                messages = self.execute(query, params)
                
                # Format timestamps for JSON serialization
                if messages:
                    for msg in messages:
                        if 'created_at' in msg and msg['created_at']:
                            msg['created_at'] = msg['created_at'].isoformat()
                
                return messages if messages else []
                
            except Exception as e:
                logger.error(f"❌ Error fetching conversation: {e}")
                return []