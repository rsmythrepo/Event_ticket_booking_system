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
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/event_bookings'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)