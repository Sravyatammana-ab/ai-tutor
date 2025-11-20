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
    PointsSelector,
    FilterSelector,
)

from config import Config


class QdrantService:
    """Wrapper around Qdrant client with a couple of convenience helpers."""

    def __init__(self) -> None:
        if not Config.QDRANT_URL:
            raise ValueError("QDRANT_URL is not configured")

        qdrant_url = Config.QDRANT_URL.strip()
        if qdrant_url.endswith(":6333"):
            qdrant_url = qdrant_url[:-5]

        self.client = QdrantClient(
            url=qdrant_url,
            api_key=Config.QDRANT_API_KEY or None,
        )
        self.collection_name = Config.QDRANT_COLLECTION_NAME
        self.vector_size = Config.QDRANT_VECTOR_SIZE or 1536

    def create_collection_if_not_exists(self) -> None:
        collections = self.client.get_collections()
        names = [collection.name for collection in collections.collections]
        if self.collection_name in names:
            return

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.vector_size,
                distance=Distance.COSINE,
            ),
        )
        self.ensure_payload_index("document_id")

    def ensure_payload_index(self, field_name: str, field_type: PayloadSchemaType = PayloadSchemaType.KEYWORD) -> None:
        try:
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name=field_name,
                field_schema=field_type,
            )
        except Exception as exc:
            # Index already exists
            if "already has index" not in str(exc).lower():
                raise

    def upsert_point(self, point_id: str, vector: List[float], payload: Dict) -> None:
        self.upsert_points_batch([{"id": point_id, "vector": vector, "payload": payload}])

    def upsert_points_batch(self, points: List[Dict]) -> None:
        if not points:
            return

        structs = [
            PointStruct(id=point["id"], vector=point["vector"], payload=point["payload"])
            for point in points
        ]
        self.client.upsert(
            collection_name=self.collection_name,
            points=structs,
            wait=False
        )

    def upsert_points_in_batches(self, points: List[Dict], batch_size: int = 24) -> None:
        if not points:
            return

        batch_size = max(1, batch_size)
        for start in range(0, len(points), batch_size):
            chunk = points[start:start + batch_size]
            # Retry with exponential backoff to avoid gateway/read timeouts
            last_exc: Optional[Exception] = None
            for attempt in range(3):
                try:
                    self.upsert_points_batch(chunk)
                    last_exc = None
                    break
                except Exception as exc:
                    last_exc = exc
                    # short sleep then retry
                    time.sleep(1.0 * (2 ** attempt))
            if last_exc:
                raise last_exc

    def _build_filter(self, filter_conditions: Optional[Dict]) -> Optional[Filter]:
        if not filter_conditions:
            return None
        conditions = [
            FieldCondition(key=key, match=MatchValue(value=value))
            for key, value in filter_conditions.items()
        ]
        if not conditions:
            return None
        return Filter(must=conditions)

    def search_similar(
        self,
        query_vector: List[float],
        limit: int = 5,
        filter_conditions: Optional[Dict] = None,
    ) -> List[Dict]:
        query_filter = self._build_filter(filter_conditions)
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            query_filter=query_filter,
            with_payload=True,
            with_vectors=False,
        )

        formatted = []
        for result in results:
            formatted.append(
                {
                    "score": result.score,
                    "payload": result.payload,
                }
            )
        return formatted
    
    def get_document_metadata_samples(self, document_id: str, limit: int = 64) -> List[Dict]:
        """
        Retrieve a sample of payloads for the supplied document to inspect metadata like chapter titles.
        """
        payloads: List[Dict] = []
        try:
            filter_condition = Filter(
                must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))]
            )
            next_offset = None
            remaining = max(1, limit)

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
                payloads.extend([point.payload for point in points if point.payload])
                remaining = limit - len(payloads)
                if not next_offset:
                    break
        except Exception as exc:
            print(f"Error fetching document metadata samples: {exc}")
        return payloads
    
    def search_by_hash(self, file_hash: str) -> List[Dict]:
        """Search for documents by file hash"""
        try:
            filter_condition = Filter(
                must=[FieldCondition(key="file_hash", match=MatchValue(value=file_hash))]
            )
            # Use scroll to get all points with this hash
            results, _ = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=filter_condition,
                limit=1,
                with_payload=True,
                with_vectors=False
            )
            
            if results:
                # Get unique document_id from first result
                first_result = results[0]
                payload = first_result.payload
                return [{
                    'document_id': payload.get('document_id'),
                    'filename': payload.get('filename'),
                    'file_hash': file_hash
                }]
            return []
        except Exception as e:
            print(f"Error searching by hash: {e}")
            return []
    
    def delete_by_hash(self, file_hash: str) -> None:
        """Delete all points with a given file hash"""
        try:
            # Get all point IDs with this hash
            filter_condition = Filter(
                must=[FieldCondition(key="file_hash", match=MatchValue(value=file_hash))]
            )
            results, _ = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=filter_condition,
                limit=10000,  # Large limit to get all
                with_payload=False,
                with_vectors=False
            )
            
            if results:
                point_ids = [point.id for point in results]
                # Delete points by IDs
                from qdrant_client.models import PointIdsList
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=PointIdsList(points=point_ids)
                )
                print(f"Deleted {len(point_ids)} points with hash {file_hash}")
        except Exception as e:
            print(f"Error deleting by hash: {e}")
            import traceback
            traceback.print_exc()
            # Don't raise - allow upload to continue

