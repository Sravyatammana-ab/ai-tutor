import os
from typing import Optional

# Strict import with clear error if package not installed
try:
    from azure.ai.documentintelligence import (
        DocumentIntelligenceClient,
        DocumentIntelligenceApiVersion
    )
    from azure.core.credentials import AzureKeyCredential
except ImportError as e:
    raise ImportError(
        "azure-ai-documentintelligence package is not installed. "
        "Please install: pip install azure-ai-documentintelligence azure-core"
    ) from e

from config import Config


class AzureOCRService:
    """Service for extracting text from PDFs and images using Azure Document Intelligence"""
    
    def __init__(self):
        """Initialize Azure Document Intelligence client with credentials from environment"""
        self.endpoint = Config.AZURE_ENDPOINT
        self.key = Config.AZURE_KEY
        
        # Strong validation: Check if values are actually set (not just truthy)
        endpoint_set = bool(self.endpoint and self.endpoint.strip())
        key_set = bool(self.key and self.key.strip())
        
        # Masked logging: Show masked endpoint and first/last 4 chars of key
        if endpoint_set:
            endpoint_masked = self.endpoint[:40] + "..." if len(self.endpoint) > 40 else self.endpoint
            endpoint_masked = endpoint_masked.rstrip('/')
            print(f"✓ AZURE_ENDPOINT loaded: {endpoint_masked}")
        else:
            print("✗ AZURE_ENDPOINT is NOT SET or EMPTY")
        
        if key_set:
            # Show first 4 and last 4 characters of key (masked)
            if len(self.key) > 8:
                key_masked = self.key[:4] + "..." + self.key[-4:]
            else:
                key_masked = "***" + self.key[-4:] if len(self.key) > 4 else "***"
            print(f"✓ AZURE_KEY loaded: {key_masked} (length: {len(self.key)})")
        else:
            print("✗ AZURE_KEY is NOT SET or EMPTY")
        
        # Clear error if values are missing
        if not endpoint_set:
            raise ValueError(
                "AZURE_ENDPOINT is required but not configured. "
                "Please set AZURE_ENDPOINT in your .env file or environment variables. "
                "Value must not be empty or whitespace-only."
            )
        
        if not key_set:
            raise ValueError(
                "AZURE_KEY is required but not configured. "
                "Please set AZURE_KEY in your .env file or environment variables. "
                "Value must not be empty or whitespace-only."
            )
        
        # Ensure endpoint is properly formatted (remove trailing slash for SDK)
        self.endpoint = self.endpoint.strip().rstrip('/')
        
        # Validate endpoint format - MUST start with https://
        if not self.endpoint.startswith('https://'):
            raise ValueError(
                f"AZURE_ENDPOINT must start with https://. "
                f"Got: {self.endpoint[:50]}..."
            )
        
        try:
            # Initialize Document Intelligence client
            self.client = DocumentIntelligenceClient(
                endpoint=self.endpoint,
                credential=AzureKeyCredential(self.key.strip()),
                api_version=DocumentIntelligenceApiVersion.V2023_10_31
            )
            print("✓ Azure Document Intelligence client initialized successfully")
        except Exception as e:
            error_msg = str(e)
            raise ValueError(
                f"Failed to initialize Azure Document Intelligence client: {error_msg}. "
                f"Please verify AZURE_ENDPOINT and AZURE_KEY are correct."
            )
    
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

