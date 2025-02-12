from flask import Flask, render_template, request, redirect, url_for, session
from configuration.sql_connections import config_connection
import sqlite3

app = Flask(__name__)
app.secret_key = 'your'

def get_email():
    email = request.form['email']
    return email

def get_username():
    email = get_email()
    username = email.split('@')[0]
    session['username'] = username

    return username

def get_password():
    password = request.form['password']
    return password

def get_user_id(username):
    try:
        connection = config_connection()
        cursor = connection.cursor()

        # Assuming username is just the part before '@' in the email
        email = f"{username}@mcm.edu.ph"  # Replace with the correct domain if applicable
        cursor.execute('SELECT UserID FROM accounts WHERE Email = ?', (email,))
        user_id = cursor.fetchone()
        
        return user_id[0] if user_id else None  # Return UserID or None if not found
    except Exception as e:
        print(f"Error fetching user ID: {str(e)}")
        return None
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        
        username = get_username()
        email = get_email()
        password = get_password()
        
        connection = config_connection()
        cursor = connection.cursor()

        cursor.execute('SELECT * FROM accounts WHERE Email = ? AND Password = ?', (email, password,))
        account = cursor.fetchone()

        if account is None:
            msg = 'Incorrect username/password!'
            return render_template('login.html', msg=msg)

        admin = account[4]  # Assign admin status from account[4]

        if admin == 1:
            print("Admin login")
            return redirect(url_for('admin_dashboard_page', username=username))
        else:
            print("User login")
            return redirect(url_for('user_dashboard_page', username=username))

    return render_template('login.html', msg=msg)  # Render login page with msg if applicable