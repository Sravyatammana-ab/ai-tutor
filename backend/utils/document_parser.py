import os
import re
import hashlib
from typing import List, Dict, Tuple
from langchain_text_splitters import RecursiveCharacterTextSplitter

try:
    from utils.azure_ocr import AzureOCRService
except ImportError:
    AzureOCRService = None

try:
    from docx import Document
except ImportError:
    Document = None


def extract_text_from_docx(path: str) -> str:
    """Extract full text from DOCX using python-docx"""
    if not Document:
        raise ImportError("python-docx is not installed")
    
    doc = Document(path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip() != ""]
    return "\n".join(paragraphs)


def compute_file_hash(file_path: str) -> str:
    """Compute MD5 hash of file for duplicate detection"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def detect_chapters_and_units(text: str) -> Dict:
    """
    Detect chapter and unit titles from text
    Returns dict with chapter_titles, unit_titles, and structured content
    """
    chapters = []
    units = []
    
    # Common patterns for chapters/units
    chapter_patterns = [
        r'(?i)^\s*(?:chapter|ch\.?|unit|lesson)\s*(\d+)[:\.]?\s*(.+?)$',
        r'(?i)^\s*(\d+)[:\.]\s*(.+?)$',  # Numbered headings
        r'(?i)^\s*([A-Z][A-Z\s]{3,})$',  # All caps headings
    ]
    
    lines = text.split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        if not line or len(line) < 3:
            continue
        
        # Check for chapter patterns
        for pattern in chapter_patterns:
            match = re.match(pattern, line)
            if match:
                if 'chapter' in pattern.lower() or 'ch.' in pattern.lower():
                    chapters.append({
                        'number': match.group(1) if match.lastindex >= 1 else str(len(chapters) + 1),
                        'title': match.group(2) if match.lastindex >= 2 else match.group(1),
                        'line_index': i
                    })
                elif 'unit' in pattern.lower() or 'lesson' in pattern.lower():
                    units.append({
                        'number': match.group(1) if match.lastindex >= 1 else str(len(units) + 1),
                        'title': match.group(2) if match.lastindex >= 2 else match.group(1),
                        'line_index': i
                    })
                break
    
    return {
        'chapters': chapters,
        'units': units,
        'chapter_count': len(chapters) if chapters else None,
        'unit_count': len(units) if units else None
    }


_azure_service = None


def get_azure_service():
    """
    Lazily create a single Azure Document Intelligence client.
    Prevents re-initializing heavy SDK objects per request.
    """
    global _azure_service
    if _azure_service is not None:
        return _azure_service
    if not AzureOCRService:
        return None
    try:
        _azure_service = AzureOCRService()
        print("Azure Document Intelligence service initialized successfully")
    except Exception as e:
        import traceback
        print(f"Warning: Azure Document Intelligence service initialization failed: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        print("PDF extraction will not be available. Please configure AZURE_ENDPOINT and AZURE_KEY in your .env file.")
        _azure_service = None
    return _azure_service


class DocumentParser:
    """Parse PDF and DOCX documents and chunk text using LangChain"""
    
    def __init__(self):
        self.chunk_size = 1000
        self.chunk_overlap = 200
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ".", "!", "?"]
        )
        
        # Azure Document Intelligence service will be lazy-loaded
        self.azure_ocr_service = None
    
    def parse_document(self, file_path: str, file_ext: str) -> Tuple[str, Dict]:
        """
        Parse document and extract text content with metadata
        
        Returns:
            Tuple of (text_content, metadata)
        """
        # Compute file hash for duplicate detection
        file_hash = compute_file_hash(file_path)
        
        metadata = {
            'filename': os.path.basename(file_path),
            'file_type': file_ext,
            'file_size': os.path.getsize(file_path),
            'file_hash': file_hash,
            'source': 'azure_document_intelligence' if file_ext == 'pdf' else 'python-docx'
        }
        
        if file_ext == 'pdf':
            return self._parse_pdf(file_path, metadata)
        elif file_ext == 'docx':
            return self._parse_docx(file_path, metadata)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
    
    def _parse_pdf(self, file_path: str, metadata: Dict) -> Tuple[str, Dict]:
        """Parse PDF using Azure Document Intelligence"""
        if not self.azure_ocr_service:
            self.azure_ocr_service = get_azure_service()
        if not self.azure_ocr_service:
            raise ValueError(
                "Azure Document Intelligence service is not available. "
                "Please configure AZURE_ENDPOINT and AZURE_KEY in your .env file."
            )
        
        try:
            # Extract text using Azure Document Intelligence
            text_content = self.azure_ocr_service.extract_text(file_path)
            
            if not text_content or not text_content.strip():
                raise ValueError(
                    "Failed to extract text using Azure Document Intelligence - document appears empty or contains no readable text. "
                    "Please ensure the PDF contains readable text."
                )
            
            # Clean and normalize text
            text_content = self._clean_text(text_content)
            
            # Detect chapters and units
            structure_info = detect_chapters_and_units(text_content)
            metadata.update(structure_info)
            
            # Estimate page count based on text length (rough estimate: ~500 words per page)
            word_count = len(text_content.split())
            estimated_pages = max(1, word_count // 500)
            metadata['page_count'] = estimated_pages
            metadata['source'] = 'azure_document_intelligence'
            
            return text_content, metadata
            
        except ValueError:
            # Re-raise ValueError as-is (already formatted)
            raise
        except Exception as e:
            error_msg = str(e)
            raise ValueError(f"Failed to extract text using Azure Document Intelligence: {error_msg}")
    
    def _parse_docx(self, file_path: str, metadata: Dict) -> Tuple[str, Dict]:
        """Parse DOCX file using python-docx"""
        try:
            text_content = extract_text_from_docx(file_path)
            
            if not text_content or not text_content.strip():
                raise ValueError("Failed to extract text from DOCX - document appears empty")
            
            # Clean and normalize text
            text_content = self._clean_text(text_content)
            
            # Detect chapters and units
            structure_info = detect_chapters_and_units(text_content)
            metadata.update(structure_info)
            
            # Count paragraphs
            doc = Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip() != ""]
            metadata['paragraph_count'] = len(paragraphs)
            metadata['source'] = 'python-docx'
            
            return text_content, metadata
            
        except Exception as e:
            raise ValueError(f"Failed to parse DOCX: {e}")
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Restore line breaks for paragraphs
        text = re.sub(r'\.\s+([A-Z])', r'.\n\n\1', text)
        # Remove special characters that might interfere
        text = text.replace('\x00', '')
        return text.strip()
    
    def chunk_text(self, text: str, chunk_size: int = None, chunk_overlap: int = None, metadata: Dict = None) -> List[Dict]:
        """
        Split text into chunks using LangChain RecursiveCharacterTextSplitter
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk
            chunk_overlap: Overlap between chunks
            metadata: Document metadata for context
        
        Returns:
            List of chunk dictionaries with text and metadata
        """
        if chunk_size is None:
            chunk_size = self.chunk_size
        if chunk_overlap is None:
            chunk_overlap = self.chunk_overlap
        
        # Update text splitter if parameters changed
        if chunk_size != self.chunk_size or chunk_overlap != self.chunk_overlap:
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                separators=["\n\n", "\n", ".", "!", "?"]
            )
            self.chunk_size = chunk_size
            self.chunk_overlap = chunk_overlap
        
        # Split text into chunks
        chunks = self.text_splitter.split_text(text)
        
        # Get chapter/unit info from metadata
        chapters = metadata.get('chapters', []) if metadata else []
        units = metadata.get('units', []) if metadata else []
        
        # Convert to list of dictionaries with enhanced metadata
        chunk_list = []
        lines = text.split('\n')
        current_chapter = None
        current_unit = None
        
        for idx, chunk_text in enumerate(chunks):
            if not chunk_text.strip():
                continue
            
            # Find which chapter/unit this chunk belongs to
            chunk_start_pos = text.find(chunk_text)
            chunk_line_index = text[:chunk_start_pos].count('\n') if chunk_start_pos >= 0 else 0
            
            # Determine chapter and unit for this chunk
            for chapter in chapters:
                if chapter['line_index'] <= chunk_line_index:
                    current_chapter = chapter
                else:
                    break
            
            for unit in units:
                if unit['line_index'] <= chunk_line_index:
                    current_unit = unit
                else:
                    break
            
            chunk_metadata = {
                    'text': chunk_text,
                    'chunk_index': idx,
                    'length': len(chunk_text)
            }
            
            # Add chapter/unit metadata if available
            if current_chapter:
                chunk_metadata['chapter_number'] = current_chapter.get('number')
                chunk_metadata['chapter_title'] = current_chapter.get('title')
            
            if current_unit:
                chunk_metadata['unit_number'] = current_unit.get('number')
                chunk_metadata['unit_title'] = current_unit.get('title')
            
            chunk_list.append(chunk_metadata)
        
        return chunk_list
