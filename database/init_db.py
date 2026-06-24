from db import get_db_connection

conn = get_db_connection()

# USER TABLE
conn.execute('''
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    shop_type TEXT NOT NULL,
    password TEXT NOT NULL          
)
''')


# PRODUCT TABLE
conn.execute('''
CREATE TABLE IF NOT EXISTS products(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    gst_percentage REAL NOT NULL,
    stock INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')


# CUSTOMER TABLE
conn.execute('''
CREATE TABLE IF NOT EXISTS customers(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    customer_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')


# INVOICES TABLE
conn.execute('''
CREATE TABLE IF NOT EXISTS invoices(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    subtotal REAL NOT NULL,
    gst_amount REAL NOT NULL,
    grand_total REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')


# INVOICE ITEMS TABLE
conn.execute('''
CREATE TABLE IF NOT EXISTS invoice_items(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    gst_percentage REAL NOT NULL
)
''')


# BUSINESS SETTINGS TABLE
conn.execute('''
CREATE TABLE IF NOT EXISTS business_settings(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE,
    shop_name TEXT,
    address TEXT,
    phone TEXT,
    email TEXT,
    gst_number TEXT
)
''')


# PAYMENTS TABLE
conn.execute("""
CREATE TABLE IF NOT EXISTS payments(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    payment_method TEXT NOT NULL,
    paid_amount REAL NOT NULL,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")


conn.commit()
conn.close()

print("Table created successfully.")
