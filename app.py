
import os
import tempfile
from datetime import datetime, timedelta
from io import BytesIO

from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash
import qrcode
from functools import wraps

from __init__ import app, db
from ORM.DBClasses import db, User, Event, Seat, Booking, BookingSeat, Ticket, TicketTier, EventTicketTier, PaymentDetail, Payment
from flask_mail import Mail, Message
from flask import request, jsonify

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = 'askhatabi@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'pyegxiaboyccgymm'  # Replace with your password or App Password
app.config['MAIL_DEFAULT_SENDER'] = ('Booking System', 'askhatabi@gmail.com')  # The sender name and email

# Initialize Mail
mail = Mail(app)

bookings = []
users = []
admins = []

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:  # Check if user_id is in session
            flash("Please log in to access this page.", "error")
            return redirect(url_for('login'))  # Redirect to the login page if not logged in
        return f(*args, **kwargs)
    return decorated_function

def luhn_check(card_number):
    """Validate the credit card number using the Luhn algorithm."""
    card_number = card_number.replace(" ", "")
    if not card_number.isdigit():
        return False

    digits = [int(d) for d in card_number[::-1]]
    total_sum = 0

    for i, digit in enumerate(digits):
        if i % 2 == 1:
            doubled = digit * 2
            if doubled > 9:
                doubled -= 9
            total_sum += doubled
        else:
            total_sum += digit
    return total_sum % 10 == 0

@app.route('/')
@login_required
def homepage():
    now = datetime.now()
    # Extract the query parameters for filtering
    price_from = request.args.get('price_from', type=int)  # Price Range From
    price_until = request.args.get('price_until', type=int)  # Price Range Until
    date = request.args.get('date')  # Date Filter
    selected_venues = request.args.getlist('venue')  # Multiple selected venues

    try:
        # Fetch all unique venues for the venue filter
        venues = [v.venue for v in db.session.query(Event.venue).distinct()]

        # Start base query filtering by booking open and close times
        events_query = db.session.query(Event).filter(
            Event.booking_open_time <= now,
            Event.booking_close_time >= now
        )

        # Apply additional filters for price, date, and venue if provided
        if price_from is not None and price_until is not None:
            events_query = events_query.join(EventTicketTier).join(TicketTier)
            events_query = events_query.filter(TicketTier.price >= price_from, TicketTier.price <= price_until)
        elif price_from is not None:
            events_query = events_query.join(EventTicketTier).join(TicketTier)
            events_query = events_query.filter(TicketTier.price >= price_from)
        elif price_until is not None:
            events_query = events_query.join(EventTicketTier).join(TicketTier)
            events_query = events_query.filter(TicketTier.price <= price_until)

        # Apply date filter if selected
        if date:
            events_query = events_query.filter(db.func.date(Event.start_date) == date)

        # Apply venue filter if multiple venues are selected
        if selected_venues:
            events_query = events_query.filter(Event.venue.in_(selected_venues))

        # Fetch the filtered events, sorted by start date
        events = events_query.order_by(Event.start_date.asc()).all()
        #events = db.session.query(Event).order_by(Event.start_date.asc()).all()

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
@login_required
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
@login_required
def show_event_seats(event_id):
    try:
        seats = Seat.query.filter_by(event_id=event_id, is_available=True).all()
        if len(seats) == 0:
            return render_template('no_seats.html')
        return render_template('seats.html', seats=seats)
    except Exception as e:
        return f"Error: {e}"


@app.route('/send_event_email/<int:event_id>', methods=['POST'])
@login_required
def send_event_email(event_id):
    data = request.get_json()
    friend_email = data.get('email')

    # Fetch event details
    event = Event.query.get(event_id)
    user_id = session.get('user_id')
    user = User.query.get(user_id)

    if not event:
        return jsonify({"success": False, "message": "Event not found."}), 404

    msg = Message(
        subject=f"{event.title} - Event Details",
        recipients=[friend_email]
    )

    msg.body = f"""
    Hello, I wanted to share an event I thought you might be interested in. 

    Here are the details for the event "{event.title}":

    Date & Time: {event.start_date.strftime('%a, %d %B %Y, %H:%M')}
    Venue: {event.venue}
    Description: {event.description}

    Let me know what you think!
    {user.firstname}.
    """
    try:
        mail.send(msg)
        return jsonify({"success": True, "message": "Email sent successfully."}), 200
    except Exception as e:
        print("Error sending email:", e)
        return jsonify({"success": False, "message": "Failed to send email."}), 500


@app.route('/payment/<int:event_id>', methods=['POST'])
@login_required
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
@login_required
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
    save_payment_details = request.form.get('user_payment_details')

    """Luhn algorithm check for card validity - Cant actually use as we dont want to use card details"""
    #if not luhn_check(card_number):
    #    flash("Invalid card number", "error")
    #    return redirect(url_for('payment', event_id=event_id))

    selected_seats_list = selected_seats.split(',')
    seats = Seat.query.filter(
        Seat.seat_number.in_(selected_seats_list),
        Seat.event_id == event_id,
        Seat.is_available == True
    ).all()

    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
    else:
        user = None

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
    if save_payment_details:
        expiration_date_str = expiration_date + '-01'
        # Update all other payment details for this user to not be default
        PaymentDetail.query.filter_by(user_id=user.user_id).update({'default_payment': False})
        payment_detail = PaymentDetail(
            user_id=user.user_id,
            card_type=card_type,
            card_number=card_number,
            cardholder_name=cardholder_name,
            expiration_date=expiration_date_str,
            billing_address=billing_address,
            default_payment=True
        )
        db.session.add(payment_detail)
        db.session.flush()
        payment_detail_id = payment_detail.payment_detail_id
    else:
        payment_detail_id = None

    # Step 6: Record the payment itself
    payment = Payment(
        booking_id=new_booking.booking_id,
        payment_detail_id=payment_detail_id,
        payment_amount=total_amount,
        payment_status='paid'  # Assuming the payment is successful
    )
    db.session.add(payment)

    # Save change of seat and payment
    db.session.commit()

    # Step 7: Send confirmation email
    send_booking_confirmation(user.email, new_booking, event)

    # Redirect to the booking summary page
    return redirect(url_for('payment_confirmation', event_id=event.event_id, selected_seats=selected_seats, total_amount=total_amount))

# Function to send booking confirmation email
def send_booking_confirmation(user_email, booking, event):
    msg = Message('Your Ticket Booking Confirmation', recipients=[user_email])
    msg.body = f'Thank you for booking {event.title}.\n' \
               f'Date: {event.start_date.strftime("%Y-%m-%d %H:%M:%S")}\n' \
               f'Booked Seats: {len(booking.seats)}\n' \
               f'Total Amount: ${booking.total_amount}\n' \
               f'We hope you enjoy the event!'
    mail.send(msg)

@app.route('/payment_confirmation/<int:event_id>')
@login_required
def payment_confirmation(event_id):
    event = Event.query.get(event_id)
    selected_seats = request.args.get('selected_seats')
    total_amount = request.args.get('total_amount')
    user_id = session.get('user_id')
    user = User.query.get(user_id)

    selected_seats_list = selected_seats.split(',')

    return render_template('payment_confirmation.html', event=event, selected_seats=selected_seats_list, total_amount=total_amount, firstname=user.firstname)


@app.route('/mybookings')
@login_required
def my_bookings():
    if 'user_id' not in session:
        flash("Please log in to view your bookings.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    user_bookings = Booking.query.filter_by(user_id=user_id).all()
    event_ids = [booking.event_id for booking in user_bookings]
    user_events = Event.query.filter(Event.event_id.in_(event_ids)).all()

    # Create a dictionary mapping event_id to the event object
    event_dict = {event.event_id: event for event in user_events}

    return render_template('booking_summary.html', bookings=user_bookings, events=event_dict)

@app.route('/bookingmanagement')
@login_required
def booking_management():
    if 'user_id' not in session:
        flash("Please log in to manage your bookings.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    # Fetch bookings for the logged-in user
    user_bookings = Booking.query.filter_by(user_id=user_id).all()
    event_ids = [booking.event_id for booking in user_bookings]
    user_events = Event.query.filter(Event.event_id.in_(event_ids)).all()

    # Create a dictionary of events by their ID
    event_dict = {event.event_id: event for event in user_events}

    return render_template('booking_management.html', bookings=user_bookings, events=event_dict)

@app.route('/cancel_booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get(booking_id)
    if not booking or booking.booking_status == 'cancelled':
        flash("Booking not found or already canceled.", "error")
        return redirect(url_for('booking_management'))

    # Update booking status to cancelled
    booking.booking_status = 'cancelled'
    db.session.add(booking)

    # Mark the seats as available again
    for seat in booking.seats:
        seat.is_available = True
        db.session.add(seat)

    # Update available tickets in the event
    event = Event.query.get(booking.event_id)
    event.available_tickets = Seat.query.filter_by(event_id=booking.event_id, is_available=True).count()
    db.session.add(event)

    # Extend booking close time if tickets are now available
    if event.available_tickets > 0:
        event.booking_close_time = max(event.booking_close_time, datetime.now() + timedelta(days=1))

    db.session.commit()
    flash("Booking has been canceled and seats are available for booking.", "success")

    # Send cancellation email to the user
    send_cancellation_email(booking.user.email, booking, event)

    return redirect(url_for('booking_management'))

def send_cancellation_email(user_email, booking, event):
    msg = Message('Your Booking Has Been Canceled', recipients=[user_email])
    msg.body = f'Your booking for {event.title} has been canceled.\n' \
               f'Date: {event.start_date.strftime("%Y-%m-%d %H:%M:%S")}\n' \
               f'Canceled Seats: {len(booking.seats)}\n' \
               f'If this was a mistake, please rebook your seats on the event page.\n' \
               f'We hope to see you at another event!'
    mail.send(msg)

@app.route('/update_booking/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def update_booking(booking_id):
    booking = Booking.query.get(booking_id)
    if not booking:
        flash("Booking not found!", "error")
        return redirect(url_for('booking_management'))

    event = Event.query.get(booking.event_id)
    available_seats = Seat.query.filter_by(event_id=event.event_id, is_available=True).all()
    ticket_tiers = TicketTier.query.join(EventTicketTier).filter_by(event_id=event.event_id).all()

    if request.method == 'POST':
        # Retrieve selected seats and ticket tier from the form
        selected_seats = request.form.getlist('selected_seats')  # List of selected seat IDs
        tier_id = request.form.get('tier_id')

        # Mark previously booked seats as available
        for seat in booking.seats:
            seat.is_available = True
            db.session.add(seat)

        # Mark new selected seats as unavailable
        new_seats = Seat.query.filter(Seat.seat_id.in_(selected_seats)).all()
        for seat in new_seats:
            seat.is_available = False
            db.session.add(seat)

        # Update the booking's seats
        booking.seats = new_seats  # Update the booking with new seats
        tier = TicketTier.query.get(tier_id)
        booking.total_amount = len(selected_seats) * tier.price  # Recalculate total price

        db.session.commit()  # Commit changes to the database

        # Send updated booking confirmation email
        send_updated_booking_email(booking.user.email, booking, event)

        flash("Booking updated successfully!", "success")
        return redirect(url_for('booking_management'))

    return render_template('update_booking.html', booking=booking, event=event, available_seats=available_seats, ticket_tiers=ticket_tiers)
def send_updated_booking_email(user_email, booking, event):
    msg = Message('Your Updated Booking Information', recipients=[user_email])
    msg.body = f'Your booking for {event.title} has been updated.\n' \
               f'Date: {event.start_date.strftime("%Y-%m-%d %H:%M:%S")}\n' \
               f'Updated Seats: {len(booking.seats)}\n' \
               f'New Total Amount: ${booking.total_amount}\n' \
               f'We hope you enjoy the event!'
    mail.send(msg)

@app.route('/profile')
@login_required
def profile():
    user_id = session.get('user_id')

    if not user_id:
        flash("User not logged in", "error")
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    payment_details = PaymentDetail.query.filter_by(user_id=user_id).all()

    return render_template('profile.html', user=user, payment_details=payment_details)

@app.route('/print_booking/<int:booking_id>')
def print_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    event = Event.query.get_or_404(booking.event_id)
    buffer = BytesIO()
    qr_data = f"Booking ID: {booking.booking_id}, Event: {event.title}, Date: {event.start_date.strftime('%Y-%m-%d %H:%M:%S')}"
    qr_img = qrcode.make(qr_data)
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
        qr_img.save(temp_file, format='PNG')
        temp_file_path = temp_file.name
    c = canvas.Canvas(buffer, pagesize=letter)
    pdf_title = f"Booking Confirmation - {event.title} on {event.start_date.strftime('%Y-%m-%d')}"
    c.setTitle(pdf_title)
    width, height = letter
    event_date = event.start_date.strftime('%Y-%m-%d %H:%M:%S')
    title = f"{event.title} - {event_date}"
    c.setFont("Helvetica-Bold", 18)
    c.drawString(72, height - 72, title)
    c.setFont("Helvetica", 12)
    c.drawString(72, height - 100, f"Event: {event.title}")
    c.drawString(72, height - 120, f"Date: {event_date}")
    c.drawString(72, height - 140, f"Seats Booked: {len(booking.seats)}")
    c.drawString(72, height - 160, f"Total Amount: ${booking.total_amount}")
    c.drawString(72, height - 180, f"Status: {booking.booking_status}")
    c.drawString(72, 320, "Please, see the QR code attached.")
    c.drawImage(temp_file_path, 72, 100, width=200, height=200)
    c.drawString(72, height - 250, "Thank you for booking with us!")
    c.setFont("Helvetica-Oblique", 10)
    year_text = "2024"
    trademark_text = "Event Booking™"

    year_text_width = c.stringWidth(year_text, "Helvetica-Oblique", 10)
    trademark_text_width = c.stringWidth(trademark_text, "Helvetica-Oblique", 10)
    c.drawString((width - year_text_width) / 2, 50, year_text)
    c.drawString((width - trademark_text_width) / 2, 35, trademark_text)
    c.showPage()
    c.save()
    os.remove(temp_file_path)
    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=booking_{booking_id}.pdf'
    return response


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

    # Query all events from the Event table
    events = Event.query.order_by(Event.start_date.asc()).all()

    return render_template('admin/admin_event_management.html', events=events)

from datetime import datetime, timedelta
from sqlalchemy import func
from flask import jsonify


@app.route('/admin/event_sales/<int:event_id>', methods=['GET'])
def event_sales(event_id):
    start_date = datetime.now() - timedelta(days=30)
    end_date = datetime.now()
    date_range = [(start_date + timedelta(days=i)).date() for i in range((end_date - start_date).days + 1)]
    ticket_sales = (
        db.session.query(
            func.date(Booking.booking_date).label('sale_date'),
            func.count(Ticket.ticket_id).label('tickets_sold'),
            func.sum(Booking.total_amount).label('revenue')
        )
        .join(Ticket, Ticket.booking_id == Booking.booking_id)
        .filter(
            Booking.booking_date >= start_date,
            Ticket.event_id == event_id
        )
        .group_by(func.date(Booking.booking_date))
        .order_by(func.date(Booking.booking_date))
        .all()
    )
    print("Fetched Ticket Sales Data:")
    for sale in ticket_sales:
        print(f"Sale Date: {sale.sale_date}, Tickets Sold: {sale.tickets_sold}, Revenue: {sale.revenue}")
    sales_data = {sale.sale_date: {'tickets_sold': sale.tickets_sold, 'revenue': sale.revenue} for sale in ticket_sales}
    labels = []
    ticket_sales_data = []
    revenue_data = []
    for date in date_range:
        labels.append(date.strftime('%Y-%m-%d'))
        if date in sales_data:
            ticket_sales_data.append(sales_data[date]['tickets_sold'])
            revenue_data.append(sales_data[date]['revenue'])
        else:
            ticket_sales_data.append(0)
            revenue_data.append(0)
    return jsonify({
        'ticket_sales_labels': labels,
        'ticket_sales_data': ticket_sales_data,
        'revenue_data': revenue_data
    })


@app.route('/admin/salesreport', methods=['GET', 'POST'])
def sales_report():
    if not is_admin():
        flash("Unauthorized access!", "error")
        return redirect(url_for('homepage'))

    timeframe = request.args.get('timeframe', '30days')

    if timeframe == '7days':
        start_date = datetime.now() - timedelta(days=7)
    elif timeframe == '30days':
        start_date = datetime.now() - timedelta(days=30)
    elif timeframe == '1year':
        start_date = datetime.now() - timedelta(days=365)
    else:
        start_date = datetime.now() - timedelta(days=30)

    total_tickets_sold = db.session.query(func.count(BookingSeat.seat_id)).join(Booking,
                                                                                BookingSeat.booking_id == Booking.booking_id).filter(
        Booking.booking_status == 'confirmed',
        Booking.booking_date >= start_date
    ).scalar() or 0

    total_revenue = db.session.query(func.sum(Booking.total_amount)).filter(
        Booking.booking_status == 'confirmed',
        Booking.booking_date >= start_date
    ).scalar() or 0
    events = db.session.query(
        Event.event_id,
        Event.title,
        func.count(BookingSeat.seat_id).label('tickets_sold'),
        func.sum(Booking.total_amount).label('revenue')
    ).join(Booking, Booking.event_id == Event.event_id) \
        .join(BookingSeat, BookingSeat.booking_id == Booking.booking_id) \
        .join(Seat, Seat.seat_id == BookingSeat.seat_id) \
        .filter(
        Booking.booking_status == 'confirmed',
        Booking.booking_date >= start_date
    ).group_by(Event.event_id).all()

    event_data = []
    for event in events:
        ticket_sales = db.session.query(
            func.date(Booking.booking_date).label('sale_date'),
            func.count(BookingSeat.seat_id).label('tickets_sold'),
        ).join(BookingSeat, BookingSeat.booking_id == Booking.booking_id).filter(
            Booking.booking_status == 'confirmed',
            Booking.booking_date >= start_date,
            Booking.event_id == event.event_id
        ).group_by(func.date(Booking.booking_date)).order_by(func.date(Booking.booking_date)).all()
        revenue = db.session.query(
            func.date(Booking.booking_date).label('sale_date'),
            func.sum(Booking.total_amount).label('revenue')
        ).filter(
            Booking.booking_status == 'confirmed',
            Booking.booking_date >= start_date,
            Booking.event_id == event.event_id
        ).group_by(func.date(Booking.booking_date)).order_by(func.date(Booking.booking_date)).all()
        labels = [sale.sale_date.strftime('%Y-%m-%d') for sale in ticket_sales]
        ticket_sales_data = [sale.tickets_sold for sale in ticket_sales]
        revenue_data = [rev.revenue for rev in revenue]
        total_tickets_sold_ev = sum(ticket_sales_data)
        total_revenue_ev = sum(revenue_data)

        event_data.append({
            'title': event.title,
            'tickets_sold': total_tickets_sold_ev,
            'revenue': total_revenue_ev or 0,
            'ticket_sales_labels': labels,
            'ticket_sales_data': ticket_sales_data,
            'revenue_data': revenue_data,
        })

    ticket_sales = db.session.query(
        func.date(Booking.booking_date).label('sale_date'),
        func.count(BookingSeat.seat_id).label('tickets_sold'),
        func.sum(Booking.total_amount).label('total_revenue')
    ).outerjoin(BookingSeat, BookingSeat.booking_id == Booking.booking_id).filter(
        Booking.booking_status == 'confirmed',
        Booking.booking_date >= start_date
    ).group_by(func.date(Booking.booking_date)).order_by(func.date(Booking.booking_date)).all()
    sales_data = {
        sale.sale_date.strftime('%Y-%m-%d'): {
            'tickets_sold': sale.tickets_sold,
            'total_revenue': sale.total_revenue
        } for sale in ticket_sales
    }
    labels = sorted(sales_data.keys())
    tickets_sold_data = [sales_data[label]['tickets_sold'] for label in labels]
    revenue_data = [sales_data[label]['total_revenue'] for label in labels]
    print(sales_data)

    return render_template('admin/admin_sales_report.html',
                           selected_timeframe=timeframe,
                           total_tickets_sold=total_tickets_sold,
                           total_revenue=total_revenue,
                           events=event_data,
                           tickets_sold_chart_labels=labels,
                           tickets_sold_chart_data=tickets_sold_data,
                           revenue_chart_labels=labels,
                           revenue_chart_data=revenue_data)

@app.route('/admin/events/new', methods=['GET', 'POST'])
def create_event():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        venue = request.form.get('venue')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        # Get booking open and close times from the form
        booking_open_time = request.form.get('booking_open_time')
        booking_close_time = request.form.get('booking_close_time')

        # Ensure datetime fields are parsed correctly
        start_date = datetime.strptime(start_date, '%Y-%m-%dT%H:%M')
        end_date = datetime.strptime(end_date, '%Y-%m-%dT%H:%M')
        booking_open_time = datetime.strptime(booking_open_time, '%Y-%m-%dT%H:%M')
        booking_close_time = datetime.strptime(booking_close_time, '%Y-%m-%dT%H:%M')

        ticket_tiers = request.form.getlist('ticket_tiers[]')
        tier_prices = request.form.getlist('tier_prices[]')
        tier_seat_counts = request.form.getlist('tier_seat_counts[]')

        try:
            tier_seat_counts = [int(count) for count in tier_seat_counts if count]
            total_tickets = sum(tier_seat_counts)
        except ValueError:
            flash("Please provide a valid seat count for each tier.", "error")
            return render_template('admin/create_event.html')

        try:
            # Step 1: Create the new event
            new_event = Event(
                title=title,
                description=description,
                venue=venue,
                start_date=start_date,
                end_date=end_date,
                total_tickets=total_tickets,
                available_tickets=total_tickets,
                booking_open_time=booking_open_time,
                booking_close_time=booking_close_time
            )
            db.session.add(new_event)
            db.session.flush()

            # Step 2: Define ticket tiers and associate seats with each tier
            assigned_seat_count = 0  # Track seat assignment across tiers

            for tier_name, tier_price, tier_seat_count in zip(ticket_tiers, tier_prices, tier_seat_counts):
                # Ensure tier_seat_count is an integer
                tier_seat_count = int(tier_seat_count)

                # Create or find the ticket tier
                ticket_tier = TicketTier.query.filter_by(tier_name=tier_name).first()
                if not ticket_tier:
                    ticket_tier = TicketTier(tier_name=tier_name, price=tier_price)
                    db.session.add(ticket_tier)
                    db.session.flush()

                # Link the ticket tier to the event with the count of tickets for that tier
                event_ticket_tier = EventTicketTier(
                    event_id=new_event.event_id,
                    tier_id=ticket_tier.tier_id,
                    total_tickets=tier_seat_count
                )
                db.session.add(event_ticket_tier)

                # Create seats for this specific tier
                seats = []
                for _ in range(tier_seat_count):
                    assigned_seat_count += 1
                    seat_number = f"{chr(64 + (assigned_seat_count - 1) // 10 + 1)}{assigned_seat_count % 10 if assigned_seat_count % 10 != 0 else 10}"
                    seat = Seat(event_id=new_event.event_id, seat_number=seat_number, is_available=True, tier_id=ticket_tier.tier_id)
                    seats.append(seat)
                db.session.bulk_save_objects(seats)

            # Commit all changes
            db.session.commit()
            flash("Event created successfully!", "success")
            return redirect(url_for('admin_events'))

        except Exception as e:
            db.session.rollback()
            flash(f"Error creating event: {str(e)}", "error")

    return render_template('admin/create_event.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    flash("You have been logged out.", "success")
    return redirect(url_for('homepage'))


if __name__ == '__main__':
    app.run(debug=True)
