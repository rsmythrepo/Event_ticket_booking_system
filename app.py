from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash

from __init__ import app, db
from ORM.DBClasses import db, User, Event, Seat, Booking, BookingSeat, Ticket, TicketTier, EventTicketTier, PaymentDetail, Payment

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
        Seat.is_available == True
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

    cardholder_name = request.form.get('cardholder_name')
    card_type = request.form.get('card_type')
    card_number = request.form.get('card_number')
    expiration_date = request.form.get('expiration_date')
    billing_address = request.form.get('billing_address')
    total_amount = request.form.get('total_amount')
    selected_seats = request.form.get('selected_seats')
    #save_payment_details = request.form.get('user_payment_details')

    selected_seats_list = selected_seats.split(',')
    seats = Seat.query.filter(
        Seat.seat_number.in_(selected_seats_list),
        Seat.event_id == event_id,
        Seat.is_available == True
    ).all()

    user_id = session.get('user_id')
    user = User.query.get(user_id)

    # Step 1: Create a new Booking
    new_booking = Booking(
        user_id=user.user_id,
        event_id=event_id,
        total_amount=total_amount,
        booking_status='confirmed'
    )
    db.session.add(new_booking)
    db.session.flush()

    # Step 2: Mark seats as unavailable and associate them with the booking
    for seat in seats:
        seat.is_available = False  # Mark seats as booked
        booking_seat = BookingSeat(seat_id=seat.seat_id, booking_id=new_booking.booking_id)
        db.session.add(booking_seat)

        # Step 3: Generate a Ticket for each booked seat
        tier = TicketTier.query.join(EventTicketTier).filter(EventTicketTier.event_id == event_id).first()
        new_ticket = Ticket(
            booking_id=new_booking.booking_id,
            event_id=event_id,
            seat_id=seat.seat_id,
            tier_id=tier.tier_id  # Assuming we are associating with a specific tier
        )
        db.session.add(new_ticket)

    # Step 4: Update the event's ticket counts
    event.available_tickets -= len(selected_seats_list)
    db.session.add(event)

    # Step 5: Add Payment Details for the user
    expiration_date_str = expiration_date + '-01'
    payment_detail = PaymentDetail(
        user_id=user.user_id,
        card_type=card_type,
        card_number=card_number,
        cardholder_name=cardholder_name,
        expiration_date=expiration_date_str,
        billing_address=billing_address
    )
    db.session.add(payment_detail)
    db.session.flush()

    # Step 6: Record the payment itself
    payment = Payment(
        booking_id=new_booking.booking_id,
        payment_detail_id=payment_detail.payment_detail_id,
        payment_amount=total_amount,
        payment_status='paid'  # Assuming the payment is successful
    )
    db.session.add(payment)

    # Save change of seat and payment
    db.session.commit()

    # Redirect to the booking summary page
    return redirect(url_for('payment_confirmation', event_id=event.event_id, selected_seats=selected_seats, total_amount=total_amount))

@app.route('/payment_confirmation/<int:event_id>')
def payment_confirmation(event_id):
    event = Event.query.get(event_id)
    selected_seats = request.args.get('selected_seats')
    total_amount = request.args.get('total_amount')
    user_id = session.get('user_id')
    user = User.query.get(user_id)

    selected_seats_list = selected_seats.split(',')

    return render_template('payment_confirmation.html', event=event, selected_seats=selected_seats_list, total_amount=total_amount, firstname=user.firstname)


@app.route('/mybookings')
def my_bookings():
    if 'user_id' not in session:
        flash("Please log in to view your bookings.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    user_bookings = Booking.query.filter_by(user_id=user_id).all()
    event_ids = [booking.event_id for booking in user_bookings]
    user_events = Event.query.filter(Event.event_id.in_(event_ids)).all()

    return render_template('booking_summary.html', bookings=user_bookings, events=user_events)

@app.route('/bookingmanagement')
def booking_management():
    user = "user123"
    user_bookings = [b for b in bookings if b['user'] == user]
    return render_template('booking_management.html', bookings=user_bookings)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('homepage'))
    if request.method == 'POST':
        print(request.form)
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Username already exists!", "error")
            return redirect(url_for('register'))

        if existing_email:
            flash("Email already registered!", "error")
            return redirect(url_for('register'))

        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(password)
        new_user = User(
            firstname=firstname,
            secondname=lastname,
            username=username,
            email=email,
            password_hash=hashed_password,
            role_id=1
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')




@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('homepage'))
    if request.method == 'POST':
        username = request.form['username']
        password_hash = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password_hash, password_hash):
            flash("Invalid username or password!", "error")
            return redirect(url_for('login'))
        session['user_id'] = user.user_id
        session['username'] = user.username

        print(session['user_id'])
        return redirect(url_for('homepage'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash("You have been logged out.", "success")
    return redirect(url_for('homepage'))






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
