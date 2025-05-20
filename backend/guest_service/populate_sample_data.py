# Script to populate sample data for guest_service
import sqlite3

conn = sqlite3.connect('guest_service.db')
c = conn.cursor()

# Create table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS guests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    address TEXT
)''')

data = [
    (1, 'Alice', 'Smith', 'alice@example.com', '123-456-7890', '123 Main St'),
    (1, 'Bob', 'Johnson', 'bob@example.com', '234-567-8901', '456 Oak Ave'),
    (2, 'Charlie', 'Lee', 'charlie@example.com', '345-678-9012', '789 Pine Rd')
]
for property_id, first_name, last_name, email, phone, address in data:
    c.execute("INSERT INTO guests (property_id, first_name, last_name, email, phone, address) VALUES (?, ?, ?, ?, ?, ?)",
              (property_id, first_name, last_name, email, phone, address))

conn.commit()
conn.close()
print('Sample guests inserted.')
