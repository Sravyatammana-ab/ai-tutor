from typing import List, Dict, Optional
import time

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    PayloadSchemaType,
    PointIdsList
)

from config import Config


class VectorStoreService:
    """Wrapper around Qdrant client for vector storage and retrieval."""

    _shared_client: Optional[QdrantClient] = None
    _checked_collections: set = set()

    def __init__(self) -> None:
        if not Config.QDRANT_URL:
            raise ValueError("QDRANT_URL is not configured")

        qdrant_url = Config.QDRANT_URL.strip()
        if qdrant_url.endswith(":6333"):
            qdrant_url = qdrant_url[:-5]

        if VectorStoreService._shared_client is None:
            VectorStoreService._shared_client = QdrantClient(
                url=qdrant_url,
                api_key=Config.QDRANT_API_KEY or None,
            )

        self.client = VectorStoreService._shared_client
        self.collection_name = Config.QDRANT_COLLECTION_NAME
        self.vector_size = Config.QDRANT_VECTOR_SIZE or 1536

    ##########################################################################
    #  COLLECTION CREATION — uses vector name "default"
    ##########################################################################
    def create_collection_if_not_exists(self) -> None:
        # Use collection name as key for checked collections
        if self.collection_name in VectorStoreService._checked_collections:
            # Skip if we've already verified this collection exists
            try:
                collections = self.client.get_collections()
                names = [c.name for c in collections.collections]
                if self.collection_name in names:
                    return
                # Collection was deleted, remove from checked set
                VectorStoreService._checked_collections.discard(self.collection_name)
            except Exception:
                # If we can't check, proceed to creation attempt
                VectorStoreService._checked_collections.discard(self.collection_name)

        try:
            collections = self.client.get_collections()
            names = [c.name for c in collections.collections]
        except Exception as e:
            print(f"Error getting collections: {e}")
            raise

        # CREATE COLLECTION ONLY IF IT DOES NOT EXIST
        if self.collection_name not in names:
            try:
                # ALWAYS create collection with named vector "default"
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config={
                        "default": VectorParams(
                            size=self.vector_size,
                            distance=Distance.COSINE,
                        )
                    }
                )
                print(f"✓ Created collection '{self.collection_name}' with vector_name='default' (size={self.vector_size}, distance=Cosine)")
            except Exception as e:
                print(f"✗ Error creating collection: {e}")
                raise

            # Create payload indexes
            try:
                self.ensure_payload_index("document_id")
                self.ensure_payload_index("file_hash")
                print("✓ Payload indexes created")
            except Exception as e:
                print(f"⚠ Could not create payload indexes: {e}")
        else:
            print(f"✓ Collection '{self.collection_name}' already exists")

        # Mark as checked
        VectorStoreService._checked_collections.add(self.collection_name)

    ##########################################################################
    #  PAYLOAD INDEX
    ##########################################################################
    def ensure_payload_index(self, field_name: str, field_type: PayloadSchemaType = PayloadSchemaType.KEYWORD):
        try:
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name=field_name,
                field_schema=field_type,
            )
        except Exception as exc:
            if "already has index" not in str(exc).lower():
                raise

    ##########################################################################
    #  UPSERT
    ##########################################################################
    def upsert_points_batch(self, points: List[Dict]) -> None:
        if not points:
            return

        # ALWAYS use named vector "default" for upserting
        structs = [
            PointStruct(
                id=p["id"],
                vector={"default": p["vector"]},  # Named vector "default"
                payload=p["payload"]
            )
            for p in points
        ]

        self.client.upsert(
            collection_name=self.collection_name,
            points=structs,
            wait=False
        )

    def upsert_points_in_batches(self, points: List[Dict], batch_size: int = 24) -> None:
        if not points:
            return

        self.create_collection_if_not_exists()

        batch_size = max(1, batch_size)

        for start in range(0, len(points), batch_size):
            chunk = points[start:start + batch_size]

            last_err = None
            for attempt in range(3):
                try:
                    self.upsert_points_batch(chunk)
                    last_err = None
                    break
                except Exception as exc:
                    last_err = exc
                    time.sleep(1 * (2 ** attempt))

            if last_err:
                raise last_err

    ##########################################################################
    #  SEARCH
    ##########################################################################
    def _build_filter(self, filter_conditions: Optional[Dict]) -> Optional[Filter]:
        if not filter_conditions:
            return None

        conditions = []
        for key, value in filter_conditions.items():
            # Validate value is a primitive type (str, int, bool, float)
            # MatchValue only accepts primitive types, not dicts or lists
            if isinstance(value, (dict, list)):
                # If value is a dict/list, log error and skip this condition
                print(f"[WARNING] Filter value for key '{key}' is {type(value).__name__}, expected primitive. Value: {value}")
                continue
            
            # Ensure value is a valid primitive type for MatchValue
            if value is None:
                print(f"[WARNING] Filter value for key '{key}' is None, skipping")
                continue
            
            # Convert to string if needed (MatchValue accepts str, int, bool, float)
            if not isinstance(value, (str, int, bool, float)):
                value = str(value)
            
            try:
                conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value)
                    )
                )
            except Exception as e:
                print(f"[ERROR] Failed to create filter condition for key '{key}' with value {value}: {e}")
                continue
        
        if not conditions:
            return None
        
        return Filter(must=conditions)

    def search_similar(self, query_vector: List[float], limit: int = 5, filter_conditions: Optional[Dict] = None):
        self.create_collection_if_not_exists()

        query_filter = self._build_filter(filter_conditions)

        # ALWAYS use vector_name="default" explicitly
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            vector_name="default",  # Named vector "default"
            limit=limit,
            query_filter=query_filter,
            with_payload=True,
            with_vectors=False,
        )

        formatted = []
        for r in results:
            formatted.append({
                "score": r.score,
                "payload": r.payload,
            })
        return formatted

    ##########################################################################
    #  DOCUMENT METADATA
    ##########################################################################
    def get_document_metadata_samples(self, document_id: str, limit: int = 64):
        self.create_collection_if_not_exists()

        payloads = []
        try:
            filter_condition = Filter(
                must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))]
            )

            next_offset = None
            remaining = limit

            while remaining > 0:
                points, next_offset = self.client.scroll(
                    collection_name=self.collection_name,
                    scroll_filter=filter_condition,
                    limit=remaining,
                    with_payload=True,
                    with_vectors=False,
                    offset=next_offset,
                )

                if not points:
                    break

                payloads.extend([p.payload for p in points if p.payload])
                remaining = limit - len(payloads)

                if not next_offset:
                    break

        except Exception as exc:
            print(f"Error fetching metadata: {exc}")

        return payloads

    ##########################################################################
    #  SEARCH BY HASH
    ##########################################################################
    def search_by_hash(self, file_hash: str):
        self.create_collection_if_not_exists()

        try:
            filter_condition = Filter(
                must=[FieldCondition(key="file_hash", match=MatchValue(value=file_hash))]
            )

            results, _ = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=filter_condition,
                limit=1,
                with_payload=True,
                with_vectors=False,
            )

            if results:
                payload = results[0].payload
                return [{
                    "document_id": payload.get("document_id"),
                    "filename": payload.get("filename"),
                    "file_hash": file_hash
                }]

            return []

        except Exception as e:
            print(f"Error searching by hash: {e}")
            return []

    ##########################################################################
    #  DELETE BY HASH
    ##########################################################################
    def delete_by_hash(self, file_hash: str):
        self.create_collection_if_not_exists()

        try:
            filter_condition = Filter(
                must=[FieldCondition(key="file_hash", match=MatchValue(value=file_hash))]
            )

            results, _ = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=filter_condition,
                limit=10000,
                with_payload=False,
                with_vectors=False,
            )

            if results:
                ids = [p.id for p in results]

                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=PointIdsList(points=ids)
                )
                print(f"Deleted {len(ids)} points with hash {file_hash}")

        except Exception as e:
            print(f"Error deleting by hash: {e}")
