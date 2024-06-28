from datetime import date
import enum
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from sqlalchemy import create_engine, MetaData, Table
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
CORS(app) 
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['JWT_SECRET_KEY'] = 'jwt_secret_key_here'

db = SQLAlchemy(app)
jwt = JWTManager(app)

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
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    loans = db.relationship('Loan', backref='customer', lazy=True)

    def __init__(self, username, password, name, city, age):
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.name = name
        self.city = city
        self.age = age
        
    
class Loan(db.Model):
    __tablename__ = 'loans'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    loan_date = db.Column(db.Date, default=date.today, nullable=False)
    return_date = db.Column(db.Date, nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)

@app.route('/register', methods=['POST'])
def create_new_user():
    data = request.get_json()
    name = data.get('name')
    city = data.get('city')
    age = data.get('age')


def admin_user_creation():
    admin_password = generate_password_hash('admin')
    admin_user = Customer(username = "admin", password = "admin", name="admin", city='AdminCity', age=0)
    db.session.add(admin_user)
    db.session.commit()

# @app.route('/', methods=['GET'])
# def direct_to_login_page():
#     return "BUssiness"

# @app.route('/register', methods=['GET'])
# def direct_to_register_page():
#     return "Hello world"

# def delete_customer_table():
#     DATABASE_URI = 'sqlite:///library.db'  # Replace with your actual database URI
#     engine = create_engine(DATABASE_URI)
#     metadata = MetaData()
#     table_name = 'your_table_name'
#     table_to_delete = Table(table_name, metadata, autoload_with=engine)
#     table_to_delete.drop(engine)

if __name__ == '__main__':
    with app.app_context():
        if(not all_tables_created):
            db.create_all()         
        if(not admin_user_created):
            admin_user_creation()  
        # delete_customer_table()  
    app.run(debug=True)

