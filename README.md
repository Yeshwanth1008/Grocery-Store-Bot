# Grocery Store Telegram Bot

An interactive Telegram chatbot for a grocery store built with Python, featuring inventory management, cart functionality, order processing, and both home delivery and take-away options.

## Features

🛒 **Shopping Features:**
- Browse products by category
- Search products by name
- View popular/trending items
- Add/remove items from cart
- Real-time stock checking

📦 **Order Management:**
- Home delivery and take-away options
- Dynamic delivery fee calculation
- Order history tracking
- Real-time order status updates
- Billing information generation

🗄️ **Database Integration:**
- Complete MySQL database schema
- Customer information management
- Inventory tracking
- Sales analytics
- Order history

🔧 **Advanced Features:**
- Session management for multiple users
- Error handling and logging
- Configurable settings via environment variables
- Admin panel capabilities (extendable)

## Prerequisites

- Python 3.7 or higher
- MySQL 5.7 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Grocery-Store-Bot-main
   ```

2. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up MySQL database:**
   - Create a MySQL database named `grocery_store`
   - Import the database schema:
   ```bash
   mysql -u your_username -p grocery_store < database_schema.sql
   ```

4. **Configure environment variables:**
   - Copy `.env.template` to `.env`
   - Update the configuration values:
   ```bash
   cp .env.template .env
   ```
   - Edit `.env` file with your actual values:
   ```env
   BOT_TOKEN=your_telegram_bot_token_here
   DB_USER=your_mysql_username
   DB_PASSWORD=your_mysql_password
   # ... other settings
   ```

5. **Create Telegram Bot:**
   - Message [@BotFather](https://t.me/botfather) on Telegram
   - Use `/newbot` command to create a new bot
   - Get your bot token and add it to `.env` file

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BOT_TOKEN` | Telegram Bot Token | Required |
| `DB_HOST` | MySQL host | localhost |
| `DB_USER` | MySQL username | root |
| `DB_PASSWORD` | MySQL password | Required |
| `DB_NAME` | Database name | grocery_store |
| `STORE_NAME` | Your store name | Fresh Groceries |
| `DELIVERY_FEE` | Delivery charge | 5.0 |
| `FREE_DELIVERY_MINIMUM` | Free delivery threshold | 50.0 |
| `MIN_ORDER_AMOUNT` | Minimum order amount | 10.0 |

### Database Configuration

The bot uses MySQL with the following main tables:
- `customers` - Customer information
- `products` - Product catalog
- `orders` - Order management
- `order_items` - Order line items
- `categories` - Product categories
- `sales` - Sales analytics

## Usage

1. **Start the bot:**
   ```bash
   python Bot.py
   ```

2. **Interact with your bot on Telegram:**
   - Start conversation with `/start`
   - Browse products by category
   - Add items to cart
   - Select delivery or pickup
   - Complete checkout process

## Bot Commands

- `/start` - Initialize bot and show main menu
- `/help` - Display help information
- `/cart` - Quick access to shopping cart
- `/orders` - View order history

## Main Features Flow

### Shopping Flow:
1. **Browse Products** → Select Category → View Products → Add to Cart
2. **Search Products** → Enter Keywords → View Results → Add to Cart
3. **Popular Items** → View Trending → Add to Cart

### Checkout Flow:
1. **View Cart** → **Checkout** → **Select Order Type**
2. **Enter Details** (Address for delivery / Phone for pickup)
3. **Confirm Order** → **Receive Bill** → **Track Order**

## Database Schema Highlights

### Products Table
```sql
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock INT DEFAULT 0,
    description TEXT,
    image_url VARCHAR(500)
);
```

### Orders Table
```sql
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id VARCHAR(20) UNIQUE NOT NULL,
    customer_id BIGINT NOT NULL,
    total DECIMAL(10, 2) NOT NULL,
    order_type ENUM('delivery', 'takeaway') NOT NULL,
    status ENUM('pending', 'confirmed', 'preparing', 'ready', 'delivered', 'cancelled')
);
```

## File Structure

```
Grocery-Store-Bot-main/
├── Bot.py                 # Main bot application
├── config.py             # Configuration management
├── database.py           # Database utility functions
├── database_schema.sql   # MySQL database schema
├── requirements.txt      # Python dependencies
├── .env.template        # Environment variables template
└── README.md           # This file
```

## Extending the Bot

### Adding New Product Categories:
1. Insert into `categories` table
2. Add products with the new category
3. Bot will automatically show the new category

### Adding New Features:
1. Create new message handlers in `Bot.py`
2. Add corresponding database methods in `database.py`
3. Update keyboard markups as needed

### Admin Features (Extendable):
- View sales reports
- Manage inventory
- Update product information
- Manage customer orders

## Logging

The bot includes comprehensive logging:
- All operations are logged with timestamps
- Error tracking and debugging information
- Configurable log levels via environment variables
- Logs stored in `grocery_bot.log` file

## Error Handling

- Database connection retry logic
- Input validation for all user inputs
- Graceful error messages for users
- Comprehensive exception handling

## Security Considerations

- Environment variables for sensitive data
- SQL injection prevention with parameterized queries
- Input sanitization
- User session management

## Troubleshooting

### Common Issues:

1. **Database Connection Error:**
   - Check MySQL service is running
   - Verify database credentials in `.env`
   - Ensure database exists and schema is imported

2. **Bot Not Responding:**
   - Verify bot token is correct
   - Check internet connection
   - Review logs for error messages

3. **Products Not Showing:**
   - Ensure products have stock > 0
   - Check database data insertion
   - Verify category names match

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## License

This project is open source and available under the [IITM License](LICENSE).

## Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the logs for error details

---

**Note:** Remember to keep your `.env` file secure and never commit it to version control. Always use environment variables for sensitive configuration data.
