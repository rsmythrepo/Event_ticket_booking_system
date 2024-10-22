

-- Trigger to automatically set the seat as unavailable when a ticket is inserted
DELIMITER $$
CREATE TRIGGER after_ticket_insert
AFTER INSERT ON ticket
FOR EACH ROW
BEGIN
    UPDATE seat
    SET is_available = FALSE
    WHERE seat_id = NEW.seat_id;
END$$
DELIMITER ;


-- Trigger to automatically set the seat as available when a ticket is refunded
DELIMITER $$
CREATE TRIGGER after_payment_update
AFTER UPDATE ON payment
FOR EACH ROW
BEGIN
    IF NEW.payment_status = 'refunded' THEN
        UPDATE seat
        SET is_available = TRUE
        WHERE seat_id IN (SELECT seat_id FROM ticket WHERE booking_id = NEW.booking_id);
    END IF;
END$$
DELIMITER ;


-- Trigger to ensure total_tickets equals the total number of seats for an event
DELIMITER $$
CREATE TRIGGER before_seat_insert
BEFORE INSERT ON seat
FOR EACH ROW
BEGIN
    DECLARE seat_count INT;
    SELECT COUNT(*) INTO seat_count FROM seat WHERE event_id = NEW.event_id;

    -- Check if adding the new seat exceeds the total_tickets
    IF seat_count + 1 > (SELECT total_tickets FROM event WHERE event_id = NEW.event_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cannot add more seats than the total_tickets for the event.';
    END IF;
END$$
DELIMITER ;

-- Trigger to automatically update available_tickets when a ticket is booked
DELIMITER $$
CREATE TRIGGER after_ticket_insert
AFTER INSERT ON ticket
FOR EACH ROW
BEGIN
    UPDATE seat
    SET is_available = FALSE
    WHERE seat_id = NEW.seat_id;

    -- Update the available_tickets in the event table
    UPDATE event
    SET available_tickets = (SELECT COUNT(*) FROM seat WHERE event_id = NEW.event_id AND is_available = TRUE)
    WHERE event_id = NEW.event_id;
END$$
DELIMITER ;

-- Trigger to automatically update available_tickets when a ticket is refunded
DELIMITER $$
CREATE TRIGGER after_payment_update
AFTER UPDATE ON payment
FOR EACH ROW
BEGIN
    IF NEW.payment_status = 'refunded' THEN
        UPDATE seat
        SET is_available = TRUE
        WHERE seat_id IN (SELECT seat_id FROM ticket WHERE booking_id = NEW.booking_id);

        -- Update the available_tickets in the event table
        UPDATE event
        SET available_tickets = (SELECT COUNT(*) FROM seat WHERE event_id = (SELECT event_id FROM ticket WHERE booking_id = NEW.booking_id) AND is_available = TRUE)
        WHERE event_id = (SELECT event_id FROM ticket WHERE booking_id = NEW.booking_id);
    END IF;
END$$
DELIMITER ;