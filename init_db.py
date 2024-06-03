import sqlite3

def init_db():
    conn = sqlite3.connect('internship_finder.db')
    cursor = conn.cursor()
    cursor.execute('''
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
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
