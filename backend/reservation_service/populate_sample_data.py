# Script to populate sample data for reservation_service (SQLAlchemy schema compatible)
import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('backend/reservation_service/reservation_service.db')
c = conn.cursor()

# Insert required properties
to_property = [
    (1, 'Hotel Alpha', 'Downtown'),
    (2, 'Hotel Beta', 'Airport')
]
c.execute('CREATE TABLE IF NOT EXISTS properties (id INTEGER PRIMARY KEY, name TEXT, location TEXT)')
for id, name, location in to_property:
    c.execute('INSERT OR IGNORE INTO properties (id, name, location) VALUES (?, ?, ?)', (id, name, location))

# Insert required guests
to_guest = [
    (1, 'Alice', 'Smith', 'alice@example.com', '123-456-7890', '123 Main St'),
    (2, 'Bob', 'Johnson', 'bob@example.com', '234-567-8901', '456 Oak Ave'),
    (3, 'Charlie', 'Lee', 'charlie@example.com', '345-678-9012', '789 Pine Rd')
]
c.execute('CREATE TABLE IF NOT EXISTS guests (id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, email TEXT, phone TEXT, address TEXT)')
for id, first_name, last_name, email, phone, address in to_guest:
    c.execute('INSERT OR IGNORE INTO guests (id, first_name, last_name, email, phone, address) VALUES (?, ?, ?, ?, ?, ?)', (id, first_name, last_name, email, phone, address))

# Insert required rooms
to_room = [
    (1, 1, '101', 1, 'AVAILABLE', '1', 'WiFi,TV'),
    (2, 1, '102', 2, 'OCCUPIED', '1', 'WiFi,TV'),
    (3, 2, '201', 3, 'AVAILABLE', '2', 'WiFi,TV'),
    (4, 2, '202', 3, 'OCCUPIED', '2', 'WiFi,TV,Jacuzzi')
]
c.execute('CREATE TABLE IF NOT EXISTS rooms (id INTEGER PRIMARY KEY, property_id INTEGER, number TEXT, type_id INTEGER, status TEXT, floor TEXT, amenities TEXT)')
for id, property_id, number, type_id, status, floor, amenities in to_room:
    c.execute('INSERT OR IGNORE INTO rooms (id, property_id, number, type_id, status, floor, amenities) VALUES (?, ?, ?, ?, ?, ?, ?)', (id, property_id, number, type_id, status, floor, amenities))

# Create table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER,
    room_id INTEGER,
    guest_id INTEGER,
    check_in TEXT,
    check_out TEXT,
    status TEXT,
    price REAL,
    payment_status TEXT,
    created_at TEXT,
    updated_at TEXT
)''')

# Insert sample reservations (property_id, guest_id, room_id, check_in, check_out, status, price, payment_status, created_at, updated_at)
now = datetime.now()
data = [
    (1, 1, 1, now.isoformat(sep=' ', timespec='seconds'), (now + timedelta(days=2)).isoformat(sep=' ', timespec='seconds'), 'BOOKED', 200.0, 'PAID', now.isoformat(sep=' ', timespec='seconds'), now.isoformat(sep=' ', timespec='seconds')),
    (1, 2, 2, (now + timedelta(days=1)).isoformat(sep=' ', timespec='seconds'), (now + timedelta(days=3)).isoformat(sep=' ', timespec='seconds'), 'CHECKED_IN', 300.0, 'PAID', now.isoformat(sep=' ', timespec='seconds'), now.isoformat(sep=' ', timespec='seconds')),
    (2, 3, 3, now.isoformat(sep=' ', timespec='seconds'), (now + timedelta(days=1)).isoformat(sep=' ', timespec='seconds'), 'CANCELED', 150.0, 'REFUNDED', now.isoformat(sep=' ', timespec='seconds'), now.isoformat(sep=' ', timespec='seconds'))
]
for property_id, guest_id, room_id, check_in, check_out, status, price, payment_status, created_at, updated_at in data:
    c.execute("INSERT INTO reservations (property_id, guest_id, room_id, check_in, check_out, status, price, payment_status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (property_id, guest_id, room_id, check_in, check_out, status, price, payment_status, created_at, updated_at))

conn.commit()
conn.close()
print('Sample reservations inserted.')
