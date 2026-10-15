"""
Qdrant Vector Database Service Module
Handles connection, embedding generation (sentence-transformers/all-MiniLM-L6-v2, 384d),
collection creation, payload indexing, vector upsert, deletion, and semantic similarity search.
"""

from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
import os
import requests

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION_NAME = "product_embeddings"
VECTOR_DIMENSION = 384

# Global cached client and model instances
_client = None
_model = None


def get_qdrant_client():
    """Return a singleton QdrantClient instance with version check warning suppressed."""
    global _client
    if _client is None:
        _client = QdrantClient(
            host=QDRANT_HOST,
            port=QDRANT_PORT,
            timeout=10.0,
            check_compatibility=False
        )
    return _client


def get_embedding_model():
    """Return a singleton SentenceTransformer model instance (all-MiniLM-L6-v2)."""
    global _model
    if _model is None:
        print("Loading sentence-transformers/all-MiniLM-L6-v2 embedding model...")
        _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _model


def generate_embedding(text):
    """Generate a normalized 384-dimensional vector embedding for the input text."""
    if not text or not text.strip():
        text = "product"
    model = get_embedding_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def init_qdrant_collection(recreate=False):
    """
    Ensure the Qdrant collection 'product_embeddings' exists with Cosine distance.
    Creates payload index on 'category' for metadata filtering.
    """
    client = get_qdrant_client()
    exists = client.collection_exists(COLLECTION_NAME)

    if recreate and exists:
        print(f"Deleting existing Qdrant collection '{COLLECTION_NAME}' for clean recreation...")
        client.delete_collection(COLLECTION_NAME)
        exists = False

    if not exists:
        print(f"Creating Qdrant collection '{COLLECTION_NAME}' (384 dimensions, Cosine distance)...")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=VECTOR_DIMENSION,
                distance=models.Distance.COSINE
            )
        )
        # Create payload index on category for fast filtering
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="category",
            field_schema=models.PayloadSchemaType.KEYWORD
        )
        print("Collection and payload index created successfully.")
    else:
        print(f"Collection '{COLLECTION_NAME}' already exists.")


def upsert_product_vector(product_id, product_name, category, description, price, stock_quantity):
    """
    Generate embedding for product text and upsert point into Qdrant.
    Idempotent operation (updates existing point if product_id exists).
    """
    client = get_qdrant_client()
    full_text = f"{product_name}. {description if description else ''}"
    vector = generate_embedding(full_text)

    point = models.PointStruct(
        id=int(product_id),
        vector=vector,
        payload={
            "product_id": int(product_id),
            "product_name": product_name,
            "category": category,
            "price": float(price),
            "stock_quantity": int(stock_quantity)
        }
    )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[point]
    )
    return True


def delete_product_vector(product_id):
    """Delete a product vector point from Qdrant by its product_id."""
    client = get_qdrant_client()
    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=models.PointIdsList(points=[int(product_id)])
    )
    return True


def get_collection_stats():
    """Retrieve collection status, total vector count, and health info."""
    try:
        client = get_qdrant_client()
        if not client.collection_exists(COLLECTION_NAME):
            return {
                "status": "not_created",
                "collection_name": COLLECTION_NAME,
                "vector_count": 0,
                "dimension": VECTOR_DIMENSION,
                "message": f"Collection '{COLLECTION_NAME}' has not been initialized."
            }
        
        info = client.get_collection(COLLECTION_NAME)
        count_res = client.count(COLLECTION_NAME)

        return {
            "status": "online",
            "collection_name": COLLECTION_NAME,
            "vector_count": count_res.count,
            "points_count": info.points_count,
            "indexed_vectors_count": getattr(info, "indexed_vectors_count", count_res.count),
            "dimension": VECTOR_DIMENSION,
            "distance": "Cosine",
            "collection_status": str(info.status)
        }
    except Exception as e:
        return {
            "status": "offline",
            "collection_name": COLLECTION_NAME,
            "vector_count": 0,
            "dimension": VECTOR_DIMENSION,
            "error": str(e)
        }


def search_products_semantic(query_text, category=None, limit=10):
    """
    Perform semantic similarity search on Qdrant.
    Optional category filter.
    Returns ranked list of:
    [{'product_id': int, 'score': float, 'payload': dict}, ...]
    """
    client = get_qdrant_client()
    query_vector = generate_embedding(query_text)

    # Use query_points (official method in Qdrant)
    try:
        query_filter = None
        if category and category != "All":
            query_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="category",
                        match=models.MatchValue(value=category)
                    )
                ]
            )

        response = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            query_filter=query_filter,
            limit=limit,
            with_payload=True
        )

        results = []
        for point in response.points:
            results.append({
                "product_id": int(point.id),
                "score": round(float(point.score), 4),
                "payload": point.payload
            })
        return results

    except Exception:
        # Fallback to standard HTTP REST search endpoint if query_points API varies
        search_payload = {
            "vector": query_vector,
            "limit": limit,
            "with_payload": True
        }
        if category and category != "All":
            search_payload["filter"] = {
                "must": [{"key": "category", "match": {"value": category}}]
            }
        
        url = f"http://{QDRANT_HOST}:{QDRANT_PORT}/collections/{COLLECTION_NAME}/points/search"
        resp = requests.post(url, json=search_payload, timeout=5)
        if resp.status_code == 200:
            data = resp.json().get("result", [])
            return [
                {
                    "product_id": int(r["id"]),
                    "score": round(float(r["score"]), 4),
                    "payload": r.get("payload", {})
                }
                for r in data
            ]
        return []


if __name__ == "__main__":
    init_qdrant_collection()
    stats = get_collection_stats()
    print("Collection stats:", stats)
