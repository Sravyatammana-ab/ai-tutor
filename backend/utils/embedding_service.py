import os
from openai import OpenAI
from config import Config

class EmbeddingService:
    """Generate embeddings using OpenAI API"""
    
    def __init__(self):
        if not Config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in environment variables")
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_EMBEDDING_MODEL
    
    def generate_embedding(self, text: str) -> list:
        """
        Generate embedding for given text
        
        Args:
            text: Text to generate embedding for
        
        Returns:
            List of embedding values
        """
        try:
            # Clean and prepare text
            text = text.replace("\n", " ").strip()
            if not text:
                return None
            
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None
    
    def generate_embeddings_batch(self, texts: list) -> list:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to generate embeddings for
        
        Returns:
            List of embedding lists
        """
        embeddings = []
        for text in texts:
            embedding = self.generate_embedding(text)
            if embedding:
                embeddings.append(embedding)
        return embeddings


