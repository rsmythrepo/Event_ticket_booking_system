from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash

from __init__ import app, db
from ORM.DBClasses import Event, Seat, Booking, TicketTier, EventTicketTier, User

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


@app.route('/bookevent/<int:event_id>', methods=['GET', 'POST'])
def book_event(event_id):
    event = Event.query.get(event_id)
    if not event:
        flash("Event not found!", "error")
        return redirect(url_for('homepage'))

    if request.method == 'POST':
        user_id = 1
        seat_count = int(request.form['seat_count'])

        if event.available_tickets >= seat_count:
            event.available_tickets -= seat_count

            booking = Booking(user_id=user_id, event_id=event_id, total_amount=seat_count * event.price_range[0])
            db.session.add(booking)
            db.session.commit()

            available_seats = Seat.query.filter_by(event_id=event_id, is_available=True).limit(seat_count).all()
            for seat in available_seats:
                seat.is_available = False
                db.session.commit()

            flash("Booking successful!", "success")
        else:
            flash("Not enough seats available.", "error")

        return redirect(url_for('my_bookings'))

    return render_template('event_details.html', event=event)

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
    if 'user_id' not in session:
        flash('Please log in to manage your bookings.', 'error')
        return redirect(url_for('login'))

    user_id = session['user_id']  # Fetch the logged-in user's ID

    try:
        # Fetch the user's active bookings
        user_bookings = Booking.query.filter_by(user_id=user_id, booking_status='confirmed').all()

        # Format the bookings to match the template's expected structure
        bookings = [{
            'id': booking.booking_id,
            'event_title': booking.event.title,
            'date': booking.booking_date.strftime('%Y-%m-%d %H:%M'),
            'seats': booking.total_tickets,
            'status': booking.booking_status
        } for booking in user_bookings]

    except Exception as e:
        flash(f"Error fetching bookings: {str(e)}", 'error')
        bookings = []

    return render_template('booking_management.html', bookings=bookings)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        print(request.form)
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        username = request.form['username']
        email = request.form['email']  # New email field
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
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            flash("Invalid username or password!", "error")
            return redirect(url_for('login'))
        session['user_id'] = user.id
        session['username'] = user.username
        flash("Login successful!", "success")
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