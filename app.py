# For connecting to mysql locally
import mysql.connector
from flask import Flask
from config import Config
#-----------------------------------------

from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = "secret_key"

# For connecting to mysql locally
#-------------------------------------------------------
app.config.from_object(Config)
app.config['SECRET_KEY'] = 'secret_key'  # Add secret key here

# Initialize MySQL connection
def connect_db():
    return mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )
#--------------------------------------------------------

bookings = []
users = []
admins = []

@app.route('/')
def homepage():
    conn = connect_db()
    cur = conn.cursor(dictionary=True)

    # Fetch events ordered by start_date in descending order
    cur.execute("SELECT * FROM event ORDER BY start_date ASC")
    events = cur.fetchall()
    cur.close()
    conn.close()

    # Pass the events to the template
    return render_template('home.html', events=events)

@app.route('/event/<int:event_id>')
def event_details(event_id):
    conn = connect_db()
    cur = conn.cursor(dictionary=True)

    # Fetch the event by event_id
    cur.execute("SELECT * FROM event WHERE event_id = %s", (event_id,))
    event = cur.fetchone()

    cur.close()
    conn.close()

    if not event:
        flash("Event not found!", "error")
        return redirect(url_for('homepage'))

    return render_template('event_details.html', event=event)


@app.route('/bookevent/<int:event_id>', methods=['GET', 'POST'])
def book_event(event_id):
    event = next((e for e in events if e['id'] == event_id), None)
    if not event:
        flash("Event not found!", "error")
        return redirect(url_for('homepage'))

    if request.method == 'POST':
        user = "user123"  # Simulating a logged-in user
        seat_count = int(request.form['seat_count'])

        if event['available_seats'] >= seat_count:
            event['available_seats'] -= seat_count
            bookings.append({
                'user': user,
                'event_id': event_id,
                'seats': seat_count,
                'status': 'Confirmed'
            })
            flash("Booking successful!", "success")
        else:
            flash("Not enough seats available.", "error")

        return redirect(url_for('my_bookings'))

    return render_template('event_details.html', event=event)


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
