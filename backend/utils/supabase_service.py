from supabase import create_client, Client
from typing import List, Dict, Optional
from config import Config
from datetime import datetime

class SupabaseService:
    """Service for interacting with Supabase database"""
    
    def __init__(self):
        if not Config.SUPABASE_URL or not Config.SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        # Use modern Supabase SDK without proxy parameter
        try:
            self.client: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
            self.table_name = 'conversations'
            self._ensure_table_exists()
        except Exception as e:
            raise ValueError(f"Failed to initialize Supabase client: {e}")
    
    def _ensure_table_exists(self):
        """Ensure conversations table exists (manual setup required in Supabase)"""
        # Note: Table creation should be done manually in Supabase dashboard
        # This is a placeholder for table structure documentation
        pass
    
    def save_conversation(
        self,
        session_id: str,
        document_id: str,
        user_message: str,
        ai_response: str,
        audio_path: str,
        language: str = 'en'
    ):
        """
        Save conversation turn to Supabase
        
        Args:
            session_id: Session identifier
            document_id: Document identifier
            user_message: User's message
            ai_response: AI's response
            audio_path: Path to audio file
            language: Language code
        """
        try:
            data = {
                'session_id': session_id,
                'document_id': document_id,
                'user_message': user_message,
                'ai_response': ai_response,
                'audio_path': audio_path,
                'language': language,
                'created_at': datetime.now().isoformat()
            }
            
            self.client.table(self.table_name).insert(data).execute()
        except Exception as e:
            print(f"Error saving conversation to Supabase: {e}")
            # Don't raise - allow conversation to continue even if DB save fails
            pass
    
    def get_conversation_history(self, session_id: str) -> List[Dict]:
        """
        Retrieve conversation history for a session
        
        Args:
            session_id: Session identifier
        
        Returns:
            List of conversation messages
        """
        try:
            response = self.client.table(self.table_name)\
                .select('*')\
                .eq('session_id', session_id)\
                .order('created_at', desc=False)\
                .execute()
            
            return response.data if response.data else []
        except Exception as e:
            print(f"Error retrieving conversation history: {e}")
            return []
    
    def get_sessions_by_document(self, document_id: str) -> List[Dict]:
        """
        Get all sessions for a document
        
        Args:
            document_id: Document identifier
        
        Returns:
            List of session data
        """
        try:
            response = self.client.table(self.table_name)\
                .select('session_id')\
                .eq('document_id', document_id)\
                .execute()
            
            # Get unique session IDs
            session_ids = list(set([row['session_id'] for row in response.data]))
            return [{'session_id': sid} for sid in session_ids]
        except Exception as e:
            print(f"Error retrieving sessions: {e}")
            return []


