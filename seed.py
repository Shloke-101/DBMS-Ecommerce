"""
End-to-End Seed & Synchronization Pipeline
1. Initializes SQLite schema and seeds 35 curated products.
2. Initializes Qdrant vector collection 'product_embeddings' (384-d, Cosine).
3. Indexes all SQLite products into Qdrant with dense vectors and metadata.
4. Verifies count and runs a test semantic similarity search.
"""

from database import get_db_connection
from init_sqlite import seed_sqlite
from qdrant_service import (
    init_qdrant_collection,
    upsert_product_vector,
    get_collection_stats,
    search_products_semantic
)


def seed_all():
    print("\n[Step 1/3] Initializing SQLite Relational Database...")
    seed_sqlite()

    print("\n[Step 2/3] Initializing Qdrant Vector Collection...")
    init_qdrant_collection(recreate=False)

    print("\n[Step 3/3] Generating Embeddings and Indexing Products into Qdrant...")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Products ORDER BY product_id ASC")
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()

    indexed_count = 0
    for p in products:
        upsert_product_vector(
            product_id=p["product_id"],
            product_name=p["product_name"],
            category=p["category"],
            description=p["description"],
            price=p["price"],
            stock_quantity=p["stock_quantity"]
        )
        indexed_count += 1
        print(f" -> Indexed [{p['product_id']}] {p['product_name'][:40]}... in Qdrant")

    stats = get_collection_stats()
    print("\n==================================================")
    print("SEEDING & INDEXING COMPLETE!")
    print("==================================================")
    print(f"Total SQLite Products Indexed : {indexed_count}")
    print(f"Total Qdrant Vectors Stored   : {stats.get('vector_count', 0)}")
    print(f"Collection Status             : {stats.get('status', 'unknown')}")
    print("==================================================")

    # Verification Query
    test_query = "Affordable headphones for travelling"
    print(f"\n[Verification] Running Test Semantic Search: '{test_query}'")
    results = search_products_semantic(test_query, limit=3)
    for r in results:
        print(f" * Score: {r['score']:.4f} | ID: {r['product_id']} | Name: {r['payload']['product_name']} (${r['payload']['price']})")
    print("==================================================\n")


if __name__ == "__main__":
    seed_all()
