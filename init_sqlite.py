"""
Stage 1: SQLite Database Initialization & Seed Script
Initializes normalized schema and populates sample categories, products, and orders idempotently.
"""

from database import get_db_connection, init_db
from sample_data import CATEGORIES, SAMPLE_PRODUCTS, SAMPLE_ORDERS


def seed_sqlite():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Seed Categories (idempotent via INSERT OR IGNORE)
    inserted_categories = 0
    for cat in CATEGORIES:
        cursor.execute("INSERT OR IGNORE INTO Categories (category_name) VALUES (?)", (cat,))
        if cursor.rowcount > 0:
            inserted_categories += 1

    # 2. Seed Products (idempotent: check if product_name already exists)
    inserted_products = 0
    skipped_products = 0
    for p in SAMPLE_PRODUCTS:
        cursor.execute("SELECT product_id FROM Products WHERE product_name = ?", (p["product_name"],))
        existing = cursor.fetchone()
        if existing:
            skipped_products += 1
        else:
            cursor.execute("""
                INSERT INTO Products (product_name, category, description, price, stock_quantity)
                VALUES (?, ?, ?, ?, ?)
            """, (p["product_name"], p["category"], p["description"], p["price"], p["stock_quantity"]))
            inserted_products += 1

    # 3. Seed Sample Orders (if none exist)
    cursor.execute("SELECT COUNT(*) AS cnt FROM Orders")
    order_count = cursor.fetchone()["cnt"]
    inserted_orders = 0
    if order_count == 0:
        for order in SAMPLE_ORDERS:
            total_amount = 0.0
            order_items_data = []
            for item in order["items"]:
                cursor.execute("SELECT product_id, price FROM Products WHERE product_name = ?", (item["product_name"],))
                prod = cursor.fetchone()
                if prod:
                    subtotal = prod["price"] * item["quantity"]
                    total_amount += subtotal
                    order_items_data.append((prod["product_id"], item["quantity"], prod["price"]))

            if order_items_data:
                cursor.execute("""
                    INSERT INTO Orders (customer_name, total_amount)
                    VALUES (?, ?)
                """, (order["customer_name"], round(total_amount, 2)))
                order_id = cursor.lastrowid
                inserted_orders += 1

                for prod_id, qty, unit_price in order_items_data:
                    cursor.execute("""
                        INSERT INTO Order_Items (order_id, product_id, quantity, price)
                        VALUES (?, ?, ?, ?)
                    """, (order_id, prod_id, qty, unit_price))

    conn.commit()

    # Print summary
    cursor.execute("SELECT COUNT(*) AS total FROM Products")
    total_products = cursor.fetchone()["total"]
    cursor.execute("SELECT COUNT(*) AS total FROM Categories")
    total_categories = cursor.fetchone()["total"]
    cursor.execute("SELECT COUNT(*) AS total FROM Orders")
    total_orders = cursor.fetchone()["total"]
    cursor.execute("SELECT COUNT(*) AS total FROM Order_Items")
    total_order_items = cursor.fetchone()["total"]
    conn.close()

    print("==================================================")
    print("STAGE 1: SQLite Database Seeding Completed")
    print("==================================================")
    print(f"Categories   : {total_categories} total (newly added: {inserted_categories})")
    print(f"Products     : {total_products} total (newly inserted: {inserted_products}, skipped: {skipped_products})")
    print(f"Orders       : {total_orders} total (newly inserted: {inserted_orders})")
    print(f"Order Items  : {total_order_items} total")
    print("==================================================")


if __name__ == "__main__":
    seed_sqlite()
