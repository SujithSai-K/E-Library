import sqlite3
from datetime import date

class Database:
    
    def updateUser(id, name, phone, gender, dob):
        conn = sqlite3.connect('instance\Database.db')
        c = conn.cursor()
        c.execute("UPDATE users SET name=?, phone=?, gender=?, dob=? WHERE user_id=?", (name, phone, gender, dob, id))
        conn.commit()
        conn.close()

    def addSection(section_name, section_description):
        conn = sqlite3.connect('instance\Database.db')
        c = conn.cursor()
        section_date = date.today()
        c.execute("CREATE TABLE IF NOT EXISTS sections (section_id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT, date TEXT)")
        c.execute("INSERT INTO sections (title, description, date) VALUES (?, ?, ?)", (section_name, section_description, section_date))
        conn.commit()
        conn.close()
    
    def deleteSection(id):
        conn = sqlite3.connect('instance\Database.db')
        c = conn.cursor()
        c.execute("DELETE FROM sections WHERE section_id=?", (id, ))
        conn.commit()
        conn.close()

    def updateSection(id, title, description):
        conn = sqlite3.connect('instance\Database.db')
        c = conn.cursor()
        c.execute("UPDATE sections SET title=?, description=? WHERE Section_id=?", (title, description, id))
        conn.commit()
        conn.close()

    def getSections():
        conn = sqlite3.connect('instance\Database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM sections")
        sections = c.fetchall()
        conn.close()
        return sections
    
    def getSectionsU():
        conn = sqlite3.connect('instance\Database.db')
        c = conn.cursor()
        c.execute("SELECT section_id, title, description FROM sections")
        sections = c.fetchall()
        conn.close()
        return sections

    def getSection(id):
        conn = sqlite3.connect('instance\Database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM sections WHERE section_id=?", (id,))
        section = c.fetchone()
        conn.close()
        return section
    
    def addBook(title, author, description, section_id, link):
        conn = sqlite3.connect('instance\Database.db')
        c = conn.cursor()
        book_date = date.today()
        c.execute("CREATE TABLE IF NOT EXISTS books (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, author TEXT, description TEXT, section_id INTEGER, date TEXT, context text, foreign key(section_id) references sections(section_id))")
        c.execute("INSERT INTO books (title, author, description, section_id, date, context) VALUES (?, ?, ?, ?, ?, ?)", (title, author, description, section_id, book_date, link))
        conn.commit()
        conn.close()
    
    def updateBook(id, title, author, description, content):
        conn = sqlite3.connect('instance\Database.db')
        c = conn.cursor()
        c.execute("UPDATE books SET title=?, author=?, description=?, context=? WHERE id=?", (title, author, description, content, id))
        conn.commit()
        conn.close()

    def deleteBook(id):
        conn = sqlite3.connect('instance\Database.db')
        c = conn.cursor()
        c.execute("DELETE FROM books WHERE id=?", (id,))
        conn.commit()
        conn.close()
    
    def getBooks(sec_id):
        conn = sqlite3.connect('instance\Database.db')
        c = conn.cursor()
        c.execute("SELECT id, title, author, description, date FROM books WHERE section_id=?", (sec_id,)) 
        books = c.fetchall()
        conn.close()
        return books
    
    def getBook(id):
        conn = sqlite3.connect('instance\Database.db') 
        c = conn.cursor()
        c.execute("SELECT * FROM books WHERE id=?", (id,))
        book = c.fetchone()
        conn.close()
        return book
    
    def getBooksU():
        conn = sqlite3.connect('instance\Database.db')
        c = conn.cursor()
        c.execute("SELECT id, title, author, description FROM books")
        book = c.fetchall()
        conn.close()
        return book

    def addRequest(user_id, user_name,  book_id, book_name):
        conn = sqlite3.connect('instance\Database.db')
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS requests (user_id INTEGER, user_name TEXT, book_id INTEGER, book_name TEXT, date TEXT, foreign key(user_id) references users(user_id), foreign key(book_id) references books(book_id))")
        request_date = date.today()
        c.execute("INSERT INTO requests (user_id, user_name, book_id, book_name, date) VALUES (?, ?, ?, ?, ?)", (user_id, user_name, book_id, book_name, request_date))
        conn.commit()
        conn.close()
    
    def getRequests():
        conn = sqlite3.connect('instance\Database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM requests")
        requests = c.fetchall()
        conn.close()
        return requests
    
    def getRequests_user(user_id):
        conn = sqlite3.connect('instance\Database.db')
        c = conn.cursor()
        c.execute("""SELECT books.id, books.title, books.author, books.description FROM users JOIN requests ON users.id = requests.user_id JOIN books ON requests.book_id = books.id WHERE users.id = ?; """, (user_id,))
        requests = c.fetchall()
        conn.close()
        return requests
    
    def deleteRequest(book_id, usr_id):
        conn = sqlite3.connect('instance\Database.db')
        c = conn.cursor()
        c.execute("DELETE FROM requests WHERE user_id=? and book_id=?", (usr_id,book_id))
        conn.commit()
        conn.close()

    def issueBook(user_id, user_name,book_id,book_name):
        conn = sqlite3.connect('instance\Database.db')
        c = conn.cursor()
        c.execute("create table if not exists BookRegister (book_id integer, book_name TEXT, user_id integer, user_name TEXT, Issued_Date TEXT, return_date Text nullable, foreign key(book_id) references books(book_id), foreign key(user_id) references users(user_id))")
        issued_date = date.today()
        c.execute("INSERT INTO BookRegister (book_id,book_name, user_id,user_name, Issued_Date) VALUES (?, ?, ?, ?, ?)", (book_id,book_name, user_id,user_name, issued_date)) 
        conn.commit()
        conn.close()

    def getIssuedBooks(user_id):
        conn = sqlite3.connect('instance\Database.db')
        c = conn.cursor()
        c.execute("""SELECT books.id, books.title, books.author, books.description FROM bookregister join books on bookregister.book_id = books.id WHERE bookregister.user_id = ? AND bookregister.return_date IS NULL; """, (user_id,))
        books = c.fetchall()
        conn.close()
        return books

    def  getAllIssuedBooks():
        conn = sqlite3.connect('instance\Database.db')
        c = conn.cursor()
        c.execute("""SELECT book_id, book_name, user_id, user_name, Issued_Date FROM bookregister WHERE return_date IS NULL;""")
        books = c.fetchall()
        conn.close()
        return books

    def returnBook(book_id,user_id):
        conn = sqlite3.connect('instance\Database.db')
        c = conn.cursor()
        return_date = date.today()
        c.execute("update BookRegister set return_date = ? where book_id = ? and user_id = ?",(return_date, book_id, user_id))
        conn.commit()
        conn.close()

    def searchBooks(query):
        conn = sqlite3.connect('instance\Database.db')
        c = conn.cursor()
        c.execute("SELECT id, title, author, description FROM books WHERE title LIKE ?", ('%'+query+'%',))
        books = c.fetchall()
        conn.close()
        return books
    
    def searchSections(query):
        conn = sqlite3.connect('instance\Database.db')
        c = conn.cursor()
        c.execute("SELECT section_id,title, description FROM sections WHERE title LIKE ?", ('%'+query+'%', ))
        sections = c.fetchall()
        conn.close()
        return sections
    
    def getSectionTitles():
        conn = sqlite3.connect('instance\Database.db')
        c = conn.cursor()
        c.execute("SELECT title FROM sections order by title")
        titles = c.fetchall()
        conn.close()
        names = [i[0] for i in titles]
        return names
    
    def userBookCount(user_id):
        conn = sqlite3.connect('instance\Database.db')
        c = conn.cursor()
        c.execute("""SELECT  COUNT(br.book_id) AS book_count
        FROM sections AS s
        LEFT JOIN books AS b ON s.section_id = b.section_id
        LEFT JOIN BookRegister AS br ON b.id = br.book_id
        WHERE br.user_id = ?
        GROUP BY s.section_id, s.title
        ORDER BY s.title;""",(user_id,))
        books = c.fetchall()
        conn.close()
        count = []
        for i in books:
            count.append(i[0])
        return count
    
    def bookCount():
        conn = sqlite3.connect('instance\Database.db')
        c = conn.cursor()
        c.execute("""SELECT  COUNT(br.book_id) AS book_count
        FROM sections AS s
        LEFT JOIN books AS b ON s.section_id = b.section_id
        LEFT JOIN BookRegister AS br ON b.id = br.book_id
        GROUP BY s.section_id, s.title
        ORDER BY s.title;""")  
        books = c.fetchall()
        count = []
        for i in books:
            count.append(i[0])
        conn.close()
        return count
    
    def getAllUsers():
        conn = sqlite3.connect('instance\Database.db')
        c = conn.cursor()
        c.execute("""SELECT u.id, u.name, u.gender, u.date_of_birth, COUNT(br.book_id) AS books_read FROM users AS u LEFT JOIN BookRegister AS br ON u.id = br.user_id WHERE u.user_type != 'ADMIN' GROUP BY u.id, u.name, u.gender, u.date_of_birth;""")
        users = c.fetchall()
        conn.close()
        return users