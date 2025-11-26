from flask import Blueprint, request, jsonify
import os
import uuid
from datetime import datetime
from math import ceil
from werkzeug.utils import secure_filename

from utils.document_parser import DocumentParser, compute_file_hash
from utils.embedding_service import EmbeddingService
from utils.vector_store import VectorStoreService
from config import Config

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/document', methods=['POST', 'OPTIONS'])
def upload_document():
    """Upload → Parse → Chunk → Embed → Store"""
    
    # Handle preflight
    if request.method == 'OPTIONS':
        return ('', 204)
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        if file_ext not in Config.ALLOWED_EXTENSIONS:
            return jsonify({'error': f'Invalid file type. Allowed types: {Config.ALLOWED_EXTENSIONS}'}), 400
        
        # Save temporary file to compute hash
        temp_id = str(uuid.uuid4())
        temp_path = os.path.join(Config.UPLOAD_FOLDER, f"temp_{temp_id}.{file_ext}")
        file.save(temp_path)

        # Compute file hash
        file_hash = compute_file_hash(temp_path)

        # Lazy load vector store on demand (to avoid memory crash)
        vector_store = VectorStoreService()
        # Ensure collection exists with named vector "default" before any operations
        vector_store.create_collection_if_not_exists()

        existing_docs = vector_store.search_by_hash(file_hash)

        if existing_docs:
            existing = existing_docs[0]
            try: os.remove(temp_path)
            except: pass

            return jsonify({
                'success': True,
                'duplicate': True,
                'existing_document_id': existing['document_id'],
                'existing_filename': existing.get('filename', filename)
            }), 200
        
        # Reprocess check
        reprocess = request.form.get('reprocess', 'false').lower() == 'true'
        if reprocess:
            vector_store.delete_by_hash(file_hash)

        document_id = str(uuid.uuid4())
        final_path = os.path.join(Config.UPLOAD_FOLDER, f"{document_id}.{file_ext}")
        os.rename(temp_path, final_path)

        # Lazy-load Document Parser to avoid startup crash
        print(f"[upload_document] Initializing DocumentParser for file: {filename} ({file_ext})")
        
        # Log Azure-only mode before parsing
        if file_ext == 'pdf':
            print(f"[upload_document] Using Azure OCR only — no fallback.")
        
        document_parser = DocumentParser()

        try:
            print(f"[upload_document] Starting document parsing for: {filename}")
            text_content, metadata = document_parser.parse_document(final_path, file_ext)
            extraction_source = metadata.get('source', 'unknown')
            print(f"[upload_document] [OK] Document parsing successful using: {extraction_source}")
            print(f"[upload_document] Extracted text length: {len(text_content)} characters")
            print(f"[upload_document] Estimated pages: {metadata.get('page_count', 'N/A')}")
        except ValueError as e:
            # Azure OCR errors - return exact error message
            error_msg = str(e)
            print(f"[upload_document] [ERROR] Azure OCR failed: {error_msg}")
            try: os.remove(final_path)
            except: pass
            return jsonify({'error': f'Azure OCR failed: {error_msg}'}), 400
        except Exception as e:
            import traceback
            error_msg = str(e)
            error_traceback = traceback.format_exc()
            print(f"[upload_document] [ERROR] Document parsing failed: {error_msg}")
            print(f"[upload_document] Exception traceback:\n{error_traceback}")
            try: os.remove(final_path)
            except: pass
            return jsonify({'error': f'Azure OCR failed: {error_msg}'}), 400

        if not text_content.strip():
            try: os.remove(final_path)
            except: pass
            return jsonify({'error': 'File contains no readable text'}), 400

        # Chunk text
        chunks = document_parser.chunk_text(
            text_content,
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            metadata=metadata
        )

        if not chunks:
            try: os.remove(final_path)
            except: pass
            return jsonify({'error': 'Failed to chunk document'}), 500

        # Lazy-load embedding service
        embedding_service = EmbeddingService()

        total_chars = len(text_content)
        page_count = metadata.get('page_count', 1)

        stored = 0
        pending_points = []

        for chunk in chunks:
            embedding = embedding_service.generate_embedding(chunk['text'])
            if not embedding:
                continue

            # Estimate page number
            idx = chunk['chunk_index']
            if len(chunks) > 1:
                ratio = idx / (len(chunks) - 1)
                page_number = max(1, min(page_count, ceil(ratio * page_count)))
            else:
                page_number = 1

            payload = {
                'document_id': document_id,
                'file_hash': file_hash,
                'filename': filename,
                'text': chunk['text'],
                'page': page_number,
                'chunk_index': chunk['chunk_index'],
                'chapter_number': chunk.get('chapter_number'),
                'chapter_title': chunk.get('chapter_title'),
                'unit_number': chunk.get('unit_number'),
                'unit_title': chunk.get('unit_title'),
                'document_chapter_count': metadata.get('chapter_count'),
                'document_unit_count': metadata.get('unit_count'),
                'document_page_count': metadata.get('page_count')
            }

            pending_points.append({
                'id': str(uuid.uuid4()),
                'vector': embedding,
                'payload': payload
            })

            if len(pending_points) >= 48:
                vector_store.upsert_points_in_batches(pending_points, batch_size=48)
                stored += len(pending_points)
                pending_points = []

        if pending_points:
            vector_store.upsert_points_in_batches(pending_points, batch_size=48)
            stored += len(pending_points)

        if stored == 0:
            try: os.remove(final_path)
            except: pass
            return jsonify({'error': 'Failed to generate embeddings'}), 500

        return jsonify({
            'success': True,
            'document_id': document_id,
            'filename': filename,
            'stored_chunks': stored,
            'total_chunks': len(chunks),
            'message': 'Document processed successfully'
        }), 200

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500
