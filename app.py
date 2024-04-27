from flask import Flask, render_template,url_for,session,request,redirect
from flask_sqlalchemy import SQLAlchemy
import bcrypt 
from database import Database
import matplotlib.pyplot as plt


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Database.db'
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = '1234'


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_type = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    date_of_birth = db.Column(db.String(20), nullable=True)
    password = db.Column(db.String(120), nullable=False)

    def __init__(self,user_type, email, name, password):
        self.email = email
        self.user_type = user_type
        self.name = name
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')



    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

with app.app_context():
    db.create_all()





@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
            query = request.form['search']
            search = "/search/"+query
            return redirect(search)
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = Users.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if user.user_type == 'ADMIN':
                session['name'] = user.name
                session['user_type'] = user.user_type
                session['id'] = user.id
                return redirect(url_for('admin_dashboard'))
            elif user.user_type == 'USER':
                session['name'] = user.name
                session['id'] = user.id
                return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid email or password')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        password = request.form['password']
        repass = request.form['repass']
        if password != repass:
            return render_template('register.html', error='Passwords do not match')
        elif Users.query.filter_by(email=email).first():
            return render_template('register.html', error='Email already exists')
        elif password == repass:
            new_user = Users('USER',email, name, password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('name', None)
    session.pop('id', None)
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'name' in session:
        user = Users.query.get(session['id'])
        Issued = Database.getIssuedBooks(session['id'])
        requested = Database.getRequests_user(session['id'])
        if request.method == 'POST':
            query = request.form['search']
            search = "/search/"+query
            return redirect(search)
        return render_template('dashboard.html', issued = Issued, requested = requested, user=user)
    else:
        return redirect(url_for('login'))

@app.route('/request/book=<bk_id>,<bk_name>')
def request_book(bk_id,bk_name):
    usr_id = session['id']
    usr_name = session['name']
    Database.addRequest(usr_id, usr_name, bk_id, bk_name)
    return redirect(url_for('dashboard'))

@app.route('/cancel/book=<bk_id>')
def cancel_request(bk_id):
    Database.deleteRequest(bk_id, session['id'])
    return redirect(url_for('dashboard'))

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'name' in session:
        sections = Database.getSections()
        return render_template('admin_dashboard.html', sections=sections)
    else:
        return redirect(url_for('login'))


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'name' in session:
        user = Users.query.get(session['id'])
        if request.method == 'POST':
            name = request.form['name']
            phone = request.form['phone']
            gender = request.form['gender']
            dob = request.form['dob']
            user.name = name
            user.phone = phone
            user.gender = gender
            user.date_of_birth = dob
            db.session.commit()
            if user.user_type == 'ADMIN':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard'))
        return render_template('profile.html', user=user)
    else:
        return redirect(url_for('login'))
    
@app.route('/books', methods=['GET', 'POST'])
def books():
    if 'name' in session:
        user = Users.query.get(session['id'])
        sections = Database.getSectionsU()
        books = Database.getBooksU()
        requested = Database.getRequests_user(session['id'])
        issued = Database.getIssuedBooks(session['id'])
        unbooks = []
        if request.method == 'POST':
            query = request.form['search']
            search = "/search/"+query
            return redirect(search)
        for i in books:
            if i not in issued and i not in requested:
                unbooks.append(i)
        return render_template('books.html', sections=sections, books=unbooks)
    else:
        return redirect(url_for('login'))
    

@app.route('/data', methods=['GET', 'POST'])
def data():
    if 'name' in session:
        user = Users.query.get(session['id'])
        sections = Database.getSectionTitles()
        count = Database.userBookCount(session['id'])
        plt.pie(count, labels=sections, autopct='%1.1f%%')
        plt.savefig('static\images\pie.png')
        if request.method == 'POST':
            query = request.form['search']
            search = "/search/"+query
            return redirect(search)
        return render_template('stats.html',url = 'static\images\pie.png' )
    else:
        return redirect(url_for('login'))

@app.route('/Requests')
def requests():
    if 'name' in session:
        user = Users.query.get(session['id'])
        requests = Database.getRequests()
        return render_template('requests.html', requests=requests)
    else:
        return redirect(url_for('login'))
    
@app.route('/grant/<usr_id>/<usr_name>/<book_id>/<book_name>')
def grant(usr_id, book_id, usr_name, book_name):
    Database.issueBook(usr_id, usr_name, book_id, book_name)
    Database.deleteRequest(book_id, usr_id)
    return redirect(url_for('requests'))

@app.route('/deny/<book_id>/<user_id>')
def deny_book(book_id, user_id):
    Database.deleteRequest(book_id, user_id)
    return redirect(url_for('requests'))

@app.route('/add_section', methods=['GET', 'POST'])
def add_section():
    if 'name' in session:
        user = Users.query.get(session['id'])
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            title = title.upper()
            Database.addSection(title, description)
            return redirect(url_for('admin_dashboard'))
        return render_template('add_section.html', user=user)
    else:
        return redirect(url_for('login'))
    
@app.route('/delete_section/id=<id>')
def delete_section(id):
    Database.deleteSection(id)
    return redirect(url_for('admin_dashboard'))

@app.route('/section/id=<id>/edit', methods=['GET', 'POST'])
def edit_section(id):
    if 'name' in session:
        user = Users.query.get(session['id'])
        section = Database.getSection(id)
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            title = title.upper()
            Database.updateSection(id, title, description)
            return redirect(url_for('admin_dashboard'))
        return render_template('edit_section.html', section=section)
    else:
        return redirect(url_for('login'))


@app.route('/section/id=<id>/add_book', methods=['GET', 'POST'])
def add_book(id):
    if 'name' in session:
        user = Users.query.get(session['id'])
        section = Database.getSection(id)
        if request.method == 'POST':
            title = request.form['title']
            author = request.form['author']
            description = request.form['description']
            content = request.form['content']
            title = title.upper()
            section_id = section[0]
            Database.addBook(title, author, description, section_id, content)
            return redirect(url_for('admin_dashboard'))
        return render_template('add_book.html',section_name = section[1])
    else:
        return redirect(url_for('login'))


@app.route('/delete_book/id=<id>')
def delete_book(id):
    Database.deleteBook(id)
    return redirect(url_for('admin_dashboard'))

@app.route('/book/id=<id>',methods=['GET', 'POST'])
def book(id):
    if 'name' in session:
        user = Users.query.get(session['id'])
        book = Database.getBook(id)
        if request.method == 'POST':
            title = request.form['title']
            author = request.form['author']
            description = request.form['description']
            content = request.form['content']
            title = title.upper()
            Database.updateBook(id, title, author, description, content)
            return redirect("/section/id=",book[4])
        return render_template('bookdetails.html', book=book)
    else:
        return redirect(url_for('login'))

@app.route('/section/id=<id>', methods=['GET', 'POST'])
def section(id):
    if 'name' in session:
        user = Users.query.get(session['id'])
        books = Database.getBooks(id)
        section = Database.getSection(id)
        if request.method == 'POST':
            query = request.form['search']
            search = "/search/"+query
            return redirect(search)
        return render_template('section.html', books=books,section = section)
    else:
        return redirect(url_for('login'))
    
@app.route('/read/book=<id>', methods=['GET', 'POST'])
def read(id):   
    if 'name' in session:
        user = Users.query.get(session['id'])
        book = Database.getBook(id)
        if request.method == 'POST':
            query = request.form['search']
            search = "/search/"+query
            return redirect(search)
        return render_template('read.html', book=book)
    else:
        return redirect(url_for('login'))

@app.route('/return/book=<bk_id>/user=<usr_id>')
def return_book(bk_id, usr_id):
    Database.returnBook(bk_id, usr_id)
    return redirect(url_for('dashboard'))


@app.route('/revoke/book=<bk_id>/user=<usr_id>')
def revoke_book(bk_id, usr_id):
    Database.returnBook(bk_id, usr_id)
    return redirect(url_for('issuedBooks'))

@app.route('/books/sec_id=<id>', methods=['GET', 'POST'])
def books_sec(id):
        if 'name' in session:
            user = Users.query.get(session['id'])
            books = Database.getBooks(id)
            if request.method == 'POST':
                query = request.form['search']
                search = "/search/"+query
                return redirect(search)
            return render_template('books_sec.html', books=books)
        else:
            return redirect(url_for('login'))

@app.route('/search/<query>')
def search(query):
    if 'name' in session:
        user = Users.query.get(session['id'])
        sections = Database.searchSections(query)
        books = Database.searchBooks(query)
        return render_template('search.html',sections=sections, books=books, user=user) 
    else:
        return redirect(url_for('login'))

@app.route('/issuedBooks')
def issuedBooks():
    if 'name' in session:
        books = Database.getAllIssuedBooks()
        return render_template('issuedBooks.html', issued=books)
    else:
        return redirect(url_for('login'))
    
@app.route('/adminStats')
def adminStats():
    if 'name' in session:
        users = Database.getAllUsers()
        sections = Database.getSectionTitles()
        count = Database.bookCount()
        plt.pie(count, labels=sections, autopct='%1.1f%%')
        plt.savefig('static/images/apie.png')
        return render_template('admin_stats.html', users=users)
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=10000)
