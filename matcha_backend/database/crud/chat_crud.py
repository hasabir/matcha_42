# chat_crud.py

import logging
from datetime import datetime
from ..dbmanager import DBManager

logger = logging.getLogger(__name__)

class Chat(DBManager):
    def __init__(self, connection_pool):
        super().__init__(connection_pool)

    def get_or_create_conversation(self, user1_id, user2_id):
        try:
            user_a, user_b = sorted((user1_id, user2_id))
            result = self.execute(
                """
                SELECT conversation_id FROM conversations
                WHERE (user1_id = %s AND user2_id = %s)
                   OR (user1_id = %s AND user2_id = %s)
                """,
                (user_a, user_b, user_b, user_a),
                fetch=True,
            )
            if result:
                return result[0]['conversation_id']
            conv_result = self.insert('conversations', {
                'user1_id': user_a,
                'user2_id': user_b,
            })
            if conv_result and 'conversation_id' in conv_result:
                return conv_result['conversation_id']
            result = self.execute(
                """
                SELECT conversation_id FROM conversations
                WHERE (user1_id = %s AND user2_id = %s)
                   OR (user1_id = %s AND user2_id = %s)
                """,
                (user_a, user_b, user_b, user_a),
                fetch=True,
            )
            return result[0]['conversation_id'] if result else None
        except Exception as e:
            logger.error(f"Conversation error: {e}")
            return None

    def create_message(self, sender_id, receiver_id, content):
        """
        Create and persist a chat message with explicit commit.
        Returns a dict with id, timestamp, and all message details.
        """
        conn = None
        try:
            # Validate inputs
            if not sender_id or not receiver_id:
                logger.error(f"❌ Invalid user IDs: sender={sender_id}, receiver={receiver_id}")
                return None
                
            if not content or not content.strip():
                logger.error("❌ Message content cannot be empty")
                return None
                
            content = content.strip()[:5000]
            logger.info(f"📝 Creating message: {sender_id} -> {receiver_id}, length={len(content)}")
            
            convo_id = self.get_or_create_conversation(sender_id, receiver_id)
            if not convo_id:
                logger.error(f"❌ Failed to get/create conversation for users {sender_id} and {receiver_id}")
                return None

            logger.info(f"✅ Got conversation_id={convo_id}")

            # Use direct SQL with RETURNING to get complete record in one query
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = """
                INSERT INTO messages (conversation_id, sender_id, message_text)
                VALUES (%s, %s, %s)
                RETURNING message_id, created_at
            """
            logger.info(f"🔄 Executing INSERT with convo_id={convo_id}, sender={sender_id}")
            cursor.execute(query, (convo_id, sender_id, content))
            result = cursor.fetchone()
            conn.commit()  # Explicit commit to ensure persistence
            
            if not result:
                logger.error("❌ Failed to insert message - no result returned")
                return None
                
            msg_id, created_at = result
            logger.info(f"✅ Message persisted: ID={msg_id}, {sender_id} -> {receiver_id}")

            return {
                'id': msg_id,
                'conversation_id': convo_id,
                'sender_id': sender_id,
                'receiver_id': receiver_id,
                'message_text': content,
                'created_at': created_at,
            }
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"❌ Create message error: {e}", exc_info=True)
            return None
        finally:
            if conn:
                self._return_connection(conn)

    def get_conversation(self, user1_id, user2_id, limit=50, offset=0):
        """
        Retrieve all messages between two users, ordered oldest to newest.
        """
        try:
            query = """
                SELECT 
                    m.message_id AS id,
                    m.sender_id,
                    CASE WHEN m.sender_id = %s THEN %s ELSE %s END AS receiver_id,
                    m.message_text,
                    m.created_at
                FROM messages m
                JOIN conversations c ON m.conversation_id = c.conversation_id
                WHERE ((c.user1_id = %s AND c.user2_id = %s)
                    OR (c.user1_id = %s AND c.user2_id = %s))
                ORDER BY m.created_at DESC
                LIMIT %s OFFSET %s
            """
            params = (
                user1_id, user2_id, user1_id,
                user1_id, user2_id,
                user2_id, user1_id,
                limit, offset
            )
            messages = self.execute(query, params, fetch=True)
            
            if messages:
                logger.info(f"📩 Retrieved {len(messages)} messages between users {user1_id} and {user2_id}")
                for msg in messages:
                    if msg.get('created_at'):
                        msg['created_at'] = msg['created_at'].isoformat()
            else:
                logger.info(f"📭 No messages found between users {user1_id} and {user2_id}")
                
            return messages or []
        except Exception as e:
            logger.error(f"❌ Conversation retrieval error: {e}")
            return []



    def update_online_status(self, user_id, is_online, socket_id=None):
        """Update user's online status"""
        try:
            existing = self.execute("""
                SELECT user_id FROM user_online_status WHERE user_id = %s
            """, (user_id,), fetch=True)
            
            if existing:
                self.execute("""
                    UPDATE user_online_status
                    SET is_online = %s, socket_id = %s, 
                        last_seen = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = %s
                """, (is_online, socket_id, user_id))
            else:
                self.execute("""
                    INSERT INTO user_online_status (user_id, is_online, socket_id)
                    VALUES (%s, %s, %s)
                """, (user_id, is_online, socket_id))
            return True
        except Exception as e:
            logger.error(f"Error updating online status: {e}")
            return False

    def get_online_status(self, user_id):
        """Get user's online status"""
        try:
            result = self.execute("""
                SELECT is_online, last_seen FROM user_online_status
                WHERE user_id = %s
            """, (user_id,), fetch=True)
            if result:
                return {
                    'is_online': result[0]['is_online'],
                    'last_seen': result[0]['last_seen'].isoformat() if result[0]['last_seen'] else None
                }
            return {'is_online': False, 'last_seen': None}
        except Exception as e:
            logger.error(f"Error getting online status: {e}")
            return {'is_online': False, 'last_seen': None}

    def update_typing_status(self, user_id, chat_room, is_typing):
        """Update user's typing status in a chat room"""
        try:
            self.execute("""
                INSERT INTO typing_status (user_id, chat_room, is_typing, updated_at)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (user_id, chat_room)
                DO UPDATE SET is_typing = EXCLUDED.is_typing, updated_at = CURRENT_TIMESTAMP
            """, (user_id, chat_room, is_typing))
            return True
        except Exception as e:
            logger.error(f"Error updating typing status: {e}")
            return False

    def get_typing_status(self, chat_room, exclude_user_id):
        """Get typing status for other users in the chat room"""
        try:
            result = self.execute("""
                SELECT user_id, is_typing FROM typing_status
                WHERE chat_room = %s AND user_id != %s AND is_typing = TRUE
                AND updated_at > NOW() - INTERVAL '5 seconds'
            """, (chat_room, exclude_user_id), fetch=True)
            return [row['user_id'] for row in result] if result else []
        except Exception as e:
            logger.error(f"Error getting typing status: {e}")
            return []

