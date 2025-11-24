"""
Utility script to verify Qdrant connectivity and collection availability.

Usage:
    python backend/test_qdrant_connection.py
"""

from pprint import pprint

from qdrant_client import QdrantClient

from config import Config


def main():
    client = QdrantClient(
        url=Config.QDRANT_URL,
        api_key=Config.QDRANT_API_KEY or None
    )
    collections = client.get_collections()
    print("Qdrant collections:")
    pprint(collections.dict())


if __name__ == "__main__":
    main()

