import sqlite3
import os

DB_NAME = "ecommerce.db"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, DB_NAME)


def get_db_connection():
    """Establish and return a SQLite database connection with row access by column name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all required relational tables with primary keys, foreign keys, and constraints."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Categories Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Categories (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name TEXT UNIQUE NOT NULL
    );
    """)

    # 2. Products Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL CHECK(price >= 0),
        stock_quantity INTEGER NOT NULL CHECK(stock_quantity >= 0)
    );
    """)

    # 3. Orders Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT NOT NULL,
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        total_amount REAL NOT NULL CHECK(total_amount >= 0)
    );
    """)

    # 4. Order_Items Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Order_Items (
        order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL CHECK(quantity > 0),
        price REAL NOT NULL CHECK(price >= 0),
        FOREIGN KEY (order_id) REFERENCES Orders (order_id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES Products (product_id) ON DELETE RESTRICT
    );
    """)

    conn.commit()
    conn.close()
    print("Database tables initialized successfully.")


def get_all_products(category=None):
    """Fetch all products, optionally filtered by category."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if category and category != "All":
        cursor.execute("SELECT * FROM Products WHERE category = ? ORDER BY product_id ASC", (category,))
    else:
        cursor.execute("SELECT * FROM Products ORDER BY product_id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_product_by_id(product_id):
    """Fetch a single product by its ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Products WHERE product_id = ?", (product_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_products_by_ids(product_ids):
    """Fetch multiple products preserving the order of the provided product_ids list."""
    if not product_ids:
        return []
    conn = get_db_connection()
    cursor = conn.cursor()
    placeholders = ",".join(["?"] * len(product_ids))
    cursor.execute(f"SELECT * FROM Products WHERE product_id IN ({placeholders})", product_ids)
    rows = cursor.fetchall()
    conn.close()

    products_map = {row["product_id"]: dict(row) for row in rows}
    # Preserve the ranking order returned by the vector search
    ordered_products = [products_map[pid] for pid in product_ids if pid in products_map]
    return ordered_products


def search_products_keyword(keyword, category=None):
    """Search products using traditional SQL LIKE keyword matching."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "%" + keyword.strip() + "%"
    if category and category != "All":
        cursor.execute("""
            SELECT * FROM Products 
            WHERE (product_name LIKE ? OR description LIKE ?) AND category = ?
            ORDER BY product_id ASC
        """, (query, query, category))
    else:
        cursor.execute("""
            SELECT * FROM Products 
            WHERE product_name LIKE ? OR description LIKE ?
            ORDER BY product_id ASC
        """, (query, query))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def add_product(product_name, category, description, price, stock_quantity):
    """Insert a new product record and return the generated product_id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Products (product_name, category, description, price, stock_quantity)
        VALUES (?, ?, ?, ?, ?)
    """, (product_name, category, description, float(price), int(stock_quantity)))
    product_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return product_id


def update_product(product_id, product_name, category, description, price, stock_quantity):
    """Update an existing product record."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE Products
        SET product_name = ?, category = ?, description = ?, price = ?, stock_quantity = ?
        WHERE product_id = ?
    """, (product_name, category, description, float(price), int(stock_quantity), product_id))
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated


def delete_product(product_id):
    """Delete a product record by its ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Products WHERE product_id = ?", (product_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


def get_categories():
    """Retrieve distinct list of categories."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT category_name FROM Categories ORDER BY category_name ASC")
    rows = cursor.fetchall()
    conn.close()
    return [row["category_name"] for row in rows]


if __name__ == "__main__":
    init_db()
