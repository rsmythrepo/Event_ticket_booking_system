-- Insert roles
INSERT INTO role (role_name) VALUES
('Admin'),
('User');

-- Insert users
INSERT INTO `user` (username, firstname, secondname, email, password_hash, role_id) VALUES
('admin', 'Admin', 'User', 'admin@example.com', 'hashed_password', 1),
('john_doe', 'John', 'Doe', 'john@example.com', 'hashed_password', 2),
('jane_smith', 'Jane', 'Smith', 'jane@example.com', 'hashed_password', 2),
('alice_johnson', 'Alice', 'Johnson', 'alice@example.com', 'hashed_password', 2),
('bob_brown', 'Bob', 'Brown', 'bob@example.com', 'hashed_password', 2),
('charlie_black', 'Charlie', 'Black', 'charlie@example.com', 'hashed_password', 2);

-- Insert events
INSERT INTO event (title, description, venue, start_date, end_date, total_tickets, available_tickets) VALUES
('Concert in the Park', 'A great concert in the park.', 'Central Park', '2024-09-15 18:00:00', '2024-09-15 21:00:00', 100, 30),
('Theater Play', 'An amazing theater play.', 'Downtown Theater', '2024-09-20 19:30:00', '2024-09-20 21:30:00', 100, 20),
('Jazz Night', 'An enchanting evening of jazz music.', 'Jazz Club', '2024-09-25 20:00:00', '2024-09-25 23:00:00', 100, 50),
('Rock Fest', 'A thrilling rock music festival.', 'Stadium', '2024-09-30 16:00:00', '2024-09-30 22:00:00', 100, 0);

-- Insert ticket tiers
INSERT INTO ticket_tier (tier_name, price) VALUES
('General Admission', 50.00),
('VIP Admission', 100.00),
('Early Bird', 30.00); -- Added Early Bird tier

-- Insert event_ticket_tier
INSERT INTO event_ticket_tier (event_id, tier_id, total_tickets) VALUES
(1, 1, 50),  -- 50 General Admission tickets for Concert in the Park
(1, 2, 20),  -- 20 VIP tickets for Concert in the Park
(2, 1, 50),  -- 50 General Admission tickets for Theater Play
(2, 2, 50),  -- 50 VIP tickets for Theater Play
(3, 3, 30),  -- 30 Early Bird tickets for Jazz Night
(4, 1, 40),  -- 40 General Admission tickets for Rock Fest
(4, 2, 30);  -- 30 VIP tickets for Rock Fest

-- Insert seats for the events
INSERT INTO seat (event_id, seat_number, is_available) VALUES
-- Seats for Concert in the Park
(1, 'A1', TRUE),
(1, 'A2', TRUE),
(1, 'A3', TRUE),
(1, 'A4', TRUE),
(1, 'A5', TRUE),
(1, 'A6', TRUE),
(1, 'A7', TRUE),
(1, 'A8', TRUE),
(1, 'A9', TRUE),
(1, 'A10', TRUE),
-- More seats...
(1, 'B1', TRUE),
(1, 'B2', TRUE),
(1, 'B3', TRUE),
(1, 'B4', TRUE),
(1, 'B5', TRUE),
(1, 'B6', TRUE),
(1, 'B7', TRUE),
(1, 'B8', TRUE),
(1, 'B9', TRUE),
(1, 'B10', TRUE),
-- Seats for Theater Play
(2, 'C1', TRUE),
(2, 'C2', TRUE),
(2, 'C3', TRUE),
(2, 'C4', TRUE),
(2, 'C5', TRUE),
(2, 'C6', TRUE),
(2, 'C7', TRUE),
(2, 'C8', TRUE),
(2, 'C9', TRUE),
(2, 'C10', TRUE),
-- More seats...
(2, 'D1', TRUE),
(2, 'D2', TRUE),
(2, 'D3', TRUE),
(2, 'D4', TRUE),
(2, 'D5', TRUE),
(2, 'D6', TRUE),
(2, 'D7', TRUE),
(2, 'D8', TRUE),
(2, 'D9', TRUE),
(2, 'D10', TRUE),
-- Seats for Jazz Night
(3, 'E1', TRUE),
(3, 'E2', TRUE),
(3, 'E3', TRUE),
(3, 'E4', TRUE),
(3, 'E5', TRUE),
(3, 'E6', TRUE),
(3, 'E7', TRUE),
(3, 'E8', TRUE),
(3, 'E9', TRUE),
(3, 'E10', TRUE),
-- Seats for Rock Fest
(4, 'F1', TRUE),
(4, 'F2', TRUE),
(4, 'F3', TRUE),
(4, 'F4', TRUE),
(4, 'F5', TRUE),
(4, 'F6', TRUE),
(4, 'F7', TRUE),
(4, 'F8', TRUE),
(4, 'F9', TRUE),
(4, 'F10', TRUE);

-- Insert bookings and tickets (70 sold tickets total)
INSERT INTO booking (user_id, event_id, total_amount) VALUES
-- Concert in the Park
(2, 1, 150.00), -- John Doe buys 3 General Admission tickets
(3, 1, 200.00), -- Jane Smith buys 4 General Admission tickets
(4, 1, 100.00), -- Alice buys 2 VIP tickets
(5, 1, 50.00),  -- Bob buys 1 General Admission ticket
(6, 1, 300.00), -- Charlie buys 5 General Admission tickets
-- Theater Play
(2, 2, 200.00), -- John buys 4 tickets (General Admission)
(3, 2, 150.00), -- Jane buys 3 tickets (General Admission)
(4, 2, 100.00), -- Alice buys 2 tickets (VIP)
(5, 2, 300.00), -- Bob buys 3 tickets (2 VIP, 1 General)
(6, 2, 250.00), -- Charlie buys 2 tickets (VIP)
-- Jazz Night
(2, 3, 90.00),  -- John buys 3 Early Bird tickets
(3, 3, 60.00),  -- Jane buys 2 Early Bird tickets
(4, 3, 90.00),  -- Alice buys 3 Early Bird tickets
(5, 3, 120.00), -- Bob buys 4 Early Bird tickets
(6, 3, 60.00),  -- Charlie buys 2 Early Bird tickets
-- Rock Fest
(2, 4, 250.00), -- John buys 5 General Admission tickets
(3, 4, 300.00), -- Jane buys 6 General Admission tickets
(4, 4, 200.00), -- Alice buys 4 VIP tickets
(5, 4, 200.00), -- Bob buys 4 General Admission tickets
(6, 4, 150.00); -- Charlie buys 3 VIP tickets
INSERT INTO booking_seat (seat_id, booking_id) VALUES
-- Concert in the Park
(1, 1),
(2, 1),
(3, 1),
(4, 2),
(5, 2),
(6, 2),
(7, 2),
(8, 3),
(9, 3),
(10, 4),
(11, 5),
(12, 5),
(13, 5),
(14, 5),
(15, 5),
-- Theater Play
(16, 6),
(17, 6),
(18, 6),
(19, 7),
(20, 7),
(21, 7),
(22, 8),
(23, 9),
(24, 9),
(25, 9),
(26, 10),
(27, 10),
(28, 10),
-- Jazz Night
(29, 11),
(30, 11),
(31, 11),
(32, 12),
(33, 12),
(34, 13),
(35, 13),
(36, 14),
(37, 14),
(38, 14),
(39, 15),
(40, 15),
-- Rock Fest
(41, 16),
(42, 16),
(43, 16),
(44, 16),
(45, 16),
(46, 17),
(47, 17),
(48, 17),
(49, 17),
(50, 17),
(51, 18),
(52, 18),
(53, 18),
(54, 18),
(55, 19),
(56, 19),
(57, 19),
(58, 19),
(59, 20),
(60, 20),
(61, 20),
(62, 20),
(63, 20),
(64, 20);
-- Insert tickets
INSERT INTO ticket (booking_id, event_id, seat_id, tier_id) VALUES
-- Concert in the Park
(1, 1, 1, 1),  -- John Doe - Ticket 1
(1, 1, 2, 1),  -- John Doe - Ticket 2
(1, 1, 3, 1),  -- John Doe - Ticket 3
(2, 1, 4, 1),  -- Jane Smith - Ticket 1
(2, 1, 5, 1),  -- Jane Smith - Ticket 2
(2, 1, 6, 1),  -- Jane Smith - Ticket 3
(2, 1, 7, 1),  -- Jane Smith - Ticket 4
(3, 1, 8, 2),  -- Alice - Ticket 1 (VIP)
(3, 1, 9, 2),  -- Alice - Ticket 2 (VIP)
(4, 1, 10, 1), -- Bob - Ticket 1
(5, 1, 11, 1), -- Charlie - Ticket 1
(5, 1, 12, 1), -- Charlie - Ticket 2
(5, 1, 13, 1), -- Charlie - Ticket 3
(5, 1, 14, 1), -- Charlie - Ticket 4
(5, 1, 15, 1), -- Charlie - Ticket 5
-- Theater Play
(6, 2, 16, 1), -- John - Ticket 1
(6, 2, 17, 1), -- John - Ticket 2
(6, 2, 18, 1), -- John - Ticket 3
(7, 2, 19, 1), -- Jane - Ticket 1
(7, 2, 20, 1), -- Jane - Ticket 2
(7, 2, 21, 1), -- Jane - Ticket 3
(8, 2, 22, 2), -- Alice - Ticket 1 (VIP)
(9, 2, 23, 2), -- Bob - Ticket 1 (VIP)
(9, 2, 24, 2), -- Bob - Ticket 2 (VIP)
(9, 2, 25, 1), -- Bob - Ticket 3 (General Admission)
(10, 2, 26, 2), -- Charlie - Ticket 1 (VIP)
(10, 2, 27, 2), -- Charlie - Ticket 2 (VIP)
(10, 2, 28, 1), -- Charlie - Ticket 3 (General Admission)
-- Jazz Night
(11, 3, 29, 3), -- John - Ticket 1
(11, 3, 30, 3), -- John - Ticket 2
(11, 3, 31, 3), -- John - Ticket 3
(12, 3, 32, 3), -- Jane - Ticket 1
(12, 3, 33, 3), -- Jane - Ticket 2
(13, 3, 34, 3), -- Alice - Ticket 1
(13, 3, 35, 3), -- Alice - Ticket 2
(14, 3, 36, 3), -- Bob - Ticket 1
(14, 3, 37, 3), -- Bob - Ticket 2
(14, 3, 38, 3), -- Bob - Ticket 3
(15, 3, 39, 3), -- Charlie - Ticket 1
(15, 3, 40, 3), -- Charlie - Ticket 2
-- Rock Fest
(16, 4, 41, 1), -- John - Ticket 1
(16, 4, 42, 1), -- John - Ticket 2
(16, 4, 43, 1), -- John - Ticket 3
(16, 4, 44, 1), -- John - Ticket 4
(16, 4, 45, 1), -- John - Ticket 5
(17, 4, 46, 1), -- Jane - Ticket 1
(17, 4, 47, 1), -- Jane - Ticket 2
(17, 4, 48, 1), -- Jane - Ticket 3
(17, 4, 49, 2), -- Jane - Ticket 4 (VIP)
(17, 4, 50, 2), -- Jane - Ticket 5 (VIP)
(17, 4, 51, 2), -- Jane - Ticket 6 (VIP)
(18, 4, 52, 2), -- Alice - Ticket 1 (VIP)
(18, 4, 53, 2), -- Alice - Ticket 2 (VIP)
(18, 4, 54, 2), -- Alice - Ticket 3 (VIP)
(18, 4, 55, 2), -- Alice - Ticket 4 (VIP)
(19, 4, 56, 1), -- Bob - Ticket 1
(19, 4, 57, 1), -- Bob - Ticket 2
(19, 4, 58, 1), -- Bob - Ticket 3
(19, 4, 59, 1), -- Bob - Ticket 4
(20, 4, 60, 2), -- Charlie - Ticket 1 (VIP)
(20, 4, 61, 2), -- Charlie - Ticket 2 (VIP)
(20, 4, 62, 1), -- Charlie - Ticket 3
(20, 4, 63, 1), -- Charlie - Ticket 4
(20, 4, 64, 1); -- Charlie - Ticket 5

-- Insert booking_seat entries


-- Insert payment details
INSERT INTO payment_detail (user_id, card_type, card_number, cardholder_name, expiration_date, billing_address, default_payment) VALUES
(2, 'Visa', '4111111111111111', 'John Doe', '2025-12-01', '123 Main St, Cityville', TRUE),
(3, 'MasterCard', '5111111111111118', 'Jane Smith', '2026-06-01', '456 Elm St, Townsville', FALSE),
(4, 'American Express', '371449635398431', 'Alice Johnson', '2026-05-01', '789 Oak St, Villagetown', FALSE),
(5, 'Visa', '4111111111111111', 'Bob Brown', '2025-01-01', '101 Pine St, Cityville', TRUE),
(6, 'MasterCard', '5111111111111118', 'Charlie Black', '2026-07-01', '202 Birch St, Townsville', FALSE);

-- Insert payments
INSERT INTO payment (booking_id, payment_detail_id, payment_amount, payment_status) VALUES
(1, 1, 150.00, 'paid'),  -- Payment for John's 3 tickets
(2, 1, 200.00, 'paid'),  -- Payment for Jane's 4 tickets
(3, 1, 200.00, 'paid'),  -- Payment for Alice's 2 tickets (VIP)
(4, 1, 50.00, 'paid'),   -- Payment for Bob's ticket
(5, 1, 300.00, 'paid'),  -- Payment for Charlie's 5 tickets
(6, 2, 200.00, 'paid'),  -- Payment for John's 4 tickets
(7, 2, 150.00, 'paid'),  -- Payment for Jane's 3 tickets
(8, 3, 100.00, 'paid'),  -- Payment for Alice's VIP tickets
(9, 4, 300.00, 'paid'),  -- Payment for Bob's tickets
(10, 2, 250.00, 'paid'), -- Payment for Charlie's VIP tickets
(11, 1, 90.00, 'paid'),  -- Payment for John's 3 tickets
(12, 1, 60.00, 'paid'),  -- Payment for Jane's 2 tickets
(13, 1, 90.00, 'paid'),  -- Payment for Alice's tickets
(14, 1, 120.00, 'paid'), -- Payment for Bob's 4 tickets
(15, 1, 60.00, 'paid'),  -- Payment for Charlie's tickets
(16, 1, 250.00, 'paid'), -- Payment for John's 5 tickets
(17, 1, 300.00, 'paid'), -- Payment for Jane's tickets
(18, 1, 200.00, 'paid'), -- Payment for Alice's 4 tickets
(19, 1, 200.00, 'paid'), -- Payment for Bob's tickets
(20, 1, 150.00, 'paid'); -- Payment for Charlie's tickets
