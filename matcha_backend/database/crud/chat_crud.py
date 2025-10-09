"""
Chat CRUD operations for the Matcha dating app.
Handles conversations and messages between matched users.
"""
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)


class Chat:
    def __init__(self, connection_pool):
        self.connection_pool = connection_pool

    def get_or_create_conversation(self, user1_id: int, user2_id: int) -> Optional[int]:
        """
        Get existing conversation between two users or create a new one.
        Ensures user1_id < user2_id for consistency.
        Returns: conversation_id or None
        """
        # Normalize order to ensure consistency
        if user1_id > user2_id:
            user1_id, user2_id = user2_id, user1_id

        conn = self.connection_pool.getconn()
        try:
            with conn.cursor() as cursor:
                # Check if conversation exists
                cursor.execute("""
                    SELECT conversation_id FROM conversations
                    WHERE (user1_id = %s AND user2_id = %s)
                       OR (user1_id = %s AND user2_id = %s)
                """, (user1_id, user2_id, user2_id, user1_id))
                
                result = cursor.fetchone()
                if result:
                    return result[0]
                
                # Create new conversation
                cursor.execute("""
                    INSERT INTO conversations (user1_id, user2_id, created_at)
                    VALUES (%s, %s, %s)
                    RETURNING conversation_id
                """, (user1_id, user2_id, datetime.now(timezone.utc)))
                
                conn.commit()
                new_id = cursor.fetchone()
                return new_id[0] if new_id else None
                
        except Exception as e:
            conn.rollback()
            logger.exception(f"Error in get_or_create_conversation: {e}")
            return None
        finally:
            self.connection_pool.putconn(conn)

    def send_message(self, conversation_id: int, sender_id: int, message_text: str) -> Optional[Dict]:
        """
        Send a message in a conversation.
        Returns: message dict or None
        """
        if not message_text or not message_text.strip():
            logger.warning("Attempted to send empty message")
            return None

        conn = self.connection_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO messages (conversation_id, sender_id, message_text, status, created_at)
                    VALUES (%s, %s, %s, FALSE, %s)
                    RETURNING message_id, conversation_id, sender_id, message_text, status, created_at
                """, (conversation_id, sender_id, message_text.strip(), datetime.now(timezone.utc)))
                
                conn.commit()
                row = cursor.fetchone()
                
                if row:
                    return {
                        "message_id": row[0],
                        "conversation_id": row[1],
                        "sender_id": row[2],
                        "message_text": row[3],
                        "status": row[4],
                        "created_at": row[5].isoformat() if row[5] else None
                    }
                return None
                
        except Exception as e:
            conn.rollback()
            logger.exception(f"Error sending message: {e}")
            return None
        finally:
            self.connection_pool.putconn(conn)

    def get_conversation_messages(self, conversation_id: int, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        Get messages from a conversation, ordered by time (newest last).
        Returns: list of message dicts
        """
        conn = self.connection_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT message_id, conversation_id, sender_id, message_text, status, created_at
                    FROM messages
                    WHERE conversation_id = %s
                    ORDER BY created_at ASC
                    LIMIT %s OFFSET %s
                """, (conversation_id, limit, offset))
                
                rows = cursor.fetchall()
                return [
                    {
                        "message_id": row[0],
                        "conversation_id": row[1],
                        "sender_id": row[2],
                        "message_text": row[3],
                        "status": row[4],  # read status
                        "created_at": row[5].isoformat() if row[5] else None
                    }
                    for row in rows
                ]
                
        except Exception as e:
            logger.exception(f"Error getting conversation messages: {e}")
            return []
        finally:
            self.connection_pool.putconn(conn)

    def get_user_conversations(self, user_id: int) -> List[Dict]:
        """
        Get all conversations for a user with last message info.
        Returns: list of conversation dicts with other user info and last message
        """
        conn = self.connection_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        c.conversation_id,
                        c.user1_id,
                        c.user2_id,
                        c.created_at,
                        m.message_text as last_message,
                        m.created_at as last_message_at,
                        m.sender_id as last_sender_id,
                        (SELECT COUNT(*) FROM messages 
                         WHERE conversation_id = c.conversation_id 
                         AND sender_id != %s 
                         AND status = FALSE) as unread_count
                    FROM conversations c
                    LEFT JOIN LATERAL (
                        SELECT message_text, created_at, sender_id
                        FROM messages
                        WHERE conversation_id = c.conversation_id
                        ORDER BY created_at DESC
                        LIMIT 1
                    ) m ON TRUE
                    WHERE c.user1_id = %s OR c.user2_id = %s
                    ORDER BY m.created_at DESC NULLS LAST
                """, (user_id, user_id, user_id))
                
                rows = cursor.fetchall()
                conversations = []
                
                for row in rows:
                    # Determine the other user
                    other_user_id = row[2] if row[1] == user_id else row[1]
                    
                    conversations.append({
                        "conversation_id": row[0],
                        "other_user_id": other_user_id,
                        "created_at": row[3].isoformat() if row[3] else None,
                        "last_message": row[4],
                        "last_message_at": row[5].isoformat() if row[5] else None,
                        "last_sender_id": row[6],
                        "unread_count": row[7] or 0
                    })
                
                return conversations
                
        except Exception as e:
            logger.exception(f"Error getting user conversations: {e}")
            return []
        finally:
            self.connection_pool.putconn(conn)

    def mark_messages_as_read(self, conversation_id: int, user_id: int) -> bool:
        """
        Mark all messages in a conversation as read for the given user.
        Only marks messages sent by the other user.
        Returns: True if successful
        """
        conn = self.connection_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE messages
                    SET status = TRUE
                    WHERE conversation_id = %s
                    AND sender_id != %s
                    AND status = FALSE
                """, (conversation_id, user_id))
                
                conn.commit()
                return True
                
        except Exception as e:
            conn.rollback()
            logger.exception(f"Error marking messages as read: {e}")
            return False
        finally:
            self.connection_pool.putconn(conn)

    def get_unread_message_count(self, user_id: int) -> int:
        """
        Get total number of unread messages for a user across all conversations.
        Returns: count
        """
        conn = self.connection_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM messages m
                    JOIN conversations c ON m.conversation_id = c.conversation_id
                    WHERE (c.user1_id = %s OR c.user2_id = %s)
                    AND m.sender_id != %s
                    AND m.status = FALSE
                """, (user_id, user_id, user_id))
                
                result = cursor.fetchone()
                return result[0] if result else 0
                
        except Exception as e:
            logger.exception(f"Error getting unread message count: {e}")
            return 0
        finally:
            self.connection_pool.putconn(conn)

    def conversation_exists(self, conversation_id: int) -> bool:
        """Check if a conversation exists."""
        conn = self.connection_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 1 FROM conversations WHERE conversation_id = %s
                """, (conversation_id,))
                return cursor.fetchone() is not None
        except Exception as e:
            logger.exception(f"Error checking conversation existence: {e}")
            return False
        finally:
            self.connection_pool.putconn(conn)

    def user_in_conversation(self, conversation_id: int, user_id: int) -> bool:
        """Check if a user is part of a conversation."""
        conn = self.connection_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 1 FROM conversations
                    WHERE conversation_id = %s
                    AND (user1_id = %s OR user2_id = %s)
                """, (conversation_id, user_id, user_id))
                return cursor.fetchone() is not None
        except Exception as e:
            logger.exception(f"Error checking user in conversation: {e}")
            return False
        finally:
            self.connection_pool.putconn(conn)
