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