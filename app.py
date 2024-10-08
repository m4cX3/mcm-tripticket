from flask import Flask, render_template, request, redirect, url_for, session
from configuration.sql_connections import insert_own_data, insert_mcm_data, show_mcm_vehicles, show_records
from configuration.submitform import submitform
from configuration.login import login, get_user_id

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    
    return login()

@app.route('/admin_records', methods=['GET'])
def admin_records_page():
    return render_template('admin_records.html')

@app.route('/user_records', methods=['GET'])
def user_records_page():
    
    username = session.get('username')
    own_records = show_records()
    
    return render_template('user_records.html', own_records=own_records, username=username)

@app.route('/user_records_detailed', methods=['GET'])
def user_records_detailed_page():

    return render_template('user_records_detailed.html')

@app.route('/trip_ticket')
def trip_ticket_page():
    
    vehicles = show_mcm_vehicles()
    username = request.args.get('username') or session.get('username')
    
    return render_template('trip_ticket.html', vehicles=vehicles, username=username)

@app.route('/submit', methods=['POST'])  # Only need POST for form submission
def submit_form():
    
    form_data = submitform()  # Call your submitform function
    session['form_data'] = form_data  # Store in session
    username = session.get('username')

    if form_data['vehicle'] == 'Own Vehicle':
        print(form_data)
        return redirect(url_for('own_tripticket_summary_page', username=username))  # Redirect to summary page for Own Vehicle
    else:
        print(form_data)
        return redirect(url_for('mcm_tripticket_summary_page', username=username))  # Redirect to summary page for MCM Vehicle

@app.route('/own_tripticket_summary', methods=['GET', 'POST'])
def own_tripticket_summary_page():
    
    form_data = session.get('form_data')  # Get form data from session
    
    return render_template('own_tripticket_summary.html', data=form_data)

@app.route('/insert_own_to_database', methods=['POST'])
def insert_own_form_to_database():
    
    form_data = session.get('form_data')
    username = session.get('username')  # Get username from session
    user_id = get_user_id(username)

    print(f"UserID for username {username}: {user_id}")

    if user_id is not None:
        insert_own_data(form_data, user_id)
        return redirect(url_for('trip_ticket_page', username=username))  # Redirect to trip ticket page after insert
    else:
        print("UserID not found for the given username.")
        return redirect(url_for('trip_ticket_page', username=username))  # Redirect for error handling

@app.route('/mcm_tripticket_summary', methods=['GET', 'POST'])
def mcm_tripticket_summary_page():
    
    form_data = session.get('form_data')  # Get form data from session
    
    return render_template('mcm_tripticket_summary.html', data=form_data)

@app.route('/insert_mcm_to_database', methods=['POST'])
def insert_mcm_form_to_database():
    
    form_data = session.get('form_data')
    username = session.get('username')  # Get username from session
    user_id = get_user_id(username)
    
    print(f"UserID for username {username}: {user_id}")

    if user_id is not None:
        insert_mcm_data(form_data, user_id)
        return redirect(url_for('trip_ticket_page', username=username))  # Redirect to trip ticket page after insert
    else:
        print("UserID not found for the given username.")
        return redirect(url_for('trip_ticket_page', username=username))  # Redirect for error handling

if __name__ == '__main__':
    app.run(debug=True)