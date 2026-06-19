from db import get_db_connection

conn = get_db_connection()

conn.execute('''
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    shop_type TEXT NOT NULL,
    password TEXT NOT NULL          
)
''')

conn.commit()
conn.close()

print("Users table created successfully.")