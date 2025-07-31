import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Bot Configuration
    BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
    
    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'your_password')
    DB_NAME = os.getenv('DB_NAME', 'grocery_store')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    
    # Store Configuration
    STORE_NAME = os.getenv('STORE_NAME', 'Fresh Groceries')
    STORE_ADDRESS = os.getenv('STORE_ADDRESS', '123 Main Street, City, State 12345')
    STORE_PHONE = os.getenv('STORE_PHONE', '+1 (555) 123-4567')
    STORE_EMAIL = os.getenv('STORE_EMAIL', 'info@freshgroceries.com')
    
    # Delivery Configuration
    DELIVERY_FEE = float(os.getenv('DELIVERY_FEE', 5.0))
    FREE_DELIVERY_MINIMUM = float(os.getenv('FREE_DELIVERY_MINIMUM', 50.0))
    DELIVERY_RADIUS_KM = float(os.getenv('DELIVERY_RADIUS_KM', 10.0))
    
    # Order Configuration
    MIN_ORDER_AMOUNT = float(os.getenv('MIN_ORDER_AMOUNT', 10.0))
    MAX_CART_ITEMS = int(os.getenv('MAX_CART_ITEMS', 50))
    
    # Store Hours
    STORE_OPEN_TIME = os.getenv('STORE_OPEN_TIME', '08:00')
    STORE_CLOSE_TIME = os.getenv('STORE_CLOSE_TIME', '22:00')
    DELIVERY_OPEN_TIME = os.getenv('DELIVERY_OPEN_TIME', '10:00')
    DELIVERY_CLOSE_TIME = os.getenv('DELIVERY_CLOSE_TIME', '21:00')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'grocery_bot.log')
    
    @classmethod
    def get_db_config(cls):
        return {
            'host': cls.DB_HOST,
            'user': cls.DB_USER,
            'password': cls.DB_PASSWORD,
            'database': cls.DB_NAME,
            'port': cls.DB_PORT,
            'autocommit': True,
            'charset': 'utf8mb4'
        }
