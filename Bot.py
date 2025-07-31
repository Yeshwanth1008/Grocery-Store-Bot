import telebot
import requests
import uuid
from datetime import datetime
import json
import logging
import os
from config import Config
from database import get_db

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize bot
bot = telebot.TeleBot(Config.BOT_TOKEN)

# Initialize database
db = get_db()

# User session management
user_sessions = {}

class UserSession:
    def __init__(self, user_id):
        self.user_id = user_id
        self.cart = {}
        self.current_state = "main_menu"
        self.delivery_type = None
        self.customer_info = {}
        self.order_id = None

def get_user_session(user_id):
    if user_id not in user_sessions:
        user_sessions[user_id] = UserSession(user_id)
    return user_sessions[user_id]

# Keyboard markups
def create_main_menu_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("🛒 Browse Products", "🛍️ View Cart")
    markup.add("📦 Order Type", "📋 My Orders")
    markup.add("ℹ️ Help", "📞 Contact")
    return markup

def create_order_type_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("🚚 Home Delivery", "🏪 Take Away")
    markup.add("🔙 Back to Main Menu")
    return markup

def create_category_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    categories = db.get_all_categories()
    if categories:
        for category in categories:
            markup.add(f"📂 {category[0]}")
    markup.add("🔍 Search Products", "⭐ Popular Items")
    markup.add("🔙 Back to Main Menu")
    return markup

def create_cart_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("➕ Add More Items", "➖ Remove Items")
    markup.add("🛒 Checkout", "🗑️ Clear Cart")
    markup.add("🔙 Back to Main Menu")
    return markup

# Bot command handlers
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    session = get_user_session(user_id)
    
    # Register user in database
    db.register_customer(
        user_id, 
        message.from_user.first_name, 
        message.from_user.last_name, 
        message.from_user.username
    )
    
    welcome_text = f"""
🏪 Welcome to {Config.STORE_NAME}, {message.from_user.first_name}!

I can help you:
• 🛒 Browse and order products
• 🛍️ Manage your shopping cart
• 📦 Choose delivery or take-away
• 📋 Track your orders
• 📞 Get customer support

Let's get started! 🛒
    """
    
    bot.reply_to(message, welcome_text, reply_markup=create_main_menu_keyboard())

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
🆘 **How to use this bot:**

🛒 **Browse Products** - View available items by category
🛍️ **View Cart** - See items in your cart and manage them
📦 **Order Type** - Choose between home delivery or take-away
📋 **My Orders** - View your order history
ℹ️ **Help** - Show this help message
📞 **Contact** - Get store contact information

**Commands:**
/start - Start the bot
/help - Show help
/cart - Quick access to cart
/orders - View your orders
    """
    bot.reply_to(message, help_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "🛒 Browse Products")
def browse_products(message):
    session = get_user_session(message.from_user.id)
    session.current_state = "browsing"
    
    bot.reply_to(message, "Please select a category:", reply_markup=create_category_keyboard())

@bot.message_handler(func=lambda message: message.text.startswith("📂 "))
def show_category_products(message):
    category = message.text.replace("📂 ", "")
    products = db.get_products_by_category(category)
    
    if products:
        response = f"🏷️ **{category}** Products:\n\n"
        markup = telebot.types.InlineKeyboardMarkup()
        
        for product in products:
            product_id, name, price, stock, description, image_url = product
            response += f"**{name}**\n"
            response += f"💰 Price: ${price:.2f}\n"
            response += f"📦 Stock: {stock} units\n"
            if description:
                response += f"📝 {description}\n"
            response += "\n"
            
            # Add inline keyboard for adding to cart
            markup.add(telebot.types.InlineKeyboardButton(
                f"🛒 Add {name}", 
                callback_data=f"add_to_cart_{product_id}"
            ))
        
        bot.reply_to(message, response, reply_markup=markup, parse_mode='Markdown')
    else:
        bot.reply_to(message, f"Sorry, no products available in {category} category.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("add_to_cart_"))
def add_to_cart_callback(call):
    product_id = int(call.data.split("_")[-1])
    session = get_user_session(call.from_user.id)
    
    # Get product details
    product = db.get_product_by_id(product_id)
    
    if product:
        product_id, name, category, price, stock, description = product
        
        if product_id in session.cart:
            if session.cart[product_id]['quantity'] < stock:
                session.cart[product_id]['quantity'] += 1
                bot.answer_callback_query(call.id, f"✅ Added another {name} to cart!")
            else:
                bot.answer_callback_query(call.id, f"❌ Sorry, only {stock} {name} available!")
        else:
            if len(session.cart) >= Config.MAX_CART_ITEMS:
                bot.answer_callback_query(call.id, f"❌ Cart is full! Maximum {Config.MAX_CART_ITEMS} items allowed.")
                return
                
            session.cart[product_id] = {
                'name': name,
                'price': price,
                'quantity': 1
            }
            bot.answer_callback_query(call.id, f"✅ Added {name} to cart!")
    else:
        bot.answer_callback_query(call.id, "❌ Product not found!")

@bot.message_handler(func=lambda message: message.text == "🛍️ View Cart")
def view_cart(message):
    session = get_user_session(message.from_user.id)
    
    if not session.cart:
        bot.reply_to(message, "Your cart is empty! 🛒\nUse '🛒 Browse Products' to add items.")
        return
    
    cart_text = "🛍️ **Your Cart:**\n\n"
    total = 0
    
    for product_id, item in session.cart.items():
        subtotal = item['price'] * item['quantity']
        total += subtotal
        cart_text += f"**{item['name']}**\n"
        cart_text += f"💰 ${item['price']:.2f} x {item['quantity']} = ${subtotal:.2f}\n\n"
    
    cart_text += f"**Total: ${total:.2f}**"
    
    bot.reply_to(message, cart_text, reply_markup=create_cart_keyboard(), parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "📦 Order Type")
def choose_order_type(message):
    session = get_user_session(message.from_user.id)
    session.current_state = "choosing_order_type"
    
    bot.reply_to(message, "How would you like to receive your order?", 
                reply_markup=create_order_type_keyboard())

@bot.message_handler(func=lambda message: message.text in ["🚚 Home Delivery", "🏪 Take Away"])
def set_order_type(message):
    session = get_user_session(message.from_user.id)
    
    if message.text == "🚚 Home Delivery":
        session.delivery_type = "delivery"
        bot.reply_to(message, "Great! You've selected Home Delivery 🚚\n\nFor delivery, we'll need your address during checkout.")
    else:
        session.delivery_type = "takeaway"
        bot.reply_to(message, "Perfect! You've selected Take Away 🏪\n\nYou can pick up your order from our store.")
    
    bot.send_message(message.chat.id, "Order type set! You can now browse products and checkout.", 
                    reply_markup=create_main_menu_keyboard())

@bot.message_handler(func=lambda message: message.text == "🛒 Checkout")
def checkout(message):
    session = get_user_session(message.from_user.id)
    
    if not session.cart:
        bot.reply_to(message, "Your cart is empty! Add some products first.")
        return
    
    if not session.delivery_type:
        bot.reply_to(message, "Please select order type first (📦 Order Type)")
        return
    
    session.current_state = "checkout"
    
    if session.delivery_type == "delivery":
        bot.reply_to(message, "Please provide your delivery address:")
    else:
        bot.reply_to(message, "Please provide your phone number for pickup notification:")

@bot.message_handler(func=lambda message: get_user_session(message.from_user.id).current_state == "checkout")
def process_checkout(message):
    session = get_user_session(message.from_user.id)
    
    if session.delivery_type == "delivery":
        session.customer_info['address'] = message.text
        bot.reply_to(message, "Address saved! Now please provide your phone number:")
        session.current_state = "phone_input"
    else:
        session.customer_info['phone'] = message.text
        create_order(message)

@bot.message_handler(func=lambda message: get_user_session(message.from_user.id).current_state == "phone_input")
def get_phone_number(message):
    session = get_user_session(message.from_user.id)
    session.customer_info['phone'] = message.text
    create_order(message)

def create_order(message):
    session = get_user_session(message.from_user.id)
    order_id = str(uuid.uuid4())[:8].upper()
    
    # Calculate total
    total = sum(item['price'] * item['quantity'] for item in session.cart.values())
    
    # Check minimum order amount
    if total < Config.MIN_ORDER_AMOUNT:
        bot.reply_to(message, f"❌ Minimum order amount is ${Config.MIN_ORDER_AMOUNT:.2f}. Your cart total is ${total:.2f}")
        return
    
    # Add delivery fee if applicable
    delivery_fee = 0.0
    if session.delivery_type == "delivery":
        if total < Config.FREE_DELIVERY_MINIMUM:
            delivery_fee = Config.DELIVERY_FEE
    
    final_total = total + delivery_fee
    
    # Create order in database
    order_data = (
        order_id,
        message.from_user.id,
        json.dumps(session.cart),
        total,
        delivery_fee,
        final_total,
        session.delivery_type,
        session.customer_info.get('address', ''),
        session.customer_info.get('phone', ''),
        'pending',
        datetime.now()
    )
    
    # Insert order
    if db.create_order(order_data):
        # Add individual order items
        db.add_order_items(order_id, session.cart)
        
        # Update product stock
        for product_id, item in session.cart.items():
            db.update_product_stock(product_id, item['quantity'])
        
        # Generate bill
        bill_text = generate_bill(session, order_id, total, delivery_fee, final_total)
        
        bot.reply_to(message, bill_text, parse_mode='Markdown', reply_markup=create_main_menu_keyboard())
        
        # Clear cart and reset session
        session.cart = {}
        session.current_state = "main_menu"
        session.customer_info = {}
        
        logger.info(f"Order {order_id} created successfully for user {message.from_user.id}")
    else:
        bot.reply_to(message, "❌ Sorry, there was an error processing your order. Please try again.")

def generate_bill(session, order_id, subtotal, delivery_fee, total):
    bill = f"""
🧾 **ORDER CONFIRMATION**

📋 Order ID: `{order_id}`
📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Items Ordered:**
"""
    
    for item in session.cart.values():
        item_total = item['price'] * item['quantity']
        bill += f"• {item['name']} x {item['quantity']} = ${item_total:.2f}\n"
    
    bill += f"""
💰 **Subtotal:** ${subtotal:.2f}
🚚 **Delivery Fee:** ${delivery_fee:.2f}
**Total Amount:** ${total:.2f}

📦 **Order Type:** {session.delivery_type.title()}
"""
    
    if session.delivery_type == "delivery":
        bill += f"📍 **Delivery Address:** {session.customer_info.get('address', 'N/A')}\n"
    
    bill += f"📞 **Phone:** {session.customer_info.get('phone', 'N/A')}\n"
    bill += "\n✅ Your order has been confirmed!\n"
    
    if session.delivery_type == "delivery":
        bill += "🚚 Expected delivery time: 30-45 minutes"
    else:
        bill += "🏪 You can pick up your order in 15-20 minutes"
    
    return bill

@bot.message_handler(func=lambda message: message.text == "📋 My Orders")
def my_orders(message):
    orders = db.get_customer_orders(message.from_user.id, 10)
    
    if orders:
        response = "📋 **Your Recent Orders:**\n\n"
        for order in orders:
            order_id, total, status, order_date, order_type, delivery_address = order
            response += f"🔢 **Order #{order_id}**\n"
            response += f"💰 Total: ${total:.2f}\n"
            response += f"📦 Type: {order_type.title()}\n"
            response += f"📅 Date: {order_date.strftime('%Y-%m-%d %H:%M')}\n"
            response += f"📊 Status: {status.title()}\n"
            if order_type == 'delivery' and delivery_address:
                response += f"📍 Address: {delivery_address[:50]}...\n"
            response += "\n"
        
        bot.reply_to(message, response, parse_mode='Markdown')
    else:
        bot.reply_to(message, "You haven't placed any orders yet. Start shopping! 🛒")

@bot.message_handler(func=lambda message: message.text == "� Search Products")
def search_products_prompt(message):
    session = get_user_session(message.from_user.id)
    session.current_state = "searching"
    bot.reply_to(message, "🔍 What product are you looking for? Type the product name:")

@bot.message_handler(func=lambda message: get_user_session(message.from_user.id).current_state == "searching")
def search_products(message):
    session = get_user_session(message.from_user.id)
    search_term = message.text.strip()
    
    if len(search_term) < 2:
        bot.reply_to(message, "Please enter at least 2 characters to search.")
        return
    
    products = db.search_products(search_term)
    session.current_state = "main_menu"
    
    if products:
        response = f"🔍 **Search Results for '{search_term}':**\n\n"
        markup = telebot.types.InlineKeyboardMarkup()
        
        for product in products:
            product_id, name, category, price, stock, description = product
            response += f"**{name}**\n"
            response += f"📂 Category: {category}\n"
            response += f"💰 Price: ${price:.2f}\n"
            response += f"📦 Stock: {stock} units\n"
            if description:
                response += f"📝 {description}\n"
            response += "\n"
            
            markup.add(telebot.types.InlineKeyboardButton(
                f"🛒 Add {name}", 
                callback_data=f"add_to_cart_{product_id}"
            ))
        
        bot.reply_to(message, response, reply_markup=markup, parse_mode='Markdown')
    else:
        bot.reply_to(message, f"❌ No products found for '{search_term}'. Try different keywords!")

@bot.message_handler(func=lambda message: message.text == "⭐ Popular Items")
def show_popular_products(message):
    products = db.get_popular_products(10)
    
    if products:
        response = "⭐ **Most Popular Products:**\n\n"
        markup = telebot.types.InlineKeyboardMarkup()
        
        for i, product in enumerate(products, 1):
            product_id, name, category, price, stock, order_count, total_sold = product
            response += f"**{i}. {name}**\n"
            response += f"📂 {category} | 💰 ${price:.2f}\n"
            response += f"📦 {stock} in stock | 🔥 Ordered {order_count} times\n\n"
            
            markup.add(telebot.types.InlineKeyboardButton(
                f"🛒 Add {name}", 
                callback_data=f"add_to_cart_{product_id}"
            ))
        
        bot.reply_to(message, response, reply_markup=markup, parse_mode='Markdown')
    else:
        bot.reply_to(message, "No popular products data available yet.")

@bot.message_handler(func=lambda message: message.text == "📞 Contact")
def contact_info(message):
    contact_text = f"""
📞 **Contact Information**

🏪 **Store Name:** {Config.STORE_NAME}
📍 **Address:** {Config.STORE_ADDRESS}
📞 **Phone:** {Config.STORE_PHONE}
📧 **Email:** {Config.STORE_EMAIL}

🕒 **Store Hours:**
Monday - Friday: {Config.STORE_OPEN_TIME} - {Config.STORE_CLOSE_TIME}
Saturday - Sunday: {Config.STORE_OPEN_TIME} - {Config.STORE_CLOSE_TIME}

🚚 **Delivery Hours:**
Monday - Sunday: {Config.DELIVERY_OPEN_TIME} - {Config.DELIVERY_CLOSE_TIME}

💰 **Delivery Info:**
• Delivery fee: ${Config.DELIVERY_FEE:.2f}
• Free delivery on orders over ${Config.FREE_DELIVERY_MINIMUM:.2f}
• Delivery radius: {Config.DELIVERY_RADIUS_KM} km
    """
    bot.reply_to(message, contact_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "🔙 Back to Main Menu")
def back_to_main_menu(message):
    session = get_user_session(message.from_user.id)
    session.current_state = "main_menu"
    bot.reply_to(message, "Back to main menu!", reply_markup=create_main_menu_keyboard())

@bot.message_handler(func=lambda message: message.text == "🗑️ Clear Cart")
def clear_cart(message):
    session = get_user_session(message.from_user.id)
    session.cart = {}
    bot.reply_to(message, "Cart cleared! 🗑️", reply_markup=create_main_menu_keyboard())

# Error handler
@bot.message_handler(func=lambda message: True)
def handle_unknown_message(message):
    bot.reply_to(message, "Sorry, I didn't understand that. Please use the menu buttons below.", 
                reply_markup=create_main_menu_keyboard())

if __name__ == "__main__":
    logger.info("Starting Grocery Store Bot...")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        db.close()
