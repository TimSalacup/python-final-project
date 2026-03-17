-- name: create_users_table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

-- name: create_bookings_table
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    car_name TEXT NOT NULL,
    booking_date TEXT NOT NULL,
    hours INTEGER NOT NULL,
    price INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- name: select_user_by_credentials
SELECT id, name, email
FROM users
WHERE name = ? AND email = ? AND password = ?;

-- name: insert_user
INSERT INTO users(name, email, password)
VALUES (?, ?, ?);

-- name: insert_booking
INSERT INTO bookings(user_id, car_name, booking_date, hours, price)
VALUES (?, ?, ?, ?, ?);

-- name: select_bookings_for_user
SELECT id, car_name, booking_date, hours, price
FROM bookings
WHERE user_id = ?
ORDER BY id DESC;

-- name: delete_booking_for_user
DELETE FROM bookings
WHERE id = ? AND user_id = ?;
