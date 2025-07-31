import mysql.connector
from mysql.connector import Error
import logging
import json
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(**Config.get_db_config())
            if self.connection.is_connected():
                logger.info("Successfully connected to MySQL database")
                return True
        except Error as e:
            logger.error(f"Error connecting to MySQL database: {e}")
            return False
    
    def reconnect(self):
        """Reconnect to database if connection is lost"""
        if self.connection:
            self.connection.close()
        return self.connect()
    
    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        try:
            if not self.connection.is_connected():
                self.reconnect()
            
            cursor = self.connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if query.strip().lower().startswith('select') or query.strip().lower().startswith('show'):
                result = cursor.fetchall()
                cursor.close()
                return result
            else:
                self.connection.commit()
                affected_rows = cursor.rowcount
                cursor.close()
                return affected_rows
                
        except Error as e:
            logger.error(f"Database query error: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in execute_query: {e}")
            return None
    
    def get_products_by_category(self, category):
        """Get all products in a specific category"""
        query = """
            SELECT id, name, price, stock, description, image_url 
            FROM products 
            WHERE category = %s AND stock > 0
            ORDER BY name
        """
        return self.execute_query(query, (category,))
    
    def get_product_by_id(self, product_id):
        """Get product details by ID"""
        query = "SELECT id, name, category, price, stock, description FROM products WHERE id = %s"
        result = self.execute_query(query, (product_id,))
        return result[0] if result else None
    
    def get_all_categories(self):
        """Get all product categories"""
        query = "SELECT DISTINCT category FROM products WHERE stock > 0 ORDER BY category"
        return self.execute_query(query)
    
    def register_customer(self, telegram_id, first_name, last_name, username):
        """Register a new customer or update existing one"""
        query = """
            INSERT INTO customers (telegram_id, first_name, last_name, username, registration_date)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            first_name = VALUES(first_name),
            last_name = VALUES(last_name),
            username = VALUES(username),
            last_active = CURRENT_TIMESTAMP
        """
        params = (telegram_id, first_name or '', last_name or '', username or '', datetime.now())
        return self.execute_query(query, params)
    
    def create_order(self, order_data):
        """Create a new order"""
        query = """
            INSERT INTO orders (order_id, customer_id, items, subtotal, delivery_fee, 
                              total, order_type, delivery_address, phone, status, order_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        return self.execute_query(query, order_data)
    
    def add_order_items(self, order_id, cart_items):
        """Add items to order_items table"""
        query = """
            INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        for product_id, item in cart_items.items():
            subtotal = item['price'] * item['quantity']
            params = (order_id, product_id, item['quantity'], item['price'], subtotal)
            self.execute_query(query, params)
    
    def update_product_stock(self, product_id, quantity_sold):
        """Update product stock after sale"""
        query = "UPDATE products SET stock = stock - %s WHERE id = %s AND stock >= %s"
        return self.execute_query(query, (quantity_sold, product_id, quantity_sold))
    
    def get_customer_orders(self, telegram_id, limit=10):
        """Get customer's order history"""
        query = """
            SELECT order_id, total, status, order_date, order_type, delivery_address
            FROM orders 
            WHERE customer_id = %s 
            ORDER BY order_date DESC 
            LIMIT %s
        """
        return self.execute_query(query, (telegram_id, limit))
    
    def get_order_details(self, order_id):
        """Get detailed order information"""
        query = """
            SELECT o.order_id, o.customer_id, o.items, o.subtotal, o.delivery_fee, 
                   o.total, o.order_type, o.delivery_address, o.phone, o.status, 
                   o.order_date, c.first_name, c.last_name
            FROM orders o
            JOIN customers c ON o.customer_id = c.telegram_id
            WHERE o.order_id = %s
        """
        result = self.execute_query(query, (order_id,))
        return result[0] if result else None
    
    def update_order_status(self, order_id, status):
        """Update order status"""
        query = "UPDATE orders SET status = %s WHERE order_id = %s"
        return self.execute_query(query, (status, order_id))
    
    def get_low_stock_products(self, threshold=10):
        """Get products with low stock"""
        query = "SELECT id, name, category, stock FROM products WHERE stock <= %s ORDER BY stock ASC"
        return self.execute_query(query, (threshold,))
    
    def get_daily_sales_report(self, date=None):
        """Get daily sales report"""
        if date is None:
            date = datetime.now().date()
        
        query = """
            SELECT COUNT(*) as total_orders, 
                   COALESCE(SUM(total), 0) as total_revenue,
                   COALESCE(AVG(total), 0) as average_order_value
            FROM orders 
            WHERE DATE(order_date) = %s AND status NOT IN ('cancelled')
        """
        return self.execute_query(query, (date,))
    
    def search_products(self, search_term):
        """Search products by name or description"""
        query = """
            SELECT id, name, category, price, stock, description
            FROM products 
            WHERE (name LIKE %s OR description LIKE %s) AND stock > 0
            ORDER BY name
        """
        search_pattern = f"%{search_term}%"
        return self.execute_query(query, (search_pattern, search_pattern))
    
    def get_popular_products(self, limit=10):
        """Get most popular products based on order frequency"""
        query = """
            SELECT p.id, p.name, p.category, p.price, p.stock,
                   COUNT(oi.product_id) as order_count,
                   SUM(oi.quantity) as total_sold
            FROM products p
            JOIN order_items oi ON p.id = oi.product_id
            JOIN orders o ON oi.order_id = o.order_id
            WHERE o.status NOT IN ('cancelled')
            GROUP BY p.id
            ORDER BY order_count DESC, total_sold DESC
            LIMIT %s
        """
        return self.execute_query(query, (limit,))
    
    def add_customer_address(self, telegram_id, address_data):
        """Add customer delivery address"""
        query = """
            INSERT INTO customer_addresses (customer_id, address_type, street_address, 
                                          city, state, postal_code, is_default)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        return self.execute_query(query, (telegram_id, *address_data))
    
    def get_customer_addresses(self, telegram_id):
        """Get customer's saved addresses"""
        query = """
            SELECT id, address_type, street_address, city, state, postal_code, is_default
            FROM customer_addresses 
            WHERE customer_id = %s
            ORDER BY is_default DESC, id ASC
        """
        return self.execute_query(query, (telegram_id,))
    
    def close(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("MySQL connection closed")

# Singleton instance
_db_instance = None

def get_db():
    """Get singleton database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager()
    return _db_instance
