import os
from typing import Optional
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from config import Config


class AzureOCRService:
    """Service for extracting text from PDFs and images using Azure Document Intelligence"""
    
    def __init__(self):
        """Initialize Azure Document Intelligence client with credentials from environment"""
        self.endpoint = Config.AZURE_ENDPOINT
        self.key = Config.AZURE_KEY
        
        if not self.endpoint:
            raise ValueError(
                "AZURE_ENDPOINT is required. "
                "Please set AZURE_ENDPOINT in your .env file."
            )
        
        if not self.key:
            raise ValueError(
                "AZURE_KEY is required. "
                "Please set AZURE_KEY in your .env file."
            )
        
        # Remove trailing slash if present
        self.endpoint = self.endpoint.rstrip('/')
        
        try:
            # Initialize Document Intelligence client
            self.client = DocumentIntelligenceClient(
                endpoint=self.endpoint,
                credential=AzureKeyCredential(self.key)
            )
        except Exception as e:
            raise ValueError(f"Failed to initialize Azure Document Intelligence client: {e}")
    
    def extract_text(self, file_path: str) -> str:
        """
        Extract text from PDF or image using Azure Document Intelligence prebuilt-read model
        
        Args:
            file_path: Path to the PDF or image file
            
        Returns:
            Extracted text string with line breaks preserved
        """
        try:
            # Read file as bytes
            with open(file_path, 'rb') as file:
                file_bytes = file.read()
            
            # Use prebuilt-read model for text extraction
            # The body parameter accepts bytes or file-like object
            poller = self.client.begin_analyze_document(
                model_id="prebuilt-read",
                body=file_bytes
            )
            
            # Wait for the result
            result = poller.result()
            
            # Extract text from result
            # The content field contains the full text with line breaks preserved
            if hasattr(result, 'content') and result.content:
                return result.content
            
            # Fallback: extract from pages if content is not directly available
            extracted_text = []
            if hasattr(result, 'pages') and result.pages:
                for page in result.pages:
                    if hasattr(page, 'lines') and page.lines:
                        page_text = "\n".join([line.content for line in page.lines if hasattr(line, 'content') and line.content])
                        if page_text:
                            extracted_text.append(page_text)
            
            if extracted_text:
                return "\n\n".join(extracted_text)
            
            # If no text found, return empty string
            return ""
            
        except FileNotFoundError:
            raise ValueError(f"File not found: {file_path}")
        except Exception as e:
            error_msg = str(e)
            
            # Provide helpful error messages
            if "401" in error_msg or "Unauthorized" in error_msg:
                raise ValueError(
                    "Azure Document Intelligence authentication failed. "
                    "Please check your AZURE_KEY in the .env file."
                )
            elif "404" in error_msg or "Not Found" in error_msg:
                raise ValueError(
                    "Azure Document Intelligence endpoint not found. "
                    "Please check your AZURE_ENDPOINT in the .env file."
                )
            elif "429" in error_msg or "Too Many Requests" in error_msg:
                raise ValueError(
                    "Azure Document Intelligence rate limit exceeded. "
                    "Please try again later."
                )
            else:
                raise ValueError(f"Failed to extract text using Azure Document Intelligence: {error_msg}")

