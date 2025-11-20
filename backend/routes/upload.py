from flask import Blueprint, request, jsonify
import os
import uuid
from datetime import datetime
from math import ceil
from werkzeug.utils import secure_filename

from utils.document_parser import DocumentParser, compute_file_hash
from utils.embedding_service import EmbeddingService
from utils.qdrant import QdrantService
from config import Config

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/document', methods=['POST'])
def upload_document():
    """
    Handle document upload, parse, chunk, generate embeddings, and store in Qdrant
    Includes duplicate detection based on file hash
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        if file_ext not in Config.ALLOWED_EXTENSIONS:
            return jsonify({'error': f'Invalid file type. Allowed types: {Config.ALLOWED_EXTENSIONS}'}), 400
        
        # Save file temporarily to compute hash
        temp_document_id = str(uuid.uuid4())
        temp_file_path = os.path.join(Config.UPLOAD_FOLDER, f"temp_{temp_document_id}.{file_ext}")
        file.save(temp_file_path)
        
        # Compute file hash for duplicate detection
        file_hash = compute_file_hash(temp_file_path)
        
        # Check for existing document with same hash
        qdrant_service = QdrantService()
        qdrant_service.create_collection_if_not_exists()
        
        # Search for existing document with same hash
        existing_docs = qdrant_service.search_by_hash(file_hash)
        
        if existing_docs:
            # Document already exists
            existing_doc = existing_docs[0]
            existing_document_id = existing_doc.get('document_id')
            existing_filename = existing_doc.get('filename', filename)
            
            # Delete temp file
            try:
                os.remove(temp_file_path)
            except:
                pass
            
            return jsonify({
                'success': True,
                'duplicate': True,
                'existing_document_id': existing_document_id,
                'existing_filename': existing_filename,
                'message': 'This textbook already exists in the system.'
            }), 200
        
        # Check if user wants to reprocess (from request)
        reprocess = request.form.get('reprocess', 'false').lower() == 'true'
        
        if reprocess:
            # Delete old embeddings for this hash (if any)
            qdrant_service.delete_by_hash(file_hash)
        
        # Generate unique document ID
        document_id = str(uuid.uuid4())
        file_path = os.path.join(Config.UPLOAD_FOLDER, f"{document_id}.{file_ext}")
        os.rename(temp_file_path, file_path)
        
        # Parse document using Azure Document Intelligence for PDFs
        parser = DocumentParser()
        try:
            text_content, metadata = parser.parse_document(file_path, file_ext)
        except ValueError as parse_error:
            import traceback
            error_details = str(parse_error)
            print(f"Azure Document Intelligence extraction error: {error_details}")
            print(f"Traceback: {traceback.format_exc()}")
            # Clean up file
            try:
                os.remove(file_path)
            except:
                pass
            return jsonify({'error': f'Failed to extract text: {error_details}'}), 400
        except Exception as parse_error:
            import traceback
            error_details = str(parse_error)
            print(f"Unexpected Azure Document Intelligence error: {error_details}")
            print(f"Traceback: {traceback.format_exc()}")
            # Clean up file
            try:
                os.remove(file_path)
            except:
                pass
            return jsonify({'error': f'Failed to extract text: {error_details}'}), 500
        
        if not text_content or not text_content.strip():
            try:
                os.remove(file_path)
            except:
                pass
            return jsonify({'error': 'Failed to extract text - document appears empty or contains no readable text'}), 400
        
        # Chunk text using LangChain with metadata
        chunks = parser.chunk_text(
            text_content,
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            metadata=metadata
        )
        
        if not chunks:
            try:
                os.remove(file_path)
            except:
                pass
            return jsonify({'error': 'Failed to chunk document'}), 500
        
        # Generate embeddings and store in Qdrant
        embedding_service = EmbeddingService()
        
        # Ensure collection exists
        qdrant_service.ensure_payload_index('document_id')
        qdrant_service.ensure_payload_index('file_hash')
        
        # Process chunks and store embeddings with enhanced metadata
        page_count = metadata.get('page_count', 1)
        total_chars = len(text_content)
        chapter_count = metadata.get('chapter_count')
        unit_count = metadata.get('unit_count')
        
        stored_points = []
        for chunk in chunks:
            embedding = embedding_service.generate_embedding(chunk['text'])
            if not embedding:
                continue
            
            # Estimate page number based on position in text
            page_number = None
            if page_count > 1 and total_chars > 0:
                chunk_idx = chunk['chunk_index']
                position_ratio = chunk_idx / max(1, len(chunks) - 1) if len(chunks) > 1 else 0
                page_number = max(1, min(page_count, ceil(position_ratio * page_count)))
            elif page_count == 1:
                page_number = 1
            
            # Build enhanced payload with all metadata
            payload = {
                'document_id': document_id,
                'file_hash': file_hash,
                'filename': filename,
                'source': metadata.get('source', 'unknown'),
                'text': chunk['text'],
                'page': page_number,
                'chunk_index': chunk['chunk_index']
            }
            
            # Add chapter/unit metadata if available
            if chunk.get('chapter_number'):
                payload['chapter_number'] = chunk['chapter_number']
            if chunk.get('chapter_title'):
                payload['chapter_title'] = chunk['chapter_title']
            if chunk.get('unit_number'):
                payload['unit_number'] = chunk['unit_number']
            if chunk.get('unit_title'):
                payload['unit_title'] = chunk['unit_title']
            
            # Add document-level metadata for easy retrieval
            if chapter_count is not None:
                payload['document_chapter_count'] = chapter_count
            if unit_count is not None:
                payload['document_unit_count'] = unit_count
            
            stored_points.append({
                'id': str(uuid.uuid4()),
                'vector': embedding,
                'payload': payload
            })
        
        if not stored_points:
            try:
                os.remove(file_path)
            except:
                pass
            return jsonify({'error': 'Failed to generate embeddings for document'}), 500
        
        try:
            qdrant_service.upsert_points_in_batches(stored_points, batch_size=48)
        except Exception as exc:
            try:
                os.remove(file_path)
            except:
                pass
            return jsonify({'error': f'Failed to store embeddings: {exc}'}), 500
        
        return jsonify({
            'success': True,
            'document_id': document_id,
            'filename': filename,
            'chunks_processed': len(stored_points),
            'total_chunks': len(chunks),
            'chapter_count': chapter_count,
            'unit_count': unit_count,
            'file_hash': file_hash,
            'message': 'Document uploaded and processed successfully'
        }), 200
        
    except Exception as e:
        import traceback
        print(f"Error in upload_document: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500
