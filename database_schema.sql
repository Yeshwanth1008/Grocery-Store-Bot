-- Grocery Store Bot Database Schema
-- Run this script to create the required database structure

CREATE DATABASE IF NOT EXISTS grocery_store;
USE grocery_store;

-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    username VARCHAR(100),
    phone VARCHAR(20),
    registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_active DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Product categories table
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock INT DEFAULT 0,
    description TEXT,
    image_url VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_stock (stock)
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id VARCHAR(20) UNIQUE NOT NULL,
    customer_id BIGINT NOT NULL,
    items JSON NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    delivery_fee DECIMAL(10, 2) DEFAULT 0.00,
    total DECIMAL(10, 2) NOT NULL,
    order_type ENUM('delivery', 'takeaway') NOT NULL,
    delivery_address TEXT,
    phone VARCHAR(20),
    status ENUM('pending', 'confirmed', 'preparing', 'ready', 'delivered', 'cancelled') DEFAULT 'pending',
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    delivery_date DATETIME,
    notes TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(telegram_id) ON DELETE CASCADE,
    INDEX idx_customer (customer_id),
    INDEX idx_status (status),
    INDEX idx_order_date (order_date)
);

-- Order items table (for detailed tracking)
CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id VARCHAR(20) NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- Sales table for analytics
CREATE TABLE IF NOT EXISTS sales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id VARCHAR(20) NOT NULL,
    product_id INT NOT NULL,
    quantity_sold INT NOT NULL,
    revenue DECIMAL(10, 2) NOT NULL,
    sale_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    INDEX idx_sale_date (sale_date),
    INDEX idx_product (product_id)
);

-- Inventory tracking table
CREATE TABLE IF NOT EXISTS inventory_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    action ENUM('restock', 'sale', 'adjustment') NOT NULL,
    quantity_change INT NOT NULL,
    previous_stock INT NOT NULL,
    new_stock INT NOT NULL,
    reason VARCHAR(200),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- Customer addresses table
CREATE TABLE IF NOT EXISTS customer_addresses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    address_type ENUM('home', 'work', 'other') DEFAULT 'home',
    street_address TEXT NOT NULL,
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    is_default BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(telegram_id) ON DELETE CASCADE
);

-- Promotions table
CREATE TABLE IF NOT EXISTS promotions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    discount_type ENUM('percentage', 'fixed') NOT NULL,
    discount_value DECIMAL(10, 2) NOT NULL,
    min_order_amount DECIMAL(10, 2) DEFAULT 0.00,
    start_date DATETIME NOT NULL,
    end_date DATETIME NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    usage_limit INT DEFAULT NULL,
    used_count INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample categories
INSERT INTO categories (name, description) VALUES
('Fruits & Vegetables', 'Fresh fruits and vegetables'),
('Dairy & Eggs', 'Milk, cheese, yogurt, and eggs'),
('Meat & Seafood', 'Fresh meat and seafood products'),
('Bakery', 'Bread, pastries, and baked goods'),
('Pantry Staples', 'Rice, pasta, canned goods, and dry goods'),
('Beverages', 'Soft drinks, juices, and water'),
('Snacks', 'Chips, crackers, and snack foods'),
('Frozen Foods', 'Frozen vegetables, meals, and ice cream'),
('Personal Care', 'Toiletries and personal hygiene products'),
('Household', 'Cleaning supplies and household items');

-- Insert sample products
INSERT INTO products (name, category, price, stock, description) VALUES
-- Fruits & Vegetables
('Fresh Bananas (1 lb)', 'Fruits & Vegetables', 1.29, 50, 'Fresh ripe bananas'),
('Red Apples (1 lb)', 'Fruits & Vegetables', 2.49, 40, 'Crisp red apples'),
('Carrots (1 lb)', 'Fruits & Vegetables', 1.99, 30, 'Fresh orange carrots'),
('Tomatoes (1 lb)', 'Fruits & Vegetables', 3.49, 25, 'Ripe red tomatoes'),
('Spinach (1 bunch)', 'Fruits & Vegetables', 2.99, 20, 'Fresh spinach leaves'),

-- Dairy & Eggs
('Whole Milk (1 gallon)', 'Dairy & Eggs', 3.99, 35, 'Fresh whole milk'),
('Large Eggs (dozen)', 'Dairy & Eggs', 4.49, 40, 'Grade A large eggs'),
('Cheddar Cheese (8 oz)', 'Dairy & Eggs', 4.99, 25, 'Sharp cheddar cheese'),
('Greek Yogurt (32 oz)', 'Dairy & Eggs', 5.99, 20, 'Plain Greek yogurt'),

-- Meat & Seafood
('Ground Beef (1 lb)', 'Meat & Seafood', 6.99, 15, 'Fresh ground beef 80/20'),
('Chicken Breast (1 lb)', 'Meat & Seafood', 7.99, 20, 'Boneless chicken breast'),
('Salmon Fillet (1 lb)', 'Meat & Seafood', 12.99, 10, 'Fresh Atlantic salmon'),

-- Bakery
('White Bread (1 loaf)', 'Bakery', 2.99, 30, 'Fresh white bread'),
('Croissants (4 pack)', 'Bakery', 4.99, 15, 'Buttery croissants'),

-- Pantry Staples
('Jasmine Rice (2 lb)', 'Pantry Staples', 3.99, 40, 'Premium jasmine rice'),
('Spaghetti Pasta (1 lb)', 'Pantry Staples', 1.99, 50, 'Italian spaghetti pasta'),
('Olive Oil (500ml)', 'Pantry Staples', 8.99, 20, 'Extra virgin olive oil'),

-- Beverages
('Coca Cola (12 pack)', 'Beverages', 5.99, 30, '12 pack of Coca Cola cans'),
('Orange Juice (64 oz)', 'Beverages', 4.49, 25, 'Fresh orange juice'),
('Bottled Water (24 pack)', 'Beverages', 4.99, 40, '24 pack of bottled water'),

-- Snacks
('Potato Chips (family size)', 'Snacks', 3.99, 35, 'Crispy potato chips'),
('Mixed Nuts (1 lb)', 'Snacks', 7.99, 20, 'Assorted mixed nuts'),

-- Frozen Foods
('Frozen Pizza (12 inch)', 'Frozen Foods', 6.99, 15, 'Pepperoni pizza'),
('Ice Cream (1.5 qt)', 'Frozen Foods', 5.99, 20, 'Vanilla ice cream'),

-- Personal Care
('Shampoo (16 oz)', 'Personal Care', 6.99, 25, 'Moisturizing shampoo'),
('Toothpaste (4 oz)', 'Personal Care', 3.49, 30, 'Fluoride toothpaste'),

-- Household
('Dish Soap (32 oz)', 'Household', 4.99, 20, 'Grease-cutting dish soap'),
('Paper Towels (8 rolls)', 'Household', 12.99, 15, 'Absorbent paper towels');

-- Create indexes for better performance
CREATE INDEX idx_products_name ON products(name);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_customers_telegram ON customers(telegram_id);

-- Views for analytics
CREATE VIEW daily_sales AS
SELECT 
    DATE(order_date) as sale_date,
    COUNT(*) as total_orders,
    SUM(total) as total_revenue,
    AVG(total) as average_order_value
FROM orders 
WHERE status NOT IN ('cancelled') 
GROUP BY DATE(order_date);

CREATE VIEW popular_products AS
SELECT 
    p.name,
    p.category,
    COUNT(oi.product_id) as times_ordered,
    SUM(oi.quantity) as total_quantity_sold,
    SUM(oi.subtotal) as total_revenue
FROM products p
JOIN order_items oi ON p.id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status NOT IN ('cancelled')
GROUP BY p.id, p.name, p.category
ORDER BY times_ordered DESC;

-- Stored procedures for common operations
DELIMITER //

CREATE PROCEDURE UpdateProductStock(
    IN product_id INT,
    IN quantity_change INT,
    IN action_type VARCHAR(20),
    IN reason_text VARCHAR(200)
)
BEGIN
    DECLARE current_stock INT;
    DECLARE new_stock INT;
    
    -- Get current stock
    SELECT stock INTO current_stock FROM products WHERE id = product_id;
    
    -- Calculate new stock
    SET new_stock = current_stock + quantity_change;
    
    -- Update product stock
    UPDATE products SET stock = new_stock WHERE id = product_id;
    
    -- Log the inventory change
    INSERT INTO inventory_logs (product_id, action, quantity_change, previous_stock, new_stock, reason)
    VALUES (product_id, action_type, quantity_change, current_stock, new_stock, reason_text);
END //

DELIMITER ;

-- Sample data insertion complete
SELECT 'Database schema created successfully!' as message;
