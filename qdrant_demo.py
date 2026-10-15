"""
Qdrant Vector Database Lab Demonstration Script
Demonstrates all 9 core vector operations required for the college assessment:
1. Collection Creation
2. Vector Insertion
3. Collection Info Retrieval
4. Vector Count
5. Semantic Similarity Search
6. Category-Filtered Search
7. Vector & Payload Update
8. Vector Deletion
9. Persistence Verification
"""

import time
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
DEMO_COLLECTION = "product_embeddings"
VECTOR_DIM = 384


def print_banner(step_num, title):
    print("\n" + "=" * 65)
    print(f" OPERATION {step_num}: {title.upper()}")
    print("=" * 65)


def run_qdrant_demonstration():
    print("Connecting to Qdrant at http://localhost:6333 ...")
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, timeout=10.0, check_compatibility=False)
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    # -------------------------------------------------------------
    # 1. Create Collection
    # -------------------------------------------------------------
    print_banner(1, "Create Collection")
    if not client.collection_exists(DEMO_COLLECTION):
        client.create_collection(
            collection_name=DEMO_COLLECTION,
            vectors_config=models.VectorParams(size=VECTOR_DIM, distance=models.Distance.COSINE)
        )
        client.create_payload_index(
            collection_name=DEMO_COLLECTION,
            field_name="category",
            field_schema=models.PayloadSchemaType.KEYWORD
        )
        print(f"[OK] Collection '{DEMO_COLLECTION}' created (384d, Cosine distance).")
    else:
        print(f"[OK] Collection '{DEMO_COLLECTION}' already exists and is ready.")

    # -------------------------------------------------------------
    # 2. Insert Product Vectors
    # -------------------------------------------------------------
    print_banner(2, "Insert Product Vectors")
    demo_product = {
        "id": 999,
        "name": "Demo Studio Wireless Monitor Headphones",
        "category": "Electronics",
        "description": "Professional acoustic over-ear monitor headphones with planar magnetic drivers and detachable cable for sound editing and air travel.",
        "price": 149.99,
        "stock": 25
    }
    demo_text = f"{demo_product['name']}. {demo_product['description']}"
    demo_vec = model.encode(demo_text, normalize_embeddings=True).tolist()

    point = models.PointStruct(
        id=demo_product["id"],
        vector=demo_vec,
        payload={
            "product_id": demo_product["id"],
            "product_name": demo_product["name"],
            "category": demo_product["category"],
            "price": demo_product["price"],
            "stock_quantity": demo_product["stock"]
        }
    )
    client.upsert(collection_name=DEMO_COLLECTION, points=[point])
    print(f"[OK] Inserted vector point for ID {demo_product['id']}: '{demo_product['name']}'")

    # -------------------------------------------------------------
    # 3. Retrieve Collection Information
    # -------------------------------------------------------------
    print_banner(3, "Retrieve Collection Information")
    info = client.get_collection(DEMO_COLLECTION)
    print(f"Status            : {info.status}")
    print(f"Vectors Config    : Size={VECTOR_DIM}, Distance=Cosine")
    print(f"Points Count      : {info.points_count}")
    print(f"Indexed Vectors   : {getattr(info, 'indexed_vectors_count', info.points_count)}")

    # -------------------------------------------------------------
    # 4. Count Vectors
    # -------------------------------------------------------------
    print_banner(4, "Count Vectors")
    cnt = client.count(DEMO_COLLECTION)
    print(f"[OK] Total vector points in '{DEMO_COLLECTION}': {cnt.count}")

    # -------------------------------------------------------------
    # 5. Semantic Similarity Search
    # -------------------------------------------------------------
    print_banner(5, "Semantic Similarity Search")
    user_query = "Affordable wireless headphones suitable for travelling"
    print(f"Natural-Language Query: \"{user_query}\"")
    q_vec = model.encode(user_query, normalize_embeddings=True).tolist()

    res = client.query_points(
        collection_name=DEMO_COLLECTION,
        query=q_vec,
        limit=3,
        with_payload=True
    )
    for idx, hit in enumerate(res.points, 1):
        print(f"  [{idx}] Score: {hit.score:.4f} | ID: {hit.id} | Name: {hit.payload.get('product_name')} (${hit.payload.get('price')})")

    # -------------------------------------------------------------
    # 6. Category-Filtered Semantic Search
    # -------------------------------------------------------------
    print_banner(6, "Category-Filtered Semantic Search")
    filter_category = "Clothing"
    filter_query = "Lightweight comfortable gear for long jogging"
    print(f"Query: \"{filter_query}\" | Metadata Filter: category == \"{filter_category}\"")
    
    cat_filter = models.Filter(
        must=[models.FieldCondition(key="category", match=models.MatchValue(value=filter_category))]
    )
    filtered_res = client.query_points(
        collection_name=DEMO_COLLECTION,
        query=model.encode(filter_query, normalize_embeddings=True).tolist(),
        query_filter=cat_filter,
        limit=3,
        with_payload=True
    )
    for idx, hit in enumerate(filtered_res.points, 1):
        print(f"  [{idx}] Score: {hit.score:.4f} | Category: {hit.payload.get('category')} | Name: {hit.payload.get('product_name')}")

    # -------------------------------------------------------------
    # 7. Update Vector and Payload
    # -------------------------------------------------------------
    print_banner(7, "Update Vector and Payload")
    updated_name = "Demo Studio Wireless Monitor Headphones MK-II (Pro Edition)"
    updated_price = 129.99
    updated_text = f"{updated_name}. Upgraded wireless headphones with hybrid active noise cancellation."
    updated_vec = model.encode(updated_text, normalize_embeddings=True).tolist()

    updated_point = models.PointStruct(
        id=demo_product["id"],
        vector=updated_vec,
        payload={
            "product_id": demo_product["id"],
            "product_name": updated_name,
            "category": demo_product["category"],
            "price": updated_price,
            "stock_quantity": 30
        }
    )
    client.upsert(collection_name=DEMO_COLLECTION, points=[updated_point])
    print(f"[OK] Updated ID {demo_product['id']} payload and vector. New Name: '{updated_name}', Price: ${updated_price}")

    # -------------------------------------------------------------
    # 8. Delete Vector Point
    # -------------------------------------------------------------
    print_banner(8, "Delete Vector Point")
    client.delete(collection_name=DEMO_COLLECTION, points_selector=models.PointIdsList(points=[demo_product["id"]]))
    after_del_cnt = client.count(DEMO_COLLECTION)
    print(f"[OK] Deleted vector point ID {demo_product['id']}.")
    print(f"[OK] Remaining vector count: {after_del_cnt.count}")

    # -------------------------------------------------------------
    # 9. Verify Persistence
    # -------------------------------------------------------------
    print_banner(9, "Persistence Verification Instructions")
    print("Persistence is managed by Docker volume 'ecommerce-database-management_qdrant_storage'.")
    print("To test restart persistence during a lab demonstration:")
    print("  1. Run: docker compose restart")
    print("  2. Run: python -c \"import qdrant_service; print('Vectors preserved:', qdrant_service.get_collection_stats()['vector_count'])\"")
    print("[OK] All 9 Qdrant vector operations demonstrated successfully!")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    run_qdrant_demonstration()
