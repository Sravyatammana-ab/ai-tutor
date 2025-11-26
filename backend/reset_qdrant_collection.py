#!/usr/bin/env python3
"""
Script to manually delete and recreate Qdrant collection.
Use this if you're getting vector_name errors.
"""
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

load_dotenv()

QDRANT_URL = os.getenv('QDRANT_URL', '').strip()
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY', '')
QDRANT_COLLECTION_NAME = os.getenv('QDRANT_COLLECTION_NAME', 'ai_tutor_documents')
QDRANT_VECTOR_SIZE = int(os.getenv('QDRANT_VECTOR_SIZE', 1536))

if not QDRANT_URL:
    print("ERROR: QDRANT_URL not set in .env file")
    exit(1)

if QDRANT_URL.endswith(":6333"):
    QDRANT_URL = QDRANT_URL[:-5]

print(f"Connecting to Qdrant at: {QDRANT_URL}")
print(f"Collection name: {QDRANT_COLLECTION_NAME}")

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY or None,
)

# Delete collection if it exists
try:
    collections = client.get_collections()
    if QDRANT_COLLECTION_NAME in [c.name for c in collections.collections]:
        print(f"Deleting existing collection: {QDRANT_COLLECTION_NAME}")
        client.delete_collection(QDRANT_COLLECTION_NAME)
        print("✓ Collection deleted")
    else:
        print("Collection does not exist, nothing to delete")
except Exception as e:
    print(f"Error deleting collection: {e}")

# Create new collection
try:
    print(f"Creating new collection: {QDRANT_COLLECTION_NAME}")
    print(f"Using named vector 'default' with size={QDRANT_VECTOR_SIZE}, distance=Cosine")
    client.create_collection(
        collection_name=QDRANT_COLLECTION_NAME,
        vectors_config={
            "default": VectorParams(
                size=QDRANT_VECTOR_SIZE,
                distance=Distance.COSINE,
            )
        },
    )
    print("✓ Collection created successfully with vector_name='default'!")
    print("\n⚠ IMPORTANT: You need to re-upload your documents now.")
    print("The old collection has been deleted and recreated with named vector config.")
except Exception as e:
    print(f"Error creating collection: {e}")
    exit(1)

