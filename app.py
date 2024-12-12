from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import hashlib
import re

app = Flask(__name__)
app.secret_key = 'super_secret_key'

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def connect_db():
    conn = sqlite3.connect('loginy_hasla.db')
    return conn

def check_password_requirements(password):
    if len(password) < 10:
        return False

    if not any(char.isupper() for char in password):
        return False

    if not len(re.findall(r'\d', password)) >= 3:
        return False

    return True

@app.route('/')
def index():
    if 'username' in session:
        return render_template('todo.html')
    else:
        return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        conn = connect_db()
        cursor = conn.cursor()


        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        if cursor.fetchone() is not None:
            return render_template('register.html', error="User already exist!")

        if password != confirm_password:
            return render_template('register.html', error="Passwords do not match!")

        if not check_password_requirements(password):
            return render_template('register.html', error="Password does not meet the requirements!")
        
        password_hash = hash_password(password)
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        conn.close()

        return redirect('/login')
    else:
        return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT password_hash FROM users WHERE username=?", (username,))
        result = cursor.fetchone()

        if result:
            stored_password_hash = result[0]
            password_hash = hash_password(password)

            if stored_password_hash == password_hash:
                session['username'] = username
                return redirect('/')
            else:
                return render_template('login.html', error="Wrong password!")
        else:
            return render_template('login.html', error="User does not exist!")
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
