CREATE DATABASE IF NOT EXISTS event_bookings;
USE event_bookings;

CREATE TABLE role (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL
);

CREATE TABLE `user` (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    firstname VARCHAR(50) NOT NULL,
    secondname VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES role(role_id) ON DELETE CASCADE
);

CREATE TABLE event (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    venue VARCHAR(255) NOT NULL,
    start_date DATETIME NOT NULL,
    end_date DATETIME NOT NULL,
    total_tickets INT NOT NULL,
    available_tickets INT NOT NULL,
    booking_open_time DATETIME,
    booking_close_time DATETIME
);

CREATE TABLE booking (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    event_id INT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    booking_status ENUM('confirmed', 'cancelled') DEFAULT 'confirmed',
    FOREIGN KEY (user_id) REFERENCES `user`(user_id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES event(event_id) ON DELETE CASCADE
);

CREATE TABLE ticket_tier (
    tier_id INT AUTO_INCREMENT PRIMARY KEY,
    tier_name VARCHAR(50) NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);

CREATE TABLE event_ticket_tier (
    event_id INT NOT NULL,
    tier_id INT NOT NULL,
    total_tickets INT NOT NULL,
    PRIMARY KEY (event_id, tier_id),
    FOREIGN KEY (event_id) REFERENCES event(event_id) ON DELETE CASCADE,
    FOREIGN KEY (tier_id) REFERENCES ticket_tier(tier_id) ON DELETE CASCADE
);

CREATE TABLE seat (
    seat_id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    tier_id INT,
    seat_number VARCHAR(10) NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (event_id) REFERENCES event(event_id) ON DELETE CASCADE,
    FOREIGN KEY (tier_id) REFERENCES ticket_tier(tier_id) ON DELETE SET NULL,
    UNIQUE(event_id, seat_number)
);

CREATE TABLE booking_seat (
    seat_id INT NOT NULL,
    booking_id INT NOT NULL,
    PRIMARY KEY (seat_id, booking_id),
    FOREIGN KEY (seat_id) REFERENCES seat(seat_id) ON DELETE CASCADE,
    FOREIGN KEY (booking_id) REFERENCES booking(booking_id) ON DELETE CASCADE
);

CREATE TABLE ticket (
    ticket_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    event_id INT NOT NULL,
    seat_id INT NOT NULL,
    tier_id INT NOT NULL,
    FOREIGN KEY (booking_id) REFERENCES booking(booking_id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES event(event_id) ON DELETE CASCADE,
    FOREIGN KEY (seat_id) REFERENCES seat(seat_id) ON DELETE CASCADE,
    FOREIGN KEY (tier_id) REFERENCES ticket_tier(tier_id) ON DELETE CASCADE
);

CREATE TABLE notification (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    event_id INT NOT NULL,
    message TEXT,
    notification_type TEXT,
    notification_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('sent', 'pending') DEFAULT 'pending',
    FOREIGN KEY (user_id) REFERENCES `user`(user_id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES event(event_id) ON DELETE CASCADE
);

CREATE TABLE payment_detail (
    payment_detail_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    card_type ENUM('Visa', 'MasterCard', 'AmEx', 'Discover') NOT NULL,
    card_number VARBINARY(255) NOT NULL,
    cardholder_name VARCHAR(100) NOT NULL,
    expiration_date DATE NOT NULL,
    billing_address TEXT NOT NULL,
    default_payment BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES `user`(user_id) ON DELETE CASCADE
);

CREATE TABLE payment (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    payment_detail_id INT,
    payment_amount DECIMAL(10, 2) NOT NULL,
    payment_status ENUM('pending', 'paid', 'failed', 'refunded') DEFAULT 'pending',
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES booking(booking_id) ON DELETE CASCADE,
    FOREIGN KEY (payment_detail_id) REFERENCES payment_detail(payment_detail_id) ON DELETE SET NULL
);



INSERT INTO role (role_name)
VALUES ('admin'), ('user');

INSERT INTO `user` (username, firstname, secondname, email, password_hash, role_id)
VALUES
('john.doe', 'John', 'Doe', 'john.doe@example.com', 'hashed_password_1', 2),
('jane.smith', 'Jane', 'Smith', 'jane.smith@example.com', 'hashed_password_2', 2),
('admin', 'Admin', 'User', 'admin@example.com', 'hashed_password_3', 1);

INSERT INTO event (title, description, venue, start_date, end_date, total_tickets, available_tickets, booking_open_time, booking_close_time)
VALUES
('Rock Night Live', 'A high-energy concert featuring top rock bands.', 'Downtown Arena', '2024-12-15 19:00:00', '2024-12-15 23:00:00', 500, 500, '2024-11-01 10:00:00', '2024-12-15 23:00:00'),
('Jazz Evening', 'An intimate jazz performance with renowned musicians.', 'City Jazz Club', '2024-12-20 18:00:00', '2024-12-20 21:00:00', 200, 200, '2024-11-01 09:00:00', '2024-12-20 21:00:00'),
('Pop Music Festival', 'A full-day event with popular pop artists.', 'Open Air Park', '2025-01-10 14:00:00', '2025-01-10 22:00:00', 1000, 1000, '2024-11-15 10:00:00', '2025-01-10 22:00:00'),
('Classical Night', 'A symphony orchestra performance featuring famous classical pieces.', 'Grand Concert Hall', '2025-01-25 20:00:00', '2025-01-25 22:30:00', 300, 300, '2024-12-01 09:00:00', '2025-01-25 22:30:00'),
('Electronic Dance Festival', 'A night of dance and electronic music with top DJs.', 'City Stadium', '2025-02-05 20:00:00', '2025-02-05 02:00:00', 1500, 1500, '2024-12-01 10:00:00', '2025-02-05 02:00:00'),
('Indie Rock Showcase', 'Live performances by emerging indie rock bands.', 'Underground Club', '2025-02-15 19:00:00', '2025-02-15 23:30:00', 250, 250, '2024-12-10 08:00:00', '2025-02-15 23:30:00'),
('Country Music Night', 'Enjoy live country music with popular artists.', 'Riverside Amphitheater', '2025-02-25 18:30:00', '2025-02-25 22:00:00', 400, 400, '2024-12-01 09:00:00', '2025-02-25 22:00:00'),
('Hip-Hop Bash', 'A concert featuring top hip-hop and rap artists.', 'City Sports Arena', '2025-01-20 19:00:00', '2025-01-20 23:00:00', 800, 800, '2024-11-15 10:00:00', '2025-01-20 23:00:00'),
('Reggae Vibes', 'A relaxing night of reggae music with live performances.', 'Beachside Venue', '2024-12-01 17:00:00', '2024-12-01 21:00:00', 350, 350, '2024-11-01 08:00:00', '2024-12-01 21:00:00'),
('Metal Night', 'An electrifying performance by famous metal bands.', 'Arena X', '2024-12-05 20:00:00', '2024-12-05 23:59:00', 600, 600, '2024-11-01 09:00:00', '2024-12-05 23:59:00');

INSERT INTO ticket_tier (tier_name, price)
VALUES
('VIP', 150.00),
('General Admission', 75.00),
('Economy', 50.00);

INSERT INTO event_ticket_tier (event_id, tier_id, total_tickets)
VALUES
(1, 2, 10),  -- Event 1, General Admission (10 tickets)
(2, 1, 5),   -- Event 2, VIP (5 tickets)
(2, 2, 5),  -- Event 2, General Admission (5 tickets)
(3, 2, 8),   -- Event 3, General Admission (8 tickets)
(4, 1, 2),   -- Event 4, VIP (2 tickets)
(4, 3, 3),   -- Event 4, Economy (3 tickets)
(5, 2, 5),   -- Event 5, General Admission (5 tickets)
(6, 1, 4),   -- Event 6, VIP (4 tickets)
(7, 2, 5),   -- Event 7, General Admission (5 tickets)
(8, 1, 4),   -- Event 8, VIP (4 tickets)
(9, 3, 4),   -- Event 9, Economy (4 tickets)
(10, 2, 4);  -- Event 10, General Admission (4 tickets)

INSERT INTO seat (event_id, seat_number, is_available, tier_id)
VALUES
-- Event 1 Seats (General Admission)
(1, 'A1', TRUE, 2),
(1, 'A2', TRUE, 2),
(1, 'A3', TRUE, 2),
(1, 'A4', TRUE, 2),
(1, 'A5', TRUE, 2),
(1, 'A6', TRUE, 2),
(1, 'A7', TRUE, 2),
(1, 'A8', TRUE, 2),
(1, 'A9', TRUE, 2),
(1, 'A10', TRUE, 2),

-- Event 2 Seats (VIP and General Admission)
(2, 'B1', TRUE, 1),
(2, 'B2', TRUE, 1),
(2, 'B3', TRUE, 1),
(2, 'B4', TRUE, 1),
(2, 'B5', TRUE, 1),
(2, 'B6', TRUE, 2),
(2, 'B7', TRUE, 2),
(2, 'B8', TRUE, 2),
(2, 'B9', TRUE, 2),
(2, 'B10', TRUE, 2),

-- Event 3 Seats (General Admission)
(3, 'C1', TRUE, 2),
(3, 'C2', TRUE, 2),
(3, 'C3', TRUE, 2),
(3, 'C4', TRUE, 2),
(3, 'C5', TRUE, 2),
(3, 'C6', TRUE, 2),
(3, 'C7', TRUE, 2),
(3, 'C8', TRUE, 2),

-- Event 4 Seats (VIP and Economy)
(4, 'D1', TRUE, 1),
(4, 'D2', TRUE, 1),
(4, 'D3', TRUE, 3),
(4, 'D4', TRUE, 3),
(4, 'D5', TRUE, 3),

-- Event 5 Seats (General Admission)
(5, 'E1', TRUE, 2),
(5, 'E2', TRUE, 2),
(5, 'E3', TRUE, 2),
(5, 'E4', TRUE, 2),
(5, 'E5', TRUE, 2),

-- Event 6 Seats (VIP)
(6, 'F1', TRUE, 1),
(6, 'F2', TRUE, 1),
(6, 'F3', TRUE, 1),
(6, 'F4', TRUE, 1),

-- Event 7 Seats (General Admission)
(7, 'G1', TRUE, 2),
(7, 'G2', TRUE, 2),
(7, 'G3', TRUE, 2),
(7, 'G4', TRUE, 2),
(7, 'G5', TRUE, 2),

-- Event 8 Seats (VIP)
(8, 'H1', TRUE, 1),
(8, 'H2', TRUE, 1),
(8, 'H3', TRUE, 1),
(8, 'H4', TRUE, 1),

-- Event 9 Seats (Economy)
(9, 'I1', TRUE, 3),
(9, 'I2', TRUE, 3),
(9, 'I3', TRUE, 3),
(9, 'I4', TRUE, 3),

-- Event 10 Seats (General Admission)
(10, 'J1', TRUE, 2),
(10, 'J2', TRUE, 2),
(10, 'J3', TRUE, 2),
(10, 'J4', TRUE, 2);

INSERT INTO booking (user_id, event_id, total_amount, booking_status)
VALUES
(1, 1, 150.00, 'confirmed'),
(2, 2, 75.00, 'confirmed');

INSERT INTO booking_seat (seat_id, booking_id)
VALUES
(1, 1),
(4, 2);

INSERT INTO ticket (booking_id, event_id, seat_id, tier_id)
VALUES
(1, 1, 1, 2),
(2, 1, 4, 2);


INSERT INTO notification (user_id, event_id, message, notification_type, status)
VALUES
(1, 1, 'Your booking is confirmed!', 'email', 'sent'),
(2, 2, 'Your booking is confirmed!', 'email', 'sent');

-- Update seat availability to FALSE for all seats in the ticket table
UPDATE seat
SET is_available = FALSE
WHERE seat_id IN (SELECT seat_id FROM ticket);

-- Update the event table to reduce the available_tickets for each event based on the number of seats booked
UPDATE event
SET available_tickets = available_tickets - (
    SELECT COUNT(*)
    FROM ticket
    WHERE ticket.event_id = event.event_id
);


