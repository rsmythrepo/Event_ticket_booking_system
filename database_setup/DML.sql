

-- generated data for testing
USE event_bookings;
INSERT INTO role (role_name)
VALUES ('admin'), ('user');

INSERT INTO `user` (username, firstname, secondname, email, password_hash, role_id)
VALUES
('john.doe', 'John', 'Doe', 'john.doe@example.com', 'hashed_password_1', 2),
('jane.smith', 'Jane', 'Smith', 'jane.smith@example.com', 'hashed_password_2', 2),
('admin', 'Admin', 'User', 'admin@example.com', 'hashed_password_3', 1);

INSERT INTO event (title, description, venue, start_date, end_date, total_tickets, available_tickets, booking_open_time, booking_close_time)
VALUES
('Concert A', 'A live concert by Band X', 'Stadium 1', '2024-11-20 19:00:00', '2024-11-20 22:00:00', 5, 5, '2024-10-27 00:00:00', '2024-11-20 18:00:00'),
('Theater Play B', 'A famous drama play', 'Theater 2', '2024-12-01 18:00:00', '2024-12-01 21:00:00', 10, 10, '2024-10-27 00:00:00', '2024-12-01 17:00:00'),
('Sports Match C', 'Football match between Team A and Team B', 'Arena 3', '2024-12-15 15:00:00', '2024-12-15 17:00:00', 8, 8, '2024-10-27 00:00:00', '2024-12-15 14:00:00');

INSERT INTO ticket_tier (tier_name, price)
VALUES
('VIP', 150.00),
('General Admission', 75.00),
('Economy', 50.00);

INSERT INTO event_ticket_tier (event_id, tier_id, total_tickets)
VALUES
(1, 2, 5),   -- Event 1, General Admission (5 tickets)
(2, 1, 5),   -- Event 2, VIP (5 tickets)
(2, 2, 5),   -- Event 2, General Admission (5 tickets)
(3, 3, 8);   -- Event 3, Economy (8 tickets)

INSERT INTO seat (event_id, seat_number, is_available, tier_id)
VALUES
(1, 'A1', TRUE, 2),
(1, 'A2', TRUE, 2),
(1, 'A3', TRUE, 2),
(1, 'A4', TRUE, 2),
(1, 'A5', TRUE, 2),
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
(3, 'C1', TRUE, 3),
(3, 'C2', TRUE, 3),
(3, 'C3', TRUE, 3),
(3, 'C4', TRUE, 3),
(3, 'C5', TRUE, 3),
(3, 'C6', TRUE, 3),
(3, 'C7', TRUE, 3),
(3, 'C8', TRUE, 3);

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
(1, 1, 'Your booking for Concert A is confirmed!', 'email', 'sent'),
(2, 2, 'Your booking for Theater Play B is confirmed!', 'email', 'sent');

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

