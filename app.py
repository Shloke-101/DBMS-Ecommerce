"""
Flask Web Application & REST API
E-Commerce Database Management System Using Qdrant Vector Database
Demonstrates hybrid architecture: SQLite (relational source of truth) + Qdrant (semantic vector search).
"""

from flask import Flask, render_template, request, jsonify
import database
import qdrant_service
from seed import seed_all

app = Flask(__name__)


# ---------------------------------------------------------
# Web Page Route
# ---------------------------------------------------------
@app.route("/")
def index():
    """Serve the single-page responsive product catalogue."""
    return render_template("index.html")


# ---------------------------------------------------------
# Product Listing & Category Filter
# ---------------------------------------------------------
@app.route("/api/products", methods=["GET"])
def list_products():
    """Retrieve all products, optionally filtered by category from SQLite."""
    category = request.args.get("category", "").strip()
    products = database.get_all_products(category=category if category else None)
    return jsonify({
        "status": "success",
        "count": len(products),
        "data": products
    })


@app.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    """Retrieve a single product by ID from SQLite."""
    product = database.get_product_by_id(product_id)
    if not product:
        return jsonify({"status": "error", "message": f"Product with ID {product_id} not found."}), 404
    return jsonify({"status": "success", "data": product})


# ---------------------------------------------------------
# Product CRUD Operations (Dual-Write SQLite + Qdrant)
# ---------------------------------------------------------
@app.route("/api/products", methods=["POST"])
def add_product():
    """
    Insert a product into SQLite and immediately index its embedding in Qdrant.
    """
    data = request.get_json() or {}
    name = data.get("product_name", "").strip()
    category = data.get("category", "").strip()
    description = data.get("description", "").strip()
    price = data.get("price")
    stock_quantity = data.get("stock_quantity")

    if not name or not category or price is None or stock_quantity is None:
        return jsonify({"status": "error", "message": "Fields product_name, category, price, and stock_quantity are required."}), 400

    try:
        price = float(price)
        stock_quantity = int(stock_quantity)
    except ValueError:
        return jsonify({"status": "error", "message": "Price must be a valid number and stock_quantity an integer."}), 400

    # 1. Authoritative write to SQLite
    product_id = database.add_product(name, category, description, price, stock_quantity)

    # 2. Synchronize to Qdrant Vector DB
    try:
        qdrant_service.upsert_product_vector(
            product_id=product_id,
            product_name=name,
            category=category,
            description=description,
            price=price,
            stock_quantity=stock_quantity
        )
        vector_synced = True
    except Exception as e:
        print(f"Warning: Failed to index product {product_id} in Qdrant: {e}")
        vector_synced = False

    created_product = database.get_product_by_id(product_id)
    return jsonify({
        "status": "success",
        "message": "Product created successfully.",
        "vector_synced": vector_synced,
        "data": created_product
    }), 201


@app.route("/api/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    """
    Update a product in SQLite and update its vector and payload in Qdrant.
    """
    existing = database.get_product_by_id(product_id)
    if not existing:
        return jsonify({"status": "error", "message": f"Product with ID {product_id} not found."}), 404

    data = request.get_json() or {}
    name = data.get("product_name", existing["product_name"]).strip()
    category = data.get("category", existing["category"]).strip()
    description = data.get("description", existing["description"]).strip()
    price = data.get("price", existing["price"])
    stock_quantity = data.get("stock_quantity", existing["stock_quantity"])

    try:
        price = float(price)
        stock_quantity = int(stock_quantity)
    except ValueError:
        return jsonify({"status": "error", "message": "Price and stock_quantity must be valid numbers."}), 400

    # 1. Update SQLite
    database.update_product(product_id, name, category, description, price, stock_quantity)

    # 2. Update vector & payload in Qdrant
    try:
        qdrant_service.upsert_product_vector(
            product_id=product_id,
            product_name=name,
            category=category,
            description=description,
            price=price,
            stock_quantity=stock_quantity
        )
        vector_synced = True
    except Exception as e:
        print(f"Warning: Failed to update vector in Qdrant: {e}")
        vector_synced = False

    updated_product = database.get_product_by_id(product_id)
    return jsonify({
        "status": "success",
        "message": "Product updated successfully.",
        "vector_synced": vector_synced,
        "data": updated_product
    })


@app.route("/api/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    """
    Delete a product from SQLite and remove its point from Qdrant.
    """
    existing = database.get_product_by_id(product_id)
    if not existing:
        return jsonify({"status": "error", "message": f"Product with ID {product_id} not found."}), 404

    # 1. Delete from SQLite
    database.delete_product(product_id)

    # 2. Delete from Qdrant
    try:
        qdrant_service.delete_product_vector(product_id)
        vector_deleted = True
    except Exception as e:
        print(f"Warning: Failed to delete vector from Qdrant: {e}")
        vector_deleted = False

    return jsonify({
        "status": "success",
        "message": f"Product {product_id} deleted successfully.",
        "vector_deleted": vector_deleted
    })


# ---------------------------------------------------------
# Search Endpoints (Keyword vs Semantic)
# ---------------------------------------------------------
@app.route("/api/search/keyword", methods=["GET"])
def search_keyword():
    """
    Traditional lexical keyword search using SQLite LIKE query across name and description.
    """
    query = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()

    if not query:
        return jsonify({"status": "error", "message": "Search query parameter 'q' is required."}), 400

    results = database.search_products_keyword(query, category=category if category else None)
    return jsonify({
        "status": "success",
        "search_type": "keyword_sql",
        "query": query,
        "count": len(results),
        "data": results
    })


@app.route("/api/search/semantic", methods=["GET"])
def search_semantic():
    """
    AI-powered semantic search:
    1. Generates 384d embedding for query string.
    2. Searches Qdrant collection with optional category payload filter.
    3. Retrieves ranked product IDs and similarity scores.
    4. Fetches authoritative product details from SQLite.
    5. Returns ranked list with similarity scores.
    """
    query = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    limit = int(request.args.get("limit", 10))

    if not query:
        return jsonify({"status": "error", "message": "Search query parameter 'q' is required."}), 400

    try:
        # Step 1 & 2: Qdrant ANN search
        vector_results = qdrant_service.search_products_semantic(
            query_text=query,
            category=category if category else None,
            limit=limit
        )

        if not vector_results:
            return jsonify({
                "status": "success",
                "search_type": "semantic_vector",
                "query": query,
                "count": 0,
                "data": []
            })

        # Step 3: Extract IDs and scores mapping
        product_ids = [r["product_id"] for r in vector_results]
        scores_map = {r["product_id"]: r["score"] for r in vector_results}

        # Step 4: Hydrate current authoritative records from SQLite
        sqlite_products = database.get_products_by_ids(product_ids)

        # Step 5: Attach similarity scores and preserve rank order
        enriched_results = []
        for p in sqlite_products:
            score = scores_map.get(p["product_id"], 0.0)
            item = dict(p)
            item["similarity_score"] = score
            item["similarity_percentage"] = f"{round(score * 100, 1)}%"
            enriched_results.append(item)

        return jsonify({
            "status": "success",
            "search_type": "semantic_vector",
            "query": query,
            "category_filter": category if category else "All",
            "count": len(enriched_results),
            "data": enriched_results
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Semantic search failed: {str(e)}"
        }), 500


# ---------------------------------------------------------
# Metadata & Diagnostic Endpoints
# ---------------------------------------------------------
@app.route("/api/categories", methods=["GET"])
def get_categories():
    """Retrieve distinct category list."""
    categories = database.get_categories()
    return jsonify({
        "status": "success",
        "data": categories
    })


@app.route("/api/qdrant/stats", methods=["GET"])
def qdrant_stats():
    """Retrieve live Qdrant collection statistics and health."""
    stats = qdrant_service.get_collection_stats()
    return jsonify({
        "status": "success",
        "data": stats
    })


@app.route("/api/seed", methods=["POST"])
def trigger_seed():
    """Admin endpoint to re-seed and re-index the database."""
    try:
        seed_all()
        stats = qdrant_service.get_collection_stats()
        return jsonify({
            "status": "success",
            "message": "Database and vector index re-seeded successfully.",
            "data": stats
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Seeding failed: {str(e)}"
        }), 500


if __name__ == "__main__":
    print("Starting Flask E-Commerce Server on http://127.0.0.1:5000 ...")
    app.run(host="127.0.0.1", port=5000, debug=True)
