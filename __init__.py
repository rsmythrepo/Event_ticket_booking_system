"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = "secret_key"

# Check environment and set database URI accordingly
if os.getenv("FLASK_ENV") == "testing":
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/test_event_bookings'
    app.config['TESTING'] = True
else:
    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("DB_PASSWORD", "root")
    db_host = os.getenv("DB_HOST", "localhost")  # Use "mysql-db" for Docker
    db_name = os.getenv("DB_NAME", "event_bookings")

    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:3306/{db_name}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.secret_key = "secret_key"

    # Check environment and set database URI accordingly
    if os.getenv("FLASK_ENV") == "testing":
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost/test_event_bookings'
        app.config['TESTING'] = True
    else:
        db_user = os.getenv("DB_USER", "root")
        db_password = os.getenv("DB_PASSWORD", "root")
        db_host = os.getenv("DB_HOST", "localhost")  # Use "mysql-db" for Docker
        db_name = os.getenv("DB_NAME", "event_bookings")

        app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:3306/{db_name}'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['SESSION_TYPE'] = 'filesystem'  # Use filesystem to persist data across server restarts
    Session(app)
    # Configure Flask-Mail
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USERNAME'] = 'askhatabi@gmail.com'  # Replace with your email
    app.config['MAIL_PASSWORD'] = 'pyegxiaboyccgymm'  # Replace with your password or App Password
    app.config['MAIL_DEFAULT_SENDER'] = ('Booking System', 'askhatabi@gmail.com')  # The sender name and email

    # Initialize extensions
    db.init_app(app)

    return app
