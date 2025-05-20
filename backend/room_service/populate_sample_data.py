# Script to populate sample data for room_service (SQLAlchemy schema compatible)
import sqlite3
from datetime import datetime

# Use the correct path so both the app and script use the same DB
conn = sqlite3.connect('backend/room_service/room_service.db')
c = conn.cursor()

# Create tables if not exist (minimal for sample data)
c.execute('''CREATE TABLE IF NOT EXISTS properties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    location TEXT
)''')
c.execute('''CREATE TABLE IF NOT EXISTS room_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER,
    name TEXT,
    base_rate REAL
)''')
c.execute('''CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER,
    number TEXT,
    type_id INTEGER,
    status TEXT,
    floor TEXT,
    amenities TEXT,
    created_at TEXT,
    updated_at TEXT
)''')

# Insert sample properties
c.execute("INSERT OR IGNORE INTO properties (id, name, location) VALUES (1, 'Hotel Alpha', 'Downtown')")
c.execute("INSERT OR IGNORE INTO properties (id, name, location) VALUES (2, 'Hotel Beta', 'Airport')")

# Insert sample room types
c.execute("INSERT OR IGNORE INTO room_types (id, property_id, name, base_rate) VALUES (1, 1, 'Single', 100.0)")
c.execute("INSERT OR IGNORE INTO room_types (id, property_id, name, base_rate) VALUES (2, 1, 'Double', 150.0)")
c.execute("INSERT OR IGNORE INTO room_types (id, property_id, name, base_rate) VALUES (3, 2, 'Suite', 250.0)")

# Insert sample rooms (status: AVAILABLE, OCCUPIED, CLEANING, MAINTENANCE)
now = datetime.now().isoformat(sep=' ', timespec='seconds')
data = [
    (1, '101', 1, 'AVAILABLE', '1', 'WiFi,TV', now, now),
    (1, '102', 2, 'OCCUPIED', '1', 'WiFi,TV', now, now),
    (1, '103', 2, 'MAINTENANCE', '1', 'WiFi,TV,MiniBar', now, now),
    (2, '201', 3, 'AVAILABLE', '2', 'WiFi,TV', now, now),
    (2, '202', 3, 'OCCUPIED', '2', 'WiFi,TV,Jacuzzi', now, now)
]
for property_id, number, type_id, status, floor, amenities, created_at, updated_at in data:
    c.execute(
        "INSERT INTO rooms (property_id, number, type_id, status, floor, amenities, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (property_id, number, type_id, status, floor, amenities, created_at, updated_at)
    )

conn.commit()
conn.close()
print('Sample properties, room types, and rooms inserted.')
