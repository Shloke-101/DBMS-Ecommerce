"""
Test Suite for Flask Backend & Qdrant Integration
Tests:
1. Product listing & category filtering
2. Qdrant status & statistics
3. Keyword search (SQLite LIKE)
4. Semantic search (Qdrant ANN + SQLite hydration)
5. Category-filtered semantic search
6. Product addition with vector synchronization
7. Product update with vector synchronization
8. Product deletion with vector deletion
"""

import unittest
import json
from app import app
import database
import qdrant_service


class BackendTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_01_get_products(self):
        """Test retrieving all products from SQLite."""
        response = self.client.get("/api/products")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "success")
        self.assertGreaterEqual(data["count"], 35)

    def test_02_get_categories(self):
        """Test retrieving distinct category list."""
        response = self.client.get("/api/categories")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("Electronics", data["data"])
        self.assertIn("Clothing", data["data"])
        self.assertIn("Books", data["data"])

    def test_03_qdrant_stats(self):
        """Test Qdrant collection status endpoint."""
        response = self.client.get("/api/qdrant/stats")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["data"]["status"], "online")
        self.assertGreaterEqual(data["data"]["vector_count"], 35)

    def test_04_keyword_search(self):
        """Test SQL LIKE keyword search."""
        response = self.client.get("/api/search/keyword?q=laptop")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["search_type"], "keyword_sql")
        self.assertGreaterEqual(data["count"], 1)

    def test_05_semantic_search(self):
        """Test natural language semantic search via Qdrant + SQLite hydration."""
        query = "Affordable headphones for travelling"
        response = self.client.get(f"/api/search/semantic?q={query}&limit=3")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["search_type"], "semantic_vector")
        self.assertGreater(data["count"], 0)
        top_result = data["data"][0]
        self.assertIn("similarity_score", top_result)
        self.assertIn("product_name", top_result)
        self.assertIn("Headphones", top_result["product_name"])

    def test_06_category_filtered_semantic_search(self):
        """Test semantic search with category payload filter."""
        query = "Comfortable shoes for running"
        response = self.client.get(f"/api/search/semantic?q={query}&category=Clothing&limit=2")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertGreater(data["count"], 0)
        for item in data["data"]:
            self.assertEqual(item["category"], "Clothing")

    def test_07_product_crud_lifecycle(self):
        """Test dual-write product creation, update, and deletion in SQLite & Qdrant."""
        # 1. Add product
        new_prod = {
            "product_name": "Test Wireless Gaming Mouse 16000 DPI",
            "category": "Electronics",
            "description": "High precision wireless optical gaming mouse with programmable macros and ultra-low latency.",
            "price": 39.99,
            "stock_quantity": 25
        }
        res_add = self.client.post("/api/products", json=new_prod)
        self.assertEqual(res_add.status_code, 201)
        data_add = res_add.get_json()
        prod_id = data_add["data"]["product_id"]
        self.assertTrue(data_add["vector_synced"])

        # Verify in SQLite
        db_prod = database.get_product_by_id(prod_id)
        self.assertIsNotNone(db_prod)

        # 2. Update product
        update_data = {
            "product_name": "Test Wireless Gaming Mouse RGB 16000 DPI",
            "price": 44.99,
            "stock_quantity": 20
        }
        res_upd = self.client.put(f"/api/products/{prod_id}", json=update_data)
        self.assertEqual(res_upd.status_code, 200)
        data_upd = res_upd.get_json()
        self.assertEqual(data_upd["data"]["price"], 44.99)

        # 3. Delete product
        res_del = self.client.delete(f"/api/products/{prod_id}")
        self.assertEqual(res_del.status_code, 200)
        self.assertTrue(res_del.get_json()["vector_deleted"])

        # Verify deletion from SQLite
        self.assertIsNone(database.get_product_by_id(prod_id))


if __name__ == "__main__":
    unittest.main()
