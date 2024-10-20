from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
from configuration.sql_connections import *
from configuration.submitform import submitform
from configuration.login import login, get_user_id

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def home_page():
    data = [
        {
          'label': "Toyota Hiace Granda",
          'quantity': 2,
          'status': "Available",
          'image': "/static/images/vehicle/toyota-hiace-grandia.jpg"
        },
        {
          'label': "Yellow Bus",
          'quantity': 3,
          'status': "Not Available",
          'image': "/static/images/vehicle/yellow-bus.jpg"
        },
        {
          'label': "Toyota Hilux (Cabin)",
          'quantity': 1,
          'status': "Available",
          "image": "/static/images/vehicle/toyota-hilux(cabin).webp"
        },
      ]
    return render_template('home.html', data=data)
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    
    return login()

@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard_page():
    
    username = session.get('username')
    records = show_all_records()
    
    record_count = len(records)
    approved_count = sum(1 for record in records if record['Approval'] == 1)
    denied_count = sum(1 for record in records if record['Approval'] == 0 and record.get('Remarks') is not None)

    current_date = datetime.now().strftime("%B %d, %Y") 

    return render_template('admin_dashboard.html', records=records, record_count=record_count, 
                           approved_count=approved_count, denied_count=denied_count, 
                           current_date=current_date, username=username)

@app.route('/user_dashboard', methods=['GET', 'POST'])
def user_dashboard_page():
    
    username = session.get('username')
    records = show_records()
    print(records)

    record_count = len(records)
    approved_count = sum(1 for record in records if record['Approval'] == 1)
    denied_count = sum(1 for record in records if record['Approval'] == 0 and record.get('Remarks') is not None)
    pending_count = sum(1 for record in records if record['Approval'] == 0)
    current_date = datetime.now().strftime("%B %d, %Y")
    
    return render_template('user_dashboard.html', records=records, record_count=record_count, 
                           approved_count=approved_count, denied_count=denied_count, 
                           pending_count=pending_count, current_date=current_date, username=username)



@app.route('/admin_records', methods=['GET'])
def admin_records_page():

    username = session.get('username')
    records = show_all_records()

    return render_template('admin_records.html', records=records, username=username)

@app.route('/admin_requests', methods=['GET'])
def admin_requests_page():

    username = session.get('username')
    records = show_all_records()

    return render_template('admin_requests.html', records=records, username=username)

@app.route('/admin_records_detailed', methods=['GET'])
def admin_records_detailed_page():
    
    username = session.get('username')

    complete_details = show_specific_record()
    print(complete_details)
    return render_template('admin_records_detailed.html', details=complete_details, username=username)

@app.route('/user_records', methods=['GET'])
def user_records_page():
    
    username = session.get('username')
    own_records = show_records()
    
    return render_template('user_records.html', own_records=own_records, username=username)

@app.route('/user_records_detailed', methods=['GET'])
def user_records_detailed_page():
    
    complete_details = show_specific_record()
    return render_template('user_records_detailed.html', details=complete_details)

@app.route('/terms_and_conditions', methods=['GET'])
def terms_and_conditions_page():

    username = session.get('username')

    return render_template('terms_and_conditions.html', username=username)

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
        return redirect(url_for('user_records_page', username=username))
    else:
        print("UserID not found for the given username.")
        return redirect(url_for('trip_ticket_page', username=username))

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
        return redirect(url_for('user_records_page', username=username))
    else:
        print("UserID not found for the given username.")
        return redirect(url_for('trip_ticket_page', username=username))

@app.route('/approve_request', methods=['POST'])
def approve_form_request():

    username = session.get('username')

    return redirect(url_for('admin_records_page'), username=username)

@app.route('/deny_request', methods=['POST'])
def deny_form_request():
    return deny_form()
if __name__ == '__main__':
    app.run(debug=True)

