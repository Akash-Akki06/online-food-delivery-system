import os
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session

# Determine the absolute path to the project root directory
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# Configure Flask to use templates and static folders from the project root instead of backend/
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static')
)
app.secret_key = 'your_super_secret_key' # Required for session management

def init_db():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Ensure users table exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    address TEXT,
                    city VARCHAR(100) DEFAULT 'Pune'
                )
            """)

            # Ensure restaurants table exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS restaurants (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    category VARCHAR(100),
                    city VARCHAR(100),
                    image_url TEXT
                )
            """)
            
            # Ensure food_items table exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS food_items (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    restaurant_id INT,
                    name VARCHAR(255) NOT NULL,
                    price INT NOT NULL,
                    image TEXT
                )
            """)
            
            # Check if restaurants is empty, if so, populate dummy data
            cursor.execute("SELECT COUNT(*) FROM restaurants")
            count = cursor.fetchone()[0]
            if count == 0:
                dummy_data = [
                    ('Burger Hub', 'Fast Food', 'Pune', 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?q=80&w=600'),
                    ('Pizza Palace', 'Italian', 'Pune', 'https://images.unsplash.com/photo-1513104890138-7c749659a591?q=80&w=600'),
                    ('South Spice', 'South Indian', 'Pune', 'https://images.unsplash.com/photo-1610192244261-3f33de3f55e4?q=80&w=600'),
                    ('North Delight', 'North Indian', 'Pune', 'https://images.unsplash.com/photo-1585937421612-70a008356fbe?q=80&w=600'),
                    ('Hyderabadi Biryani House', 'Hyderabadi', 'Pune', 'https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?q=80&w=600')
                ]
                cursor.executemany("INSERT INTO restaurants (name, category, city, image_url) VALUES (%s, %s, %s, %s)", dummy_data)
                conn.commit()

            # Check if food_items is empty, if so, populate dummy dishes
            cursor.execute("SELECT COUNT(*) FROM food_items")
            food_count = cursor.fetchone()[0]
            if food_count == 0:
                food_dummy = [
                    (1, 'Cheese Burger', 120, 'https://upload.wikimedia.org/wikipedia/commons/4/4d/Cheeseburger.jpg'),
                    (1, 'Veg Burger', 90, 'https://images.unsplash.com/photo-1606755962773-d324e0a13086'),
                    (2, 'Margherita Pizza', 200, 'https://images.unsplash.com/photo-1604382354936-07c5d9983bd3'),
                    (2, 'Farmhouse Pizza', 250, 'https://images.unsplash.com/photo-1594007654729-407eedc4be65'),
                    (3, 'Masala Dosa', 80, 'https://images.unsplash.com/photo-1668236543090-82eba5ee5976'),
                    (3, 'Idli Sambar', 60, 'https://images.unsplash.com/photo-1630383249896-424e482df921'),
                    (4, 'Butter Chicken', 220, 'https://images.unsplash.com/photo-1603894584373-5ac82b2ae398'),
                    (4, 'Paneer Butter Masala', 180, 'https://images.unsplash.com/photo-1604908176997-125f25cc6f3d'),
                    (5, 'Chicken Biryani', 250, 'https://images.unsplash.com/photo-1631515243349-e0cb75fb8d3a'),
                    (5, 'Veg Biryani', 180, 'https://images.unsplash.com/photo-1633945274405-b6c8069047b0?auto=format&fit=crop&w=800&q=80D')
                ]
                cursor.executemany("INSERT INTO food_items (restaurant_id, name, price, image) VALUES (%s, %s, %s, %s)", food_dummy)
                conn.commit()
            
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            print(f"Error initializing DB: {err}")

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='food_delivery'
        )
        print("Database connected successfully")
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

# Test connection on startup
init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error_message = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db_connection()
        if conn:
            try:
                # Use dictionary cursor to easily retrieve city by column name
                cursor = conn.cursor(dictionary=True)
                query = "SELECT * FROM users WHERE email = %s AND password = %s"
                cursor.execute(query, (email, password))
                user = cursor.fetchone()
                
                cursor.close()
                conn.close()
                
                if user:
                    # Save user details in session
                    session['user_name'] = user.get('name', 'User')
                    session['user_city'] = user.get('city', 'Pune') # Default fallback
                    return redirect('/restaurants')
                else:
                    error_message = "Invalid email or password"
            except mysql.connector.Error as err:
                error_message = "Database error occurred."
                if conn.is_connected():
                    conn.close()
        else:
            error_message = "Database connection failed."

    return render_template('login.html', error_message=error_message)
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        address = request.form.get('address')

        # Extract city from address (last word)
        city = 'Pune'
        if address:
            parts = address.strip().split()
            if parts:
                city = parts[-1]

        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (name, email, password, address, city) VALUES (%s, %s, %s, %s, %s)",
                    (name, email, password, address, city)
                )
                conn.commit()
                print("User inserted successfully")
                cursor.close()
                conn.close()
            except mysql.connector.Error as err:
                print(f"Error inserting user: {err}")
                if conn.is_connected():
                    conn.close()

        return redirect('/login')

    return render_template('register.html')

@app.route('/restaurants')
def restaurants():
    if 'user_city' not in session:
        return redirect('/login')
        
    user_city = session['user_city']
    user_name = session.get('user_name', 'User')
    restaurants_list = []
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM restaurants WHERE city = %s", (user_city,))
            restaurants_list = cursor.fetchall()
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            print(f"Database error fetching restaurants: {err}")
            
    return render_template('restaurants.html', restaurants=restaurants_list, city=user_city, name=user_name)

@app.route('/menu/<int:restaurant_id>')
def menu(restaurant_id):
    if 'user_city' not in session:
        return redirect('/login')
        
    conn = get_db_connection()
    restaurant = None
    food_items = []
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM restaurants WHERE id = %s", (restaurant_id,))
            restaurant = cursor.fetchone()
            
            cursor.execute("SELECT * FROM food_items WHERE restaurant_id = %s", (restaurant_id,))
            food_items = cursor.fetchall()
            
            for item in food_items:
                print(f"DEBUG Image: {item.get('image')}")
            
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            print(f"Database error fetching menu: {err}")
            
    if not restaurant:
        return redirect('/restaurants')
        
    return render_template('menu.html', restaurant=restaurant, food_items=food_items, name=session.get('user_name', 'User'))

@app.route('/add_to_cart/<int:item_id>')
def add_to_cart(item_id):
    if 'user_city' not in session:
        return redirect('/login')

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM food_items WHERE id = %s", (item_id,))
            item = cursor.fetchone()
            cursor.close()
            conn.close()

            if item:
                if 'cart' not in session:
                    session['cart'] = []
                
                cart = session['cart']
                
                found = False
                for cart_item in cart:
                    if cart_item['item_id'] == item['id']:
                        cart_item['quantity'] += 1
                        found = True
                        break
                
                if not found:
                    cart.append({
                        'item_id': item['id'],
                        'name': item['name'],
                        'price': item['price'],
                        'quantity': 1
                    })
                
                session.modified = True
                print("Item added to cart")
                
                return redirect("/cart")
        except mysql.connector.Error as err:
            print(f"Database error fetching item: {err}")
            if conn.is_connected():
                conn.close()
                
    return redirect('/restaurants')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/cart')
def cart():
    if 'user_city' not in session:
        return redirect('/login')
    
    cart_items = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/remove_item/<int:item_id>')
def remove_item(item_id):
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item['item_id'] != item_id]
        session.modified = True
    return redirect('/cart')

@app.route('/place_order')
def place_order():
    if 'user_city' not in session:
        return redirect('/login')
        
    session.pop('cart', None)
    import random
    agent = random.choice(["Rahul", "Amit", "Suresh", "Vikram"])
    return render_template('order_success.html', agent=agent)

if __name__ == '__main__':
    app.run(debug=True)
    
