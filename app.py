from datetime import date, datetime, timedelta
import enum
import os
from flask import Flask, render_template, request, jsonify, send_from_directory, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from sqlalchemy import create_engine, MetaData, Table, Integer, Enum
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from werkzeug.security import generate_password_hash, check_password_hash
#from flask_uploads import UploadSet, configure_uploads


app = Flask(__name__)
CORS(app) 
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['JWT_SECRET_KEY'] = 'jwt_secret_key_here'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 2400
app.config['UPLOADED_PHOTOS_DEST'] = 'media'

db = SQLAlchemy(app)
jwt = JWTManager(app)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'media')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

admin_user_created = True
all_tables_created = True

class BookType(enum.Enum):
    TYPE_1 = 10  
    TYPE_2 = 5   
    TYPE_3 = 2

class BookStatus(enum.Enum):
     AVAILABLE = "available"
     LOANED = "loaned"
     ERASED = "erased"

class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    year_published = db.Column(db.Integer, nullable=False)
    borrow_time = db.Column(Enum(BookType), nullable = False)
    filename = db.Column(db.String(255), nullable=False)
    status = db.Column(Enum(BookStatus), default = "available", nullable = False)

    def __init__(self, name, author, year_published, borrow_time, filename,exist=True,status="available"):
        self.name = name
        self.author = author
        self.year_published = year_published
        self.borrow_time = borrow_time
        self.filename = filename
        self.exist = exist
        self.status= status

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

    def __init__(self, username, password_hash, name, city, age):
        self.username = username
        self.password_hash = password_hash
        self.name = name
        self.city = city
        self.age = age
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
      
class Loan(db.Model):
    __tablename__ = 'loans'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    loan_date = db.Column(db.Date, default=date.today, nullable=False)
    return_date = db.Column(db.Date, nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)

@app.route('/register', methods=['POST', 'GET'])
def create_new_user():
    if  request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        name = data.get('name')
        city = data.get('city')
        age = data.get('age')

        if Customer.query.filter_by(username=username).first():
            return jsonify({'message': 'Username already exists'}), 400
        password_hash = generate_password_hash(password) 
        new_user = Customer(username=username, password_hash=password_hash, name=name, city=city,age=age)
        db.session.add(new_user)
        db.session.commit()

    return jsonify({'message': 'Registered successfully'}), 201

@app.route('/login', methods=['POST', 'GET'])
def login_to_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    customer = Customer.query.filter_by(username=username).first()

    if not customer or not check_password_hash(customer.password_hash, password): #123 after encript = to scrypt:32768:8:1$rmqHNat7nzuoXlrr$91d9cc8e2c03f57be624ce3d273b02f77772a0a3dfbdf025927550f86724dd3b2a0e047ecc12480c62aeabb66d14d6cc81519c335cca5d73cf8563e4b1516af0
            return jsonify({'message': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=username) # create new token
    return jsonify({'access_token': access_token}), 200

@app.route('/add_book', methods=['POST', 'GET'])
@jwt_required()
def add_book(): 
    # Only user can perform this action 
    current_user = get_jwt_identity()
    # print(current_user)
    if current_user != "admin":
        return jsonify({"msg": "Admin access required"}), 403
    #extract the data from the request
    name = request.form.get('name')
    author = request.form.get('author')
    year_published = request.form.get('year_published')
    borrow_time = request.form.get('borrow_time')
    # print(borrow_time)
    exist = request.form.get('exist')
    isloaned = request.form.get('isloaned')
    file = request.files['filename'] # Path to the image
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400
    
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    new_book = Book(name=name, author=author, year_published=year_published,borrow_time=borrow_time,filename=filename,
                    exist=exist,isloaned=isloaned)
    
    db.session.add(new_book)
    db.session.commit()

    return jsonify({
    'message': 'File uploaded successfully',
}), 200

@app.route('/display_books', methods=['GET'])
@jwt_required()
def show_books():
    current_user = get_jwt_identity()
    book_list = []
    if current_user == "admin":
        books = Book.query.all()
        for book in books:   
            book_dic = {
            'name' : book.name,
            'author': book.author,
            'year_published': book.year_published,
            'borrow_time': BookType(book.borrow_time).name,
            'filename': book.filename,
            'exist': book.exist,
            'isloaned': book.isloaned
            }
            book_list.append(book_dic)
        
    return jsonify(book_list)

@app.route('/display_customers', methods=['GET'])
@jwt_required()
def show_customers():
    current_user = get_jwt_identity()
    customers_list = []
    if (current_user != "admin"):
        return jsonify({"message":"Only admin is permitted"})
    customers = db.session.query(Customer).filter(Customer.id != 1).all()
    for customer in customers:
        customer_dict = {
            'username' : customer.username,
            'name' : customer.name,
            'city' : customer.city,
            'age' : customer.age,
            'status' : customer.active
        }
        customers_list.append(customer_dict)
    return jsonify(customers_list)

@app.route('/loan_book', methods=['GET', 'POST'])
@jwt_required()
def loan_book():
    current_user = get_jwt_identity()
    #current_user_id = current_user.id
    if current_user == "admin":
        return jsonify({"msg": "Only regular user can borrow"}), 403
    print("BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB")
    data = request.get_json()
    customerId = data.get('customerId')
    bookId = data.get('bookId')
    loan_date = date.today()
    the_book = db.session.query(Book).filter(Book.id == bookId).first()
    print(the_book)
    the_book_borrow_time = the_book.borrow_time
    return_date = loan_date + timedelta(days=10)
    print(current_user, return_date)

    



@app.route('/', methods=['GET'])
def direct_to_login_page():
    return "MY RESPONSE"


def admin_user_creation():
    admin_password = generate_password_hash('admin')
    admin_user = Customer(username = "admin", password_hash= admin_password, name="admin", city='AdminCity', age=0)
    db.session.add(admin_user)
    db.session.commit()


def delete_books_table():
    DATABASE_URI = 'sqlite:///instance/library.db'  # Replace with your actual database URI
    engine = create_engine(DATABASE_URI)
    metadata = MetaData()
    table_name = 'books'
    table_to_delete = Table(table_name, metadata, autoload_with=engine)
    table_to_delete.drop(engine)

def change_table_name():
    engine = create_engine('sqlite:///instance/library.db')
    connection = engine.raw_connection()
    cursor = connection.cursor()
    cursor.execute('DROP TABLE books;')
    connection.commit()
    cursor.close()
    connection.close()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # change_table_name()
        #delete_books_table()         
        #admin_user_creation() 
    app.run(debug=True)

