#!/usr/bin/env python3
"""
Admin utility for Grocery Store Bot
Provides basic administrative functions for managing the store
"""

import sys
import json
from datetime import datetime, timedelta
from database import get_db
from config import Config

class AdminUtility:
    def __init__(self):
        self.db = get_db()
        
    def show_menu(self):
        """Display admin menu"""
        print("\n" + "="*50)
        print("🏪 GROCERY STORE BOT - ADMIN PANEL")
        print("="*50)
        print("1. 📊 View Daily Sales Report")
        print("2. 📦 Check Low Stock Products") 
        print("3. 🛒 View Recent Orders")
        print("4. 👥 Customer Statistics")
        print("5. 📈 Popular Products Report")
        print("6. ➕ Add New Product")
        print("7. 🔄 Update Product Stock")
        print("8. 📋 Order Management")
        print("9. 🗑️  Delete Product")
        print("0. ❌ Exit")
        print("="*50)
        
    def daily_sales_report(self):
        """Show daily sales report"""
        print("\n📊 DAILY SALES REPORT")
        print("-" * 30)
        
        # Get today's sales
        today_sales = self.db.get_daily_sales_report()
        if today_sales and today_sales[0]:
            total_orders, total_revenue, avg_order = today_sales[0]
            print(f"Today ({datetime.now().strftime('%Y-%m-%d')}):")
            print(f"  📋 Total Orders: {total_orders}")
            print(f"  💰 Total Revenue: ${total_revenue:.2f}")
            print(f"  📊 Average Order: ${avg_order:.2f}")
        else:
            print("No sales data for today")
            
        # Get weekly summary
        week_ago = datetime.now() - timedelta(days=7)
        weekly_orders = self.db.execute_query("""
            SELECT COUNT(*) as orders, COALESCE(SUM(total), 0) as revenue
            FROM orders 
            WHERE order_date >= %s AND status NOT IN ('cancelled')
        """, (week_ago,))
        
        if weekly_orders and weekly_orders[0]:
            orders, revenue = weekly_orders[0]
            print(f"\nWeek Summary (Last 7 days):")
            print(f"  📋 Total Orders: {orders}")
            print(f"  💰 Total Revenue: ${revenue:.2f}")
            
    def check_low_stock(self):
        """Check products with low stock"""
        print("\n📦 LOW STOCK ALERT")
        print("-" * 30)
        
        threshold = input("Enter stock threshold (default 10): ").strip()
        threshold = int(threshold) if threshold.isdigit() else 10
        
        low_stock = self.db.get_low_stock_products(threshold)
        
        if low_stock:
            print(f"Products with stock <= {threshold}:")
            for product in low_stock:
                product_id, name, category, stock = product
                status = "🔴 OUT OF STOCK" if stock == 0 else f"🟡 LOW ({stock} left)"
                print(f"  {product_id}: {name} ({category}) - {status}")
        else:
            print(f"✅ All products have sufficient stock (>{threshold})")
            
    def recent_orders(self):
        """Show recent orders"""
        print("\n🛒 RECENT ORDERS")
        print("-" * 30)
        
        limit = input("Number of orders to show (default 10): ").strip()
        limit = int(limit) if limit.isdigit() else 10
        
        orders = self.db.execute_query("""
            SELECT o.order_id, c.first_name, c.last_name, o.total, 
                   o.status, o.order_type, o.order_date
            FROM orders o
            JOIN customers c ON o.customer_id = c.telegram_id
            ORDER BY o.order_date DESC
            LIMIT %s
        """, (limit,))
        
        if orders:
            for order in orders:
                order_id, fname, lname, total, status, order_type, order_date = order
                customer_name = f"{fname} {lname}".strip() or "Unknown"
                print(f"  #{order_id} - {customer_name}")
                print(f"    💰 ${total:.2f} | 📦 {order_type} | 📊 {status}")
                print(f"    📅 {order_date.strftime('%Y-%m-%d %H:%M')}")
                print()
        else:
            print("No recent orders found")
            
    def customer_stats(self):
        """Show customer statistics"""
        print("\n👥 CUSTOMER STATISTICS")
        print("-" * 30)
        
        # Total customers
        total_customers = self.db.execute_query("SELECT COUNT(*) FROM customers")
        print(f"📊 Total Customers: {total_customers[0][0] if total_customers else 0}")
        
        # Active customers (ordered in last 30 days)
        month_ago = datetime.now() - timedelta(days=30)
        active_customers = self.db.execute_query("""
            SELECT COUNT(DISTINCT customer_id) FROM orders 
            WHERE order_date >= %s
        """, (month_ago,))
        print(f"🔥 Active Customers (30 days): {active_customers[0][0] if active_customers else 0}")
        
        # Top customers
        top_customers = self.db.execute_query("""
            SELECT c.first_name, c.last_name, COUNT(o.id) as order_count, 
                   SUM(o.total) as total_spent
            FROM customers c
            JOIN orders o ON c.telegram_id = o.customer_id
            WHERE o.status NOT IN ('cancelled')
            GROUP BY c.telegram_id
            ORDER BY total_spent DESC
            LIMIT 5
        """)
        
        if top_customers:
            print("\n🏆 Top Customers:")
            for i, customer in enumerate(top_customers, 1):
                fname, lname, orders, spent = customer
                name = f"{fname} {lname}".strip() or "Unknown"
                print(f"  {i}. {name} - {orders} orders, ${spent:.2f}")
                
    def popular_products_report(self):
        """Show popular products report"""
        print("\n📈 POPULAR PRODUCTS REPORT")
        print("-" * 30)
        
        products = self.db.get_popular_products(10)
        
        if products:
            print("Top 10 Most Ordered Products:")
            for i, product in enumerate(products, 1):
                product_id, name, category, price, stock, order_count, total_sold = product
                print(f"  {i}. {name} ({category})")
                print(f"     💰 ${price:.2f} | 📦 {stock} in stock")
                print(f"     🔥 {order_count} orders | 📊 {total_sold} units sold")
                print()
        else:
            print("No sales data available yet")
            
    def add_product(self):
        """Add a new product"""
        print("\n➕ ADD NEW PRODUCT")
        print("-" * 30)
        
        name = input("Product name: ").strip()
        if not name:
            print("❌ Product name is required")
            return
            
        category = input("Category: ").strip()
        if not category:
            print("❌ Category is required")
            return
            
        try:
            price = float(input("Price: $").strip())
            stock = int(input("Initial stock: ").strip())
        except ValueError:
            print("❌ Invalid price or stock value")
            return
            
        description = input("Description (optional): ").strip()
        
        # Insert product
        result = self.db.execute_query("""
            INSERT INTO products (name, category, price, stock, description)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, category, price, stock, description or None))
        
        if result:
            print(f"✅ Product '{name}' added successfully!")
        else:
            print("❌ Failed to add product")
            
    def update_stock(self):
        """Update product stock"""
        print("\n🔄 UPDATE PRODUCT STOCK")
        print("-" * 30)
        
        # Search for product
        search = input("Enter product name or ID: ").strip()
        if not search:
            return
            
        # Try to find product
        if search.isdigit():
            products = self.db.execute_query("""
                SELECT id, name, category, price, stock 
                FROM products WHERE id = %s
            """, (int(search),))
        else:
            products = self.db.execute_query("""
                SELECT id, name, category, price, stock 
                FROM products WHERE name LIKE %s
            """, (f"%{search}%",))
            
        if not products:
            print("❌ Product not found")
            return
            
        if len(products) > 1:
            print("Multiple products found:")
            for i, product in enumerate(products):
                product_id, name, category, price, stock = product
                print(f"  {i+1}. {name} ({category}) - Current stock: {stock}")
                
            try:
                choice = int(input("Select product (number): ")) - 1
                if 0 <= choice < len(products):
                    selected_product = products[choice]
                else:
                    print("❌ Invalid selection")
                    return
            except ValueError:
                print("❌ Invalid selection")
                return
        else:
            selected_product = products[0]
            
        product_id, name, category, price, current_stock = selected_product
        print(f"\nSelected: {name}")
        print(f"Current stock: {current_stock}")
        
        try:
            new_stock = int(input("New stock quantity: ").strip())
            if new_stock < 0:
                print("❌ Stock cannot be negative")
                return
        except ValueError:
            print("❌ Invalid stock value")
            return
            
        # Update stock
        result = self.db.execute_query("""
            UPDATE products SET stock = %s WHERE id = %s
        """, (new_stock, product_id))
        
        if result:
            print(f"✅ Stock updated! {name}: {current_stock} → {new_stock}")
            
            # Log the change
            change = new_stock - current_stock
            action = "restock" if change > 0 else "adjustment"
            self.db.execute_query("""
                INSERT INTO inventory_logs (product_id, action, quantity_change, 
                                         previous_stock, new_stock, reason)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (product_id, action, change, current_stock, new_stock, "Admin update"))
        else:
            print("❌ Failed to update stock")
            
    def order_management(self):
        """Manage orders"""
        print("\n📋 ORDER MANAGEMENT")
        print("-" * 30)
        
        order_id = input("Enter order ID: ").strip().upper()
        if not order_id:
            return
            
        order = self.db.get_order_details(order_id)
        if not order:
            print("❌ Order not found")
            return
            
        # Display order details
        (order_id, customer_id, items, subtotal, delivery_fee, total, 
         order_type, address, phone, status, order_date, fname, lname) = order
         
        customer_name = f"{fname} {lname}".strip() or "Unknown"
        
        print(f"\n📋 Order #{order_id}")
        print(f"👤 Customer: {customer_name}")
        print(f"📅 Date: {order_date.strftime('%Y-%m-%d %H:%M')}")
        print(f"📦 Type: {order_type.title()}")
        print(f"📊 Status: {status.title()}")
        print(f"💰 Total: ${total:.2f}")
        
        if order_type == 'delivery' and address:
            print(f"📍 Address: {address}")
        if phone:
            print(f"📞 Phone: {phone}")
            
        # Show items
        if items:
            cart_items = json.loads(items)
            print("\n🛒 Items:")
            for item in cart_items.values():
                print(f"  • {item['name']} x {item['quantity']} = ${item['price'] * item['quantity']:.2f}")
                
        # Status update options
        print(f"\nCurrent status: {status}")
        print("Available status updates:")
        statuses = ['pending', 'confirmed', 'preparing', 'ready', 'delivered', 'cancelled']
        for i, s in enumerate(statuses, 1):
            if s != status:
                print(f"  {i}. {s.title()}")
                
        try:
            choice = input("\nEnter new status number (or Enter to skip): ").strip()
            if choice.isdigit():
                choice = int(choice) - 1
                if 0 <= choice < len(statuses) and statuses[choice] != status:
                    new_status = statuses[choice]
                    if self.db.update_order_status(order_id, new_status):
                        print(f"✅ Order status updated to: {new_status.title()}")
                    else:
                        print("❌ Failed to update order status")
        except (ValueError, IndexError):
            print("❌ Invalid choice")
            
    def delete_product(self):
        """Delete a product"""
        print("\n🗑️ DELETE PRODUCT")
        print("-" * 30)
        print("⚠️  WARNING: This will permanently delete the product!")
        
        search = input("Enter product name or ID: ").strip()
        if not search:
            return
            
        # Find product
        if search.isdigit():
            products = self.db.execute_query("""
                SELECT id, name, category, stock FROM products WHERE id = %s
            """, (int(search),))
        else:
            products = self.db.execute_query("""
                SELECT id, name, category, stock FROM products WHERE name LIKE %s
            """, (f"%{search}%",))
            
        if not products:
            print("❌ Product not found")
            return
            
        if len(products) > 1:
            print("Multiple products found:")
            for i, product in enumerate(products):
                product_id, name, category, stock = product
                print(f"  {i+1}. {name} ({category}) - Stock: {stock}")
                
            try:
                choice = int(input("Select product to delete (number): ")) - 1
                if 0 <= choice < len(products):
                    selected_product = products[choice]
                else:
                    print("❌ Invalid selection")
                    return
            except ValueError:
                print("❌ Invalid selection")
                return
        else:
            selected_product = products[0]
            
        product_id, name, category, stock = selected_product
        
        print(f"\n⚠️  You are about to delete:")
        print(f"Product: {name} ({category})")
        print(f"Current stock: {stock}")
        
        confirm = input("\nType 'DELETE' to confirm: ").strip()
        if confirm == 'DELETE':
            result = self.db.execute_query("DELETE FROM products WHERE id = %s", (product_id,))
            if result:
                print(f"✅ Product '{name}' deleted successfully!")
            else:
                print("❌ Failed to delete product")
        else:
            print("❌ Deletion cancelled")
            
    def run(self):
        """Run the admin utility"""
        print("🏪 Grocery Store Bot Admin Utility")
        print("Connecting to database...")
        
        if not self.db.connection or not self.db.connection.is_connected():
            print("❌ Failed to connect to database. Check your configuration.")
            return
            
        print("✅ Connected to database successfully!")
        
        while True:
            try:
                self.show_menu()
                choice = input("\nSelect option (0-9): ").strip()
                
                if choice == '0':
                    print("👋 Goodbye!")
                    break
                elif choice == '1':
                    self.daily_sales_report()
                elif choice == '2':
                    self.check_low_stock()
                elif choice == '3':
                    self.recent_orders()
                elif choice == '4':
                    self.customer_stats()
                elif choice == '5':
                    self.popular_products_report()
                elif choice == '6':
                    self.add_product()
                elif choice == '7':
                    self.update_stock()
                elif choice == '8':
                    self.order_management()
                elif choice == '9':
                    self.delete_product()
                else:
                    print("❌ Invalid option. Please try again.")
                    
                input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                input("Press Enter to continue...")
                
        # Close database connection
        self.db.close()

if __name__ == "__main__":
    admin = AdminUtility()
    admin.run()
