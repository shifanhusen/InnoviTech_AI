"""
Conversation memory management using Redis.
"""
import json
from redis import Redis
from app.core.config import settings
from app.utils.logger import logger


class MemoryService:
    """Manages conversation history in Redis with TTL-based expiration."""
    
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.ttl = settings.SESSION_TTL_SECONDS
        self.max_messages = settings.MAX_HISTORY_MESSAGES
    
    def _get_key(self, session_id: str) -> str:
        """Generate Redis key for a session."""
        return f"session:{session_id}"
    
    def get_history(self, session_id: str) -> list[dict]:
        """
        Retrieve conversation history for a session.
        
        Args:
            session_id: Unique session identifier
        
        Returns:
            List of message dictionaries with 'role' and 'content' keys
        """
        key = self._get_key(session_id)
        try:
            data = self.redis.get(key)
            if data is None:
                logger.debug(f"No history found for session {session_id}")
                return []
            history = json.loads(data)
            logger.debug(f"Retrieved {len(history)} messages for session {session_id}")
            return history
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Error decoding history for session {session_id}: {e}")
            return []
    
    def append_message(self, session_id: str, role: str, content: str) -> None:
        """
        Append a message to the conversation history and refresh TTL.
        
        Args:
            session_id: Unique session identifier
            role: Message role ('user' or 'assistant')
            content: Message content
        """
        key = self._get_key(session_id)
        
        # Get existing history
        history = self.get_history(session_id)
        
        # Append new message
        history.append({
            "role": role,
            "content": content
        })
        
        # Keep only last N messages
        if len(history) > self.max_messages:
            history = history[-self.max_messages:]
        
        # Save back to Redis with TTL
        try:
            self.redis.setex(
                key,
                self.ttl,
                json.dumps(history)
            )
            logger.debug(f"Appended {role} message to session {session_id}, TTL refreshed")
        except Exception as e:
            logger.error(f"Error saving history for session {session_id}: {e}")
            raise
    
    def reset_session(self, session_id: str) -> None:
        """
        Clear all conversation history for a session.
        
        Args:
            session_id: Unique session identifier
        """
        key = self._get_key(session_id)
        try:
            deleted = self.redis.delete(key)
            if deleted:
                logger.info(f"Session {session_id} reset successfully")
            else:
                logger.info(f"Session {session_id} did not exist")
        except Exception as e:
            logger.error(f"Error resetting session {session_id}: {e}")
            raise
    
    def session_exists(self, session_id: str) -> bool:
        """
        Check if a session exists in Redis.
        
        Args:
            session_id: Unique session identifier
        
        Returns:
            True if session exists, False otherwise
        """
        key = self._get_key(session_id)
        return self.redis.exists(key) > 0
