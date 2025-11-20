from typing import List, Dict, Optional
from collections import defaultdict

class MemoryService:
    """
    Service for managing conversational memory using LangChain-style approach
    In-memory storage for conversation history (can be extended to use persistent storage)
    """
    
    def __init__(self):
        # In-memory storage for conversation history
        # Format: {session_id: [{'role': 'user'|'assistant', 'content': '...'}, ...]}
        self.conversations: Dict[str, List[Dict]] = defaultdict(list)
        self.max_history_length = 20  # Keep last 20 messages per session
    
    def add_to_history(self, session_id: str, user_message: str, ai_response: str):
        """
        Add conversation turn to memory
        
        Args:
            session_id: Session identifier
            user_message: User's message
            ai_response: AI's response
        """
        self.conversations[session_id].append({
            'role': 'user',
            'content': user_message
        })
        self.conversations[session_id].append({
            'role': 'assistant',
            'content': ai_response
        })
        
        # Trim history if too long
        if len(self.conversations[session_id]) > self.max_history_length:
            self.conversations[session_id] = self.conversations[session_id][-self.max_history_length:]
    
    def get_conversation_history(self, session_id: str) -> List[Dict]:
        """
        Get conversation history for a session
        
        Args:
            session_id: Session identifier
        
        Returns:
            List of conversation messages
        """
        return self.conversations.get(session_id, [])
    
    def clear_history(self, session_id: str):
        """
        Clear conversation history for a session
        
        Args:
            session_id: Session identifier
        """
        if session_id in self.conversations:
            del self.conversations[session_id]
    
    def get_all_sessions(self) -> List[str]:
        """
        Get all session IDs
        
        Returns:
            List of session IDs
        """
        return list(self.conversations.keys())


