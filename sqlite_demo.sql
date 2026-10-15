-- ====================================================================
-- SQLite Relational Database Laboratory Demonstration Script
-- Demonstrates: INSERT, SELECT, UPDATE, DELETE, and relational JOINs
-- ====================================================================

-- 1. INSERT Operation: Add a new category and product
INSERT INTO Categories (category_name) 
VALUES ('Audio & Video');

INSERT INTO Products (product_name, category, description, price, stock_quantity)
VALUES ('Compact USB Condenser Microphone', 'Electronics', 'Studio cardioid microphone for podcasting, online lectures, and gaming.', 59.99, 40);

-- 2. SELECT Operation: Retrieve products with stock filtering and sorting
SELECT 
    product_id, 
    product_name, 
    category, 
    price, 
    stock_quantity
FROM Products
WHERE category = 'Electronics' AND price < 100.00
ORDER BY price ASC;

-- 3. UPDATE Operation: Adjust pricing and update inventory
UPDATE Products
SET price = 54.99, stock_quantity = 38
WHERE product_name = 'Compact USB Condenser Microphone';

-- 4. DELETE Operation: Remove a record with integrity constraint check
DELETE FROM Products
WHERE product_name = 'Compact USB Condenser Microphone';

-- 5. Relational JOIN Operation: Complete Order Details with Items and Product Info
SELECT 
    o.order_id,
    o.customer_name,
    o.order_date,
    p.product_name,
    p.category,
    oi.quantity,
    oi.price AS unit_price,
    ROUND(oi.quantity * oi.price, 2) AS line_item_subtotal,
    o.total_amount AS order_total
FROM Orders o
INNER JOIN Order_Items oi ON o.order_id = oi.order_id
INNER JOIN Products p ON oi.product_id = p.product_id
ORDER BY o.order_id ASC, oi.order_item_id ASC;

-- 6. Aggregate Query: Revenue and Items Sold Per Category
SELECT 
    p.category,
    COUNT(oi.order_item_id) AS total_orders_placed,
    SUM(oi.quantity) AS total_units_sold,
    ROUND(SUM(oi.quantity * oi.price), 2) AS total_category_revenue
FROM Order_Items oi
INNER JOIN Products p ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY total_category_revenue DESC;
