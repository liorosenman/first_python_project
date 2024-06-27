from datetime import date
import enum
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
CORS(app)  # Enable CORS for all routes

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'media')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

admin_user_created = True
all_tables_created = True

class BookType(enum.Enum):
    TEN_DAYS = 1
    FIVE_DAYS = 2
    TWO_DAYS = 3

class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    year_published = db.Column(db.Date, nullable=False)
    type = db.Column(db.Integer, nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    exist = db.Column(db.Boolean, default=True, nullable=False)

    def __init__(self, name, author, year_published, type, filename, exist=True):
        self.name = name
        self.author = author
        self.year_published = year_published
        self.type = type
        self.filename = filename
        self.exist = exist

class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    loans = db.relationship('Loan', backref='customer', lazy=True)

    def __init__(self, password, name, city, age):
        self.name = name
        self.city = city
        self.age = age
        self.password_hash = generate_password_hash(password)
        
    
class Loan(db.Model):
    __tablename__ = 'loans'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    loan_date = db.Column(db.Date, default=date.today, nullable=False)
    return_date = db.Column(db.Date, nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)

@app.route('/', methods=['POST'])
def direct_to_login_page():


def admin_user_creation():
    admin_password = generate_password_hash('admin')
    admin_user = Customer(id=1, password_hash = "admin", name="admin", city='AdminCity', age=0)
    db.session.add(admin_user)
    db.session.commit()

# @app.route('/', methods=['GET'])
# def direct_to_login_page():
#     return "BUssiness"

# @app.route('/register', methods=['GET'])
# def direct_to_register_page():
#     return "Hello world"

if __name__ == '__main__':
    with app.app_context():
        if(not all_tables_created):
            db.create_all()         
        if(not admin_user_created):
            admin_user_creation()    
    app.run(debug=True)

