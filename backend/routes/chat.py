from flask import Blueprint, request, jsonify
import uuid
from typing import Dict

from utils.embedding_service import EmbeddingService
from utils.qdrant import QdrantService
from utils.llm_service import LLMService
from utils.tts import TTSService
from utils.supabase_service import SupabaseService
from utils.memory_service import MemoryService
from utils.translator import TranslatorService
from config import Config

chat_bp = Blueprint('chat', __name__)

# Initialize services (lazy initialization to handle errors gracefully)
embedding_service = None
qdrant_service = None
llm_service = None
tts_service = None
supabase_service = None
memory_service = None
translator_service = None

def get_embedding_service():
    global embedding_service
    if embedding_service is None:
        embedding_service = EmbeddingService()
    return embedding_service

def get_qdrant_service():
    global qdrant_service
    if qdrant_service is None:
        qdrant_service = QdrantService()
    return qdrant_service

def get_llm_service():
    global llm_service
    if llm_service is None:
        llm_service = LLMService()
    return llm_service

def get_tts_service():
    global tts_service
    if tts_service is None:
        tts_service = TTSService()
    return tts_service

def get_supabase_service():
    global supabase_service
    if supabase_service is None:
        try:
            supabase_service = SupabaseService()
        except Exception as e:
            print(f"Warning: Supabase service initialization failed: {e}")
            return None
    return supabase_service

def get_memory_service():
    global memory_service
    if memory_service is None:
        memory_service = MemoryService()
    return memory_service

def get_translator_service():
    global translator_service
    if translator_service is None:
        translator_service = TranslatorService()
    return translator_service


@chat_bp.route('/message', methods=['POST'])
def send_message():
    """
    Handle user message, retrieve context, generate response, and convert to speech
    """
    try:
        data = request.json
        user_message = (data.get('message') or '').strip()
        document_id = data.get('document_id')
        language = data.get('language', 'en')
        session_id = data.get('session_id')
        history_from_client = data.get('history', [])
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        if not document_id:
            return jsonify({'error': 'No document_id provided'}), 400
        
        # Generate session_id if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Get services
        embedding_service = get_embedding_service()
        qdrant_service = get_qdrant_service()
        llm_service = get_llm_service()
        tts_service = get_tts_service()
        supabase_service = get_supabase_service()
        memory_service = get_memory_service()
        translator_service = get_translator_service()
        
        def localize_text(text: str) -> str:
            if not text:
                return text
            language_value = (language or '').lower()
            if not language_value or language_value.startswith('en'):
                return text
            try:
                return translator_service.translate(text, language)
            except Exception as translate_error:
                print(f"Warning: translation failed for language {language}: {translate_error}")
                return text
        
        # Generate embedding for user query
        query_embedding = embedding_service.generate_embedding(user_message)
        if not query_embedding:
            return jsonify({'error': 'Failed to generate query embedding'}), 500
        
        # Enhanced retrieval: Try multiple strategies
        # Strategy 1: Direct semantic search with document filter
        results = qdrant_service.search_similar(
            query_vector=query_embedding,
            limit=10,  # Increased limit for better context
            filter_conditions={'document_id': document_id}
        )
        
        # Strategy 2: If no results, try without filter (fallback)
        if not results or len(results) == 0:
            results = qdrant_service.search_similar(
                query_vector=query_embedding,
                limit=10,
                filter_conditions=None
            )
            # Filter results by document_id manually
            results = [r for r in results if r['payload'].get('document_id') == document_id]
        
        # Strategy 3: For chapter/unit count queries, get metadata directly
        query_lower = user_message.lower()
        is_count_query = any(keyword in query_lower for keyword in [
            'how many chapters', 'how many units', 'number of chapters', 'number of units',
            'what are the chapters', 'list of chapters', 'chapter names'
        ])
        
        # Extract chapter/unit metadata from results
        chapter_titles = set()
        unit_titles = set()
        chapter_count_from_metadata = None
        unit_count_from_metadata = None
        
        for result in results:
            payload = result.get('payload', {})
            if payload.get('chapter_title'):
                chapter_titles.add(payload['chapter_title'])
            if payload.get('unit_title'):
                unit_titles.add(payload['unit_title'])
            if payload.get('document_chapter_count') is not None:
                chapter_count_from_metadata = payload['document_chapter_count']
            if payload.get('document_unit_count') is not None:
                unit_count_from_metadata = payload['document_unit_count']

        def enrich_document_structure():
            nonlocal chapter_count_from_metadata, unit_count_from_metadata
            try:
                if not chapter_titles or not unit_titles or chapter_count_from_metadata is None or unit_count_from_metadata is None:
                    samples = qdrant_service.get_document_metadata_samples(document_id, limit=128)
                    for payload in samples:
                        chapter_value = payload.get('chapter_title')
                        unit_value = payload.get('unit_title')
                        if chapter_value:
                            chapter_titles.add(chapter_value)
                        if unit_value:
                            unit_titles.add(unit_value)
                        if chapter_count_from_metadata is None and payload.get('document_chapter_count') is not None:
                            chapter_count_from_metadata = payload.get('document_chapter_count')
                        if unit_count_from_metadata is None and payload.get('document_unit_count') is not None:
                            unit_count_from_metadata = payload.get('document_unit_count')
            except Exception as meta_error:
                print(f"Warning: failed to enrich document structure: {meta_error}")
        
        enrich_document_structure()

        chapter_titles_list = sorted(chapter_titles, key=lambda title: title.lower()) if chapter_titles else []
        unit_titles_list = sorted(unit_titles, key=lambda title: title.lower()) if unit_titles else []
        
        if chapter_titles_list and chapter_count_from_metadata is None:
            chapter_count_from_metadata = len(chapter_titles_list)
        if unit_titles_list and unit_count_from_metadata is None:
            unit_count_from_metadata = len(unit_titles_list)
        
        # Collect ALL retrieved text with metadata
        retrieved_context_parts = []
        for r in results:
            text = r['payload'].get('text', '')
            if text:
                # Add chapter/unit context if available
                chapter_info = ""
                if r['payload'].get('chapter_title'):
                    chapter_info = f"[Chapter: {r['payload'].get('chapter_title')}] "
                if r['payload'].get('unit_title'):
                    chapter_info += f"[Unit: {r['payload'].get('unit_title')}] "
                retrieved_context_parts.append(chapter_info + text)
        
        retrieved_context = "\n\n".join(retrieved_context_parts)
        
        # For count queries, add explicit metadata to context
        if (is_count_query or chapter_titles_list or unit_titles_list) and (chapter_count_from_metadata is not None or unit_count_from_metadata is not None):
            metadata_context = "\n\n[Document Metadata]\n"
            if chapter_count_from_metadata is not None:
                metadata_context += f"Total chapters in this textbook: {chapter_count_from_metadata}\n"
            if unit_count_from_metadata is not None:
                metadata_context += f"Total units in this textbook: {unit_count_from_metadata}\n"
            if chapter_titles_list:
                metadata_context += f"Chapter titles found: {', '.join(chapter_titles_list)}\n"
            if unit_titles_list:
                metadata_context += f"Unit titles found: {', '.join(unit_titles_list)}\n"
            retrieved_context = metadata_context + "\n" + retrieved_context
        
        # Normalize language code (e.g., 'en' -> 'en-IN', 'hi' -> 'hi-IN')
        normalized_language = language
        if normalized_language == 'en':
            normalized_language = 'en-IN'
        elif '-' not in normalized_language and len(normalized_language) == 2:
            # Map 2-letter codes to full codes for Indian languages
            lang_map = {
                'hi': 'hi-IN', 'ta': 'ta-IN', 'te': 'te-IN',
                'kn': 'kn-IN', 'ml': 'ml-IN', 'mr': 'mr-IN',
                'gu': 'gu-IN', 'bn': 'bn-IN', 'pa': 'pa-IN',
                'or': 'or-IN', 'as': 'as-IN', 'ur': 'ur-IN'
            }
            normalized_language = lang_map.get(normalized_language, 'en-IN')
        
        # CRITICAL: If no context retrieved, try one more broad search
        if not retrieved_context or not retrieved_context.strip():
            try:
                generic_query = "textbook content chapters units"
                generic_embedding = embedding_service.generate_embedding(generic_query)
                if generic_embedding:
                    fallback_results = qdrant_service.search_similar(
                        query_vector=generic_embedding,
                        limit=5,
                        filter_conditions={'document_id': document_id}
                    )
                    retrieved_context = "\n\n".join([r['payload'].get('text', '') for r in fallback_results if r['payload'].get('text')])
            except Exception as e:
                print(f"Fallback search failed: {e}")
        
        context_available = bool(retrieved_context and retrieved_context.strip())
        unavailable_reply = (
            "I carefully reviewed all the extracted chapters from this textbook but could not find information that matches your question. "
            "This typically happens when the requested topic is not covered in the uploaded book. "
            "Please try asking about another concept from this textbook."
        )
        
        # Helper: heuristic responses for chapter/unit queries
        user_message_lower = user_message.lower()

        def build_chapter_summary_response() -> str:
            if not chapter_titles_list:
                return ""
            chapter_sentence = "; ".join(chapter_titles_list)
            return chapter_sentence

        def handle_chapter_specific_queries() -> str:
            if not chapter_titles_list:
                return ""
            summary_sentence = build_chapter_summary_response()
            chapter_count = chapter_count_from_metadata or len(chapter_titles_list)
            if any(phrase in user_message_lower for phrase in ['how many chapters', 'number of chapters', 'total chapters']):
                return f"This textbook contains {chapter_count} chapters. They are: {summary_sentence}."
            if any(phrase in user_message_lower for phrase in ['what are the chapters', 'chapter names', 'list of chapters', 'chapters names']):
                return f"The chapter names are: {summary_sentence}."
            return ""

        def handle_topic_absence_queries() -> str:
            if not chapter_titles_list:
                return ""
            topic_keywords = [
                'history', 'science', 'math', 'physics', 'chemistry', 'biology',
                'geography', 'civics', 'social', 'economics', 'politics'
            ]
            for keyword in topic_keywords:
                if keyword in user_message_lower:
                    topic_present = any(keyword in title.lower() for title in chapter_titles_list)
                    if not topic_present:
                        summary_sentence = build_chapter_summary_response()
                        return (
                            f"This textbook focuses on these chapters: {summary_sentence}. "
                            f"It does not include any dedicated chapters about {keyword.title()}."
                        )
            return ""

        # Build conversation history (prefer client data if provided)
        conversation_history = []
        if isinstance(history_from_client, list) and history_from_client:
            for message in history_from_client[-5:]:  # Last 5 messages
                role = message.get('role')
                content = message.get('content')
                if role in ('user', 'assistant') and content:
                    conversation_history.append({'role': role, 'content': content})
        else:
            conversation_history = memory_service.get_conversation_history(session_id)
        
        heuristic_reply = handle_chapter_specific_queries() or handle_topic_absence_queries()
        ai_response = None

        if heuristic_reply:
            ai_response = localize_text(heuristic_reply)
        elif context_available:
            ai_response = llm_service.generate_response(
                user_message=user_message,
                context=retrieved_context,
                conversation_history=conversation_history,
                language=normalized_language
            )
        else:
            ai_response = localize_text(unavailable_reply)
        
        if not ai_response:
            ai_response = localize_text(unavailable_reply)
        
        # Convert response to speech (handle errors gracefully)
        audio_filename = None
        try:
            audio_filename = tts_service.text_to_speech(ai_response, normalized_language, session_id)
            if not audio_filename:
                print(f"Warning: TTS service returned None for language: {normalized_language}")
        except Exception as tts_error:
            print(f"Warning: TTS generation failed: {tts_error}")
            import traceback
            traceback.print_exc()
            # Continue without audio - don't fail the request
        
        # Save conversation to Supabase (optional - don't fail if it fails)
        if supabase_service:
            try:
                supabase_service.save_conversation(
                    session_id=session_id,
                    document_id=document_id,
                    user_message=user_message,
                    ai_response=ai_response,
                    audio_path=audio_filename,
                    language=language
                )
            except Exception as e:
                print(f"Warning: Failed to save conversation to Supabase: {e}")
        
        # Update conversation history in memory
        memory_service.add_to_history(session_id, user_message, ai_response)
        
        # Build sources payload
        sources_payload = []
        for idx, result in enumerate(results):
            payload = result.get('payload', {})
            sources_payload.append({
                'label': f"Source {idx + 1}",
                'page': payload.get('page'),
                'chunk_index': payload.get('chunk_index')
            })
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'response': ai_response,
            'audio_url': f'/api/audio/{audio_filename}' if audio_filename else None,
            'context_used': len(results),
            'sources': sources_payload
        }), 200
        
    except Exception as e:
        print(f"Error in send_message: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/suggestions', methods=['POST'])
def get_suggestions():
    """
    Generate initial suggested questions based on uploaded document
    """
    try:
        data = request.json
        document_id = data.get('document_id')
        language = data.get('language', 'en')
        
        if not document_id:
            return jsonify({'error': 'No document_id provided'}), 400
        
        # Get services
        qdrant_service = get_qdrant_service()
        embedding_service = get_embedding_service()
        
        # Try multiple search queries to get diverse content
        search_queries = [
            "introduction overview summary beginning",
            "main topics concepts key points",
            "chapter sections content"
        ]
        
        all_chunks = []
        for query_text in search_queries:
            try:
                query_embedding = embedding_service.generate_embedding(query_text)
                if query_embedding:
                    search_results = qdrant_service.search_similar(
                        query_vector=query_embedding,
                        limit=2,
                        filter_conditions={'document_id': document_id}
                    )
                    for result in search_results:
                        chunk_text = result['payload'].get('text', '')
                        if chunk_text and chunk_text not in all_chunks:
                            all_chunks.append(chunk_text)
            except Exception as e:
                print(f"Error in search query '{query_text}': {e}")
                continue
        
        # If no chunks found, try a broader search
        if not all_chunks:
            try:
                query_embedding = embedding_service.generate_embedding("textbook content")
                if query_embedding:
                    search_results = qdrant_service.search_similar(
                        query_vector=query_embedding,
                        limit=5,
                        filter_conditions={'document_id': document_id}
                    )
                    all_chunks = [result['payload'].get('text', '') for result in search_results if result['payload'].get('text')]
            except Exception as e:
                print(f"Error in fallback search: {e}")
        
        # Build context from retrieved chunks (limit to first 2000 chars)
        context = "\n\n".join(all_chunks[:5])[:2000]
        
        # If we have context, generate questions using LLM
        if context and len(context.strip()) > 50:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=Config.OPENAI_API_KEY)
                
                user_prompt = f"""Here is content from a textbook that was just uploaded:

{context}

Based on this textbook content, create exactly 4-5 questions that a student would ask to start learning. Each question must:
1. Be a complete question ending with a question mark
2. Be directly related to the content above
3. Help understand the main topics
4. Be suitable for a beginner

Output format: Write each question on a separate line. Do not include any explanations, numbering, or other text - only the questions."""

                response = client.chat.completions.create(
                    model=Config.OPENAI_CHAT_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that generates educational questions based on textbook content. Always respond with only the questions, nothing else."},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.8,
                    max_tokens=300
                )
                
                suggestions_text = response.choices[0].message.content.strip()
                
                # Parse suggestions into a list
                question_list = []
                for line in suggestions_text.split('\n'):
                    line = line.strip()
                    # Remove numbering, bullets, etc.
                    line = line.lstrip('1234567890.-*•) ').strip()
                    # Remove common prefixes
                    for prefix in ['Question:', 'Q:', '•', '-', '*']:
                        if line.lower().startswith(prefix.lower()):
                            line = line[len(prefix):].strip()
                    # Only add if it's a valid question
                    if line and len(line) > 15 and '?' in line:
                        question_list.append(line)
                
                # Limit to 5 questions
                question_list = question_list[:5]
                
                if question_list and len(question_list) >= 3:
                    return jsonify({
                        'success': True,
                        'suggestions': question_list
                    }), 200
            except Exception as e:
                print(f"Error generating suggestions with LLM: {e}")
        
        # Fallback: Return generic but useful questions
        fallback_questions = [
            "What is the main topic of this textbook?",
            "Can you summarize the key points?",
            "What are the important concepts I should learn?",
            "Can you explain the basics in simpler terms?"
        ]
        
        return jsonify({
            'success': True,
            'suggestions': fallback_questions
        }), 200
        
    except Exception as e:
        print(f"Error in get_suggestions: {e}")
        return jsonify({
            'success': True,
            'suggestions': [
                "What is the main topic of this textbook?",
                "Can you summarize the key points?",
                "What are the important concepts I should learn?",
                "Can you explain the basics in simpler terms?"
            ]
        }), 200

@chat_bp.route('/history/<session_id>', methods=['GET'])
def get_conversation_history(session_id):
    """
    Retrieve conversation history for a session
    """
    try:
        supabase_service = get_supabase_service()
        if supabase_service:
            history = supabase_service.get_conversation_history(session_id)
            return jsonify({'success': True, 'history': history}), 200
        else:
            # Return in-memory history if Supabase is not available
            memory_service = get_memory_service()
            history = memory_service.get_conversation_history(session_id)
            return jsonify({'success': True, 'history': history}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
