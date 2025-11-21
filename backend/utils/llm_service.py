from openai import OpenAI
from typing import List, Dict, Optional
from config import Config
from utils.translator import TranslatorService

# System prompt that enforces strict textbook-only answers
SYSTEM_PROMPT = """You are an AI Tutor. You MUST answer strictly and ONLY using the textbook content provided in the context. 

If the answer does not exist in the textbook, say:

"Sorry, the textbook does not contain this information."

Do not guess. Do not hallucinate. Do not add extra information beyond the textbook context."""


class LLMService:
    """Service for interacting with OpenAI Chat Completions API"""
    
    def __init__(self):
        if not Config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in environment variables")
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_CHAT_MODEL
        self.translator = TranslatorService()
    
    def generate_response(
        self,
        user_message: str,
        context: str,
        conversation_history: Optional[List[Dict]] = None,
        language: str = 'en'
    ) -> str:
        """
        Generate AI response using OpenAI Chat Completions
        
        Args:
            user_message: User's question/message
            context: Retrieved context from vector database
            conversation_history: Previous conversation messages
            language: Language code for response (e.g., 'en-IN', 'hi', 'ta', etc.)
        
        Returns:
            AI-generated response text
        """
        try:
            # If no context, return immediately
            if not context or not context.strip():
                return "Sorry, the textbook does not contain this information."
            
            # Map language codes to language names for the prompt
            language_map = {
                'en-IN': 'English',
                'en': 'English',
                'hi': 'Hindi',
                'hi-IN': 'Hindi',
                'ta': 'Tamil',
                'ta-IN': 'Tamil',
                'te': 'Telugu',
                'te-IN': 'Telugu',
                'kn': 'Kannada',
                'kn-IN': 'Kannada',
                'ml': 'Malayalam',
                'ml-IN': 'Malayalam',
                'mr': 'Marathi',
                'mr-IN': 'Marathi',
                'gu': 'Gujarati',
                'gu-IN': 'Gujarati',
                'bn': 'Bengali',
                'bn-IN': 'Bengali',
                'pa': 'Punjabi',
                'pa-IN': 'Punjabi',
                'or': 'Odia',
                'or-IN': 'Odia',
                'as': 'Assamese',
                'as-IN': 'Assamese',
                'ur': 'Urdu',
                'ur-IN': 'Urdu'
            }
            target_language = language_map.get(language, 'English')
            
            # Build prompt with context and language instruction
            prompt = f"""<context>
{context}
</context>

User question:
{user_message}

IMPORTANT: Answer the question using ONLY the textbook context above. Your response MUST be in {target_language} language. If the user asked in {target_language}, respond in {target_language}. Do not translate the textbook content, but explain it in {target_language}."""

            # Build messages
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
            
            # Add conversation history if provided (limited to last 5 for context)
            if conversation_history:
                history_messages = []
                for msg in conversation_history[-5:]:  # Last 5 messages for context
                    if msg.get('role') == 'user':
                        history_messages.append({"role": "user", "content": msg.get('content', '')})
                    elif msg.get('role') == 'assistant':
                        history_messages.append({"role": "assistant", "content": msg.get('content', '')})
                
                # Insert history before the current user message
                messages = [messages[0]] + history_messages + [messages[1]]
            
            # Generate response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,  # Lower temperature for more focused, factual responses
                max_tokens=1000
            )

            ai_text = response.choices[0].message.content.strip()

            # Ensure language compliance using Azure Translator when needed
            target_lang_code = language if language else 'en'
            if target_language != 'English':
                ai_text = self.translator.translate(ai_text, target_lang_code)
            
            return ai_text
        except Exception as e:
            print(f"Error generating LLM response: {e}")
            return None
