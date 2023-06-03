from flask import Flask,flash, render_template, request, redirect,url_for
import pymysql

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'nelson'
app.config['MYSQL_PASSWORD'] = '12'
app.config['MYSQL_DB'] = 'library'

app.secret_key = 'smdfkhdfher#@#'

db = pymysql.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    password=app.config['MYSQL_PASSWORD'],
    db=app.config['MYSQL_DB']
)

# Home page
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/books/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        stock = request.form['stock']
        cursor = db.cursor()
        cursor.execute("INSERT INTO books (title, author, stock) VALUES (%s, %s, %s)", (title, author, stock))
        db.commit()
        cursor.close()
        return redirect('/books')
    return render_template('add_book.html')


@app.route('/books')
def list_books():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    cursor.close()
    return render_template('list_books.html', books=books)

@app.route('/books/update/<string:book_id>', methods=['GET', 'POST'])
def update_book(book_id):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM books WHERE id = %s", (book_id))
    book = cursor.fetchone()

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        stock = request.form['stock']
        cursor.execute("UPDATE books SET title = %s, author = %s, stock = %s WHERE id = %s", (title, author, stock, book_id))
        db.commit()
        cursor.close()
        return redirect('/books')

    cursor.close()
    return render_template('update_book.html', book=book)

# Route for deleting a book
@app.route('/books/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
    db.commit()
    cursor.close()
    return redirect('/books')

@app.route('/members')
def list_members():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM members")
    members = cursor.fetchall()
    cursor.close()
    return render_template('list_members.html', members=members)

# Route for adding a member
@app.route('/members/add', methods=['GET', 'POST'])
def add_member():
    if request.method == 'POST':
        name = request.form['name']
        cursor = db.cursor()
        cursor.execute("INSERT INTO members (name) VALUES (%s)", (name,))
        db.commit()
        cursor.close()
        return redirect('/members')
    return render_template('add_member.html')

# Route for updating a member
@app.route('/members/update/<int:member_id>', methods=['GET', 'POST'])
def update_member(member_id):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM members WHERE id = %s", (member_id,))
    member = cursor.fetchone()

    if request.method == 'POST':
        name = request.form['name']
        cursor.execute("UPDATE members SET name = %s WHERE id = %s", (name, member_id))
        db.commit()
        cursor.close()
        return redirect('/members')

    cursor.close()
    return render_template('update_member.html', member=member)

# Route for deleting a member
@app.route('/members/delete/<int:member_id>', methods=['POST'])
def delete_member(member_id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM members WHERE id = %s", (member_id,))
    db.commit()
    cursor.close()
    return redirect('/members')

@app.route('/transactions')
def list_transactions():
    cursor = db.cursor()
    cursor.execute("SELECT t.id, m.name AS member_name, b.title AS book_title, t.status FROM transactions t JOIN members m ON t.member_id = m.id JOIN books b ON t.book_id = b.id")
    transactions = cursor.fetchall()
    cursor.close()
    return render_template('list_transactions.html', transactions=transactions)

# Route for issuing a book to a member
@app.route('/transactions/issue', methods=['GET', 'POST'])
def issue_book():
    if request.method == 'POST':
        member_id = request.form['member_id']
        book_id = request.form['book_id']
        cursor = db.cursor()
        cursor.execute("INSERT INTO transactions (member_id, book_id, status) VALUES (%s, %s, 'issued')", (member_id, book_id))
        db.commit()
        cursor.close()
        return redirect('/transactions')

    # Fetch members from the database
    cursor = db.cursor()
    cursor.execute("SELECT id, name FROM members")
    members = cursor.fetchall()
    cursor.close()

    # Fetch books from the database
    cursor = db.cursor()
    cursor.execute("SELECT id, title FROM books")
    books = cursor.fetchall()
    cursor.close()

    return render_template('issue_book.html', members=members, books=books)


@app.route('/transactions/return', methods=['GET', 'POST'])
def return_book():
    if request.method == 'POST':
        transaction_id = request.form['transaction_id']
        
        # Update the existing transaction status to 'returned' in the database
        cursor = db.cursor()
        cursor.execute("""
            UPDATE transactions
            SET status = 'returned'
            WHERE id = %s
        """, (transaction_id,))
        db.commit()
        
        # Fetch the member ID and rental fee for the transaction
        cursor.execute("""
            SELECT member_id, rental_fee
            FROM transactions
            WHERE id = %s
        """, (transaction_id,))
        transaction = cursor.fetchone()
        member_id, rental_fee = transaction[0], transaction[1]
        
        # Deduct the outstanding fee of 500 from the member's table
        cursor.execute("""
            UPDATE members
            SET outstanding_debt = GREATEST(outstanding_debt - 500, 0)
            WHERE id = %s
        """, (member_id))
        db.commit()
        
        cursor.close()
        
        flash('Book returned successfully!', 'success')
        return redirect(url_for('list_transactions'))

    cursor = db.cursor()
    cursor.execute("""
        SELECT t.id, CONCAT(m.name, ' - ', b.title) AS member_book
        FROM transactions t
        JOIN members m ON t.member_id = m.id
        JOIN books b ON t.book_id = b.id
        WHERE t.status = 'issued'
    """)
    transactions = cursor.fetchall()
    cursor.close()

    return render_template('return_book.html', transactions=transactions)


# Search for a book
@app.route('/books/search', methods=['GET', 'POST'])
def search_book():
    if request.method == 'POST':
        search_term = request.form['search_term'].lower()
        results = []
        for book in books:
            if search_term in book['title'].lower() or search_term in book['author'].lower():
                results.append(book)
        return render_template('search_results.html', results=results)
    return render_template('search_book.html')

if __name__ == '__main__':
    app.run(debug=True)
