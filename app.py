from flask import Flask, render_template, request, redirect, session, flash, g
from flask_mail import Mail, Message
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'manishd.btech23@rvu.edu.in'
app.config['MAIL_PASSWORD'] = 'Dhana@2023'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

DATABASE = 'internship_finder.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with app.app_context():
        cursor = db.cursor()
        cursor.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                user_type TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS internships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                teacher_id INTEGER NOT NULL,
                FOREIGN KEY (teacher_id) REFERENCES users (id)
            );
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                internship_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                FOREIGN KEY (student_id) REFERENCES users (id),
                FOREIGN KEY (internship_id) REFERENCES internships (id)
            );
        ''')
        db.commit()

@app.route('/')
def index():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        user_type = request.form['user_type']
        
        db = get_db()
        cur = db.execute('SELECT * FROM users WHERE user_id = ? AND password = ? AND user_type = ?', 
                         (user_id, password, user_type))
        user = cur.fetchone()

        if user:
            session['user_id'] = user[0]
            session['user_type'] = user_type
            return redirect('/dashboard')
        else:
            flash('Invalid login credentials')
            return redirect('/login')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        user_type = request.form['user_type']
        
        db = get_db()
        db.execute('INSERT INTO users (user_id, password, user_type) VALUES (?, ?, ?)', 
                   (user_id, password, user_type))
        db.commit()
        
        flash('Registration successful, please log in')
        return redirect('/login')
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    db = get_db()
    cur = db.execute('SELECT * FROM internships')
    internships = cur.fetchall()

    return render_template('dashboard.html', internships=internships)

@app.route('/apply/<int:internship_id>', methods=['GET', 'POST'])
def apply(internship_id):
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        student_id = session['user_id']

        db = get_db()
        db.execute('INSERT INTO applications (student_id, internship_id, name, email) VALUES (?, ?, ?, ?)', 
                   (student_id, internship_id, name, email))
        db.commit()

        cur = db.execute('SELECT * FROM internships WHERE id = ?', (internship_id,))
        internship = cur.fetchone()

        cur = db.execute('SELECT * FROM users WHERE id = ?', (internship[3],))
        teacher = cur.fetchone()

        if teacher:
            teacher_email = teacher[1]
            msg = Message('New Internship Application',
                          sender='manishd.btech23@rvu.edu.in',
                          recipients=[teacher_email])
            print(teacher_email)
            msg.body = f'Student {name} ({email}) has applied for your internship {internship[1]}.'
            mail.send(msg)

        flash('Application successful')
        return redirect('/dashboard')
    
    return render_template('apply.html')

@app.route('/post_internship', methods=['GET', 'POST'])
def post_internship():
    if 'user_id' not in session or session.get('user_type') != 'teacher':
        return redirect('/login')

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        teacher_id = session['user_id']

        db = get_db()
        db.execute('INSERT INTO internships (title, description, teacher_id) VALUES (?, ?, ?)', 
                   (title, description, teacher_id))
        db.commit()

        flash('Internship posted successfully')
        return redirect('/dashboard')
    return render_template('post_internship.html')

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)
