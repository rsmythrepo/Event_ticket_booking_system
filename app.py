from flask import Flask, render_template, request, redirect, url_for, flash, session
from __init__ import app, db
from ORM.DBClasses import Event, Seat, Booking, TicketTier, EventTicketTier

bookings = []
users = []
admins = []

@app.route('/')
def homepage():
    # Extract the query parameters for filtering
    price_from = request.args.get('price_from', type=int)  # Price Range From
    price_until = request.args.get('price_until', type=int)  # Price Range Until
    date = request.args.get('date')  # Date Filter
    selected_venues = request.args.getlist('venue')  # Multiple selected venues

    try:
        # Fetch all unique venues for the venue filter
        venues = [v.venue for v in db.session.query(Event.venue).distinct()]

        # Start with a base query for events, joining event_ticket_tier and ticket_tier for price filtering
        events_query = db.session.query(Event).join(EventTicketTier).join(TicketTier)

        # Apply price range filter if both values are provided
        if price_from is not None and price_until is not None:
            events_query = events_query.filter(TicketTier.price >= price_from, TicketTier.price <= price_until)
        elif price_from is not None:
            events_query = events_query.filter(TicketTier.price >= price_from)
        elif price_until is not None:
            events_query = events_query.filter(TicketTier.price <= price_until)

        # Apply date filter if selected
        if date:
            events_query = events_query.filter(db.func.date(Event.start_date) == date)

        # Apply venue filter if multiple venues are selected
        if selected_venues:
            events_query = events_query.filter(Event.venue.in_(selected_venues))

        # Fetch the filtered events, sorted by start date
        events = events_query.order_by(Event.start_date.asc()).all()

        # Add a count of available seats for each event
        for event in events:
            event.available_tickets = Seat.query.filter_by(event_id=event.event_id, is_available=True).count()

    except Exception as e:
        flash(f"Error fetching events: {str(e)}", "error")
        events = []
        venues = []

    # Render the template with the filtered events and venue options
    return render_template('home.html', events=events, venues=venues)


@app.route('/event/<int:event_id>')
def event_details(event_id):
    try:
        # Fetch the event by ID
        event = Event.query.get(event_id)
        if not event:
            flash("Event not found!", "error")
            return redirect(url_for('homepage'))

    except Exception as e:
        flash(f"Error fetching event details: {str(e)}", "error")
        return redirect(url_for('homepage'))

    # Pass the event to the template
    return render_template('event_details.html', event=event)


@app.route('/event/<int:event_id>/seats')
def show_event_seats(event_id):
    try:
        seats = Seat.query.filter_by(event_id=event_id, is_available=True).all()
        if len(seats) == 0:
            return render_template('no_seats.html')
        return render_template('seats.html', seats=seats)
    except Exception as e:
        return f"Error: {e}"

@app.route('/payment/<int:event_id>', methods=['POST'])
def payment(event_id):
    event = Event.query.get(event_id)
    if not event:
        return "Event not found", 404

    # Assuming you have a session with the logged-in user's ID
    #user_id = session.get('user_id')
    #user = User.query.get(user_id)

    # Retrieve the selected seat numbers from the form
    selected_seats = request.form.get('selected_seats')
    if not selected_seats:
        return "No seats selected", 400

    # Convert the selected seats to a list (e.g., ['A3', 'A4'])
    selected_seats_list = selected_seats.split(',')

    # Retrieve the selected seats from the database based on seat_number and event_id
    seats = Seat.query.filter(
        Seat.seat_number.in_(selected_seats_list),
        Seat.event_id == event_id,
        Seat.is_available == True  # Ensure the seat is available
    ).all()

    if not seats or len(seats) != len(selected_seats_list):
        return "Selected seats not available", 400

    # Assuming each seat belongs to a certain ticket tier
    total_amount = 0
    for seat in seats:
        # Retrieve the ticket tier for the event and calculate the price
        tier = TicketTier.query.join(EventTicketTier).filter(EventTicketTier.event_id == event_id).first()
        if tier:
            total_amount += tier.price


    # Render the payment page with event, seats, and total amount
    return render_template('payment.html', event=event, seats=selected_seats_list, total_amount=total_amount)


@app.route('/confirm_payment/<int:event_id>', methods=['POST'])
def confirm_payment(event_id):
    event = Event.query.get(event_id)
    if not event:
        return "Event not found", 404

    # Retrieve form data from the payment page
    cardholder_name = request.form.get('cardholder_name')
    card_type = request.form.get('card_type')
    card_number = request.form.get('card_number')
    expiration_date = request.form.get('expiration_date')
    billing_address = request.form.get('billing_address')
    total_amount = request.form.get('total_amount')
    selected_seats = request.form.get('selected_seats')

    # Convert the selected seats to a list (e.g., ['A3', 'A4'])
    selected_seats_list = selected_seats.split(',')
    seats = Seat.query.filter(
        Seat.seat_number.in_(selected_seats_list),
        Seat.event_id == event_id,
        Seat.is_available == True  # Ensure the seat is available
    ).all()

    # If payment is successful mark seats as unavailable
    for seat in seats:
        seat.is_available = False  # Mark seats as booked
        db.session.add(seat)

    # Save change of seat and payment
    db.session.commit()

    # Redirect to the booking summary page
    return redirect(url_for('booking_summary', event_id=event.event_id, selected_seats=selected_seats, total_amount=total_amount))

@app.route('/booking_summary/<int:event_id>')
def booking_summary(event_id):
    event = Event.query.get(event_id)
    selected_seats = request.args.get('selected_seats')
    total_amount = request.args.get('total_amount')

    selected_seats_list = selected_seats.split(',')

    return render_template('booking_summary.html', event=event, selected_seats=selected_seats_list, total_amount=total_amount)


@app.route('/mybookings')
def my_bookings():
    user = "user123"  # Simulating a logged-in user
    user_bookings = [b for b in bookings if b['user'] == user]
    user_events = [e for e in events if e['id'] in [b['event_id'] for b in user_bookings]]
    return render_template('booking_summary.html', bookings=user_bookings, events=user_events)


@app.route('/bookingmanagement')
def booking_management():
    user = "user123"
    user_bookings = [b for b in bookings if b['user'] == user]
    return render_template('booking_management.html', bookings=user_bookings)


def is_admin():
    return session.get('is_admin', False)


@app.route('/admin43fDSGSg34g')
def admin_login():
    session['is_admin'] = True
    flash("You are now logged in as admin.", "success")
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/dashboard')
def admin_dashboard():
    if not is_admin():
        flash("Unauthorized access!", "error")
        return redirect(url_for('homepage'))
    return render_template('admin/admin_dashboard.html')


@app.route('/admin/events')
def admin_events():
    if not is_admin():
        flash("Unauthorized access!", "error")
        return redirect(url_for('homepage'))
    return render_template('admin/admin_event_management.html', events=events)


@app.route('/admin/salesreport')
def sales_report():
    if not is_admin():
        flash("Unauthorized access!", "error")
        return redirect(url_for('homepage'))
    total_tickets_sold = sum([event['seats'] - event['available_seats'] for event in events])
    total_revenue = sum([(event['seats'] - event['available_seats']) * event['price_range'][0] for event in events])
    return render_template('admin/admin_sales_report.html', total_tickets_sold=total_tickets_sold, total_revenue=total_revenue)


@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    flash("You have been logged out.", "success")
    return redirect(url_for('homepage'))


if __name__ == '__main__':
    app.run(debug=True)
