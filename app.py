from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
from configuration.sql_connections import *
from configuration.submitform import submitform, insert_vehicle, insert_specific_vehicle
from configuration.login import login, get_user_id

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def home_page():
    details = show_mcm_vehicles()
    return render_template('home.html', details=details)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    
    return login()

@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard_page():
    
    username = session.get('username')
    records = show_all_records()  # Retrieve all records initially
    
    # Initialize variables with default values
    name_filter = ""
    start_date = None
    end_date = None

    if request.method == 'POST':
        # Get user input from the form
        name_filter = request.form.get('name', '').strip()  # Stripping leading/trailing whitespace
        start_date_filter = request.form.get('start_date')
        end_date_filter = request.form.get('end_date')

        # Convert date strings to date objects if provided
        if start_date_filter:
            start_date = datetime.strptime(start_date_filter, '%Y-%m-%d').date()
        if end_date_filter:
            end_date = datetime.strptime(end_date_filter, '%Y-%m-%d').date()

        # Filtering logic
        if name_filter:
            # Partial match (case insensitive)
            records = [record for record in records if name_filter.lower() in record['RequestedBy'].lower()]

        if start_date and end_date:
            records = [record for record in records if start_date <= record['DateFilled'] <= end_date]
        elif start_date:
            records = [record for record in records if record['DateFilled'] >= start_date]
        elif end_date:
            records = [record for record in records if record['DateFilled'] <= end_date]

    
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
    own_records = show_records()

    # Initialize variables with default values
    name_filter = ""
    start_date = None
    end_date = None

    if request.method == 'POST':
        # Get user input from the form
        name_filter = request.form.get('name', '').strip()  # Stripping leading/trailing whitespace
        start_date_filter = request.form.get('start_date')
        end_date_filter = request.form.get('end_date')

        # Convert date strings to date objects if provided
        if start_date_filter:
            start_date = datetime.strptime(start_date_filter, '%Y-%m-%d').date()
        if end_date_filter:
            end_date = datetime.strptime(end_date_filter, '%Y-%m-%d').date()

        # Filtering logic
        if name_filter:
            # Partial match (case insensitive)
            own_records = [record for record in own_records if name_filter.lower() in record['RequestedBy'].lower()]

        if start_date and end_date:
            own_records = [record for record in own_records if start_date <= record['DateFilled'] <= end_date]
        elif start_date:
            own_records = [record for record in own_records if record['DateFilled'] >= start_date]
        elif end_date:
            own_records = [record for record in own_records if record['DateFilled'] <= end_date]

    record_count = len(own_records)
    approved_count = sum(1 for record in own_records if record['Approval'] == 1)
    denied_count = sum(1 for record in own_records if record['Approval'] == 0 and record.get('Remarks') is not None)
    pending_count = sum(1 for record in own_records if record['Approval'] == 0 and record.get('Remarks') is None)
    current_date = datetime.now().strftime("%B %d, %Y")
    
    return render_template('user_dashboard.html', own_records=own_records, record_count=record_count, 
                           approved_count=approved_count, denied_count=denied_count, 
                           pending_count=pending_count, current_date=current_date, 
                           username=username, name=name_filter, start_date=start_date, end_date=end_date)



@app.route('/admin_records', methods=['GET', 'POST'])
def admin_records_page():
    username = session.get('username')
    records = show_all_records()

    # Initialize variables with default values
    name_filter = ""
    start_date = None
    end_date = None

    if request.method == 'POST':
        # Get user input from the form
        name_filter = request.form.get('name', '').strip()  # Stripping leading/trailing whitespace
        start_date_filter = request.form.get('start_date')
        end_date_filter = request.form.get('end_date')

        # Convert date strings to date objects if provided
        if start_date_filter:
            start_date = datetime.strptime(start_date_filter, '%Y-%m-%d').date()
        if end_date_filter:
            end_date = datetime.strptime(end_date_filter, '%Y-%m-%d').date()

        # Filtering logic
        if name_filter:
            # Partial match (case insensitive)
            records = [record for record in records if name_filter.lower() in record['RequestedBy'].lower()]

        if start_date and end_date:
            records = [record for record in records if start_date <= record['DateFilled'] <= end_date]
        elif start_date:
            records = [record for record in records if record['DateFilled'] >= start_date]
        elif end_date:
            records = [record for record in records if record['DateFilled'] <= end_date]

    return render_template('admin_records.html', records=records, username=username, name=name_filter, start_date=start_date, end_date=end_date)

@app.route('/admin_requests', methods=['GET'])
def admin_requests_page():

    username = session.get('username')
    records = show_all_records()

    return render_template('admin_requests.html', records=records, username=username)

@app.route('/mcm_vehicle_approved', methods=['GET'])
def mcm_vehicle_approved_page():
    username = session.get('username')
    
    form_id = request.args.get('form_id')
    vehicle_type = request.args.get('vehicle_type')
    requested_by = request.args.get('requested_by')
    vehicle_name = request.args.get('vehicle_name')
    
    form_details = show_specific_record(form_id, vehicle_type, requested_by)
    complete_details = show_vehicles_detailed(vehicle_name)

    return render_template(
        'mcm_vehicle_approved.html', 
        form_details=form_details, 
        details=complete_details, 
        username=username,
        form_id=form_id, 
        vehicle_type=vehicle_type, 
        requested_by=requested_by, 
        vehicle_name=vehicle_name
    )


@app.route('/admin_records_detailed', methods=['GET', 'POST'])
def admin_records_detailed_page():
    username = session.get('username')

    # Fetch query parameters from the URL
    form_id = request.args.get('form_id')
    vehicle_type = request.args.get('vehicle_type')
    requested_by = request.args.get('requested_by')

    # Debug print statements to ensure the parameters are being passed correctly
    print(f"Form ID: {form_id}, Vehicle Type: {vehicle_type}, Requested By: {requested_by}")

    # If form_id, vehicle_type, or requested_by are missing, return a 400 error
    if not form_id or not vehicle_type or not requested_by:
        return "Missing parameters", 400

    # Call the function to get the complete details using form_id, vehicle_type, and requested_by
    complete_details = show_specific_record(form_id, vehicle_type, requested_by)

    # Handle POST request
    if request.method == 'POST':
        if vehicle_type == "Own Vehicle":
            return redirect(url_for('admin_records_page', username=username))
        elif vehicle_type == "MCM Vehicle":
            return redirect(url_for('mcm_vehicle_approved_page', username=username, vehicle_data=complete_details))

    # Render the page with the fetched details
    return render_template('admin_records_detailed.html', details=complete_details, username=username,
                           form_id=form_id, vehicle_type=vehicle_type, requested_by=requested_by)




@app.route('/admin_vehicles', methods=['GET'])
def admin_vehicles_page():
    
    username = session.get('username')

    complete_details = show_mcm_vehicles()
    print(complete_details)
    return render_template('admin_vehicles.html', details=complete_details, username=username)

@app.route('/admin_vehicles_detailed/<vehicle_name>', methods=['GET', 'POST'])
def admin_vehicles_detailed_page(vehicle_name):
    username = session.get('username')
    
    if not vehicle_name:
        return redirect(url_for('admin_vehicles_page'))  # Redirect if no vehicle name provided

    # Fetch the detailed vehicle records for the given vehicle name
    complete_details = show_vehicles_detailed(vehicle_name)
    print(complete_details)

    # Fetch the max capacity (VehicleQuantity) from the mcm_listvehicles table based on vehicle_name
    max_capacity = get_max_capacity_from_mcm_listvehicles(vehicle_name)

    # Calculate the total number of vehicles
    total_vehicles = len(complete_details)

    # Check if the vehicle list is full
    is_full = total_vehicles >= max_capacity  # If total vehicles reach max capacity, set is_full to True

    if request.method == 'POST':
        # Insert the new vehicle based on the form data
        form_data = insert_specific_vehicle()
        add_specific_vehicle(form_data)
        # Redirect to the same page after adding a vehicle
        return redirect(url_for('admin_vehicles_detailed_page', username=username, vehicle_name=vehicle_name))
    
    # Render the template with the vehicle details, username, vehicle name, total vehicles, max capacity, and full status
    return render_template('admin_vehicles_detailed.html', 
                           details=complete_details, 
                           username=username, 
                           vehicle_name=vehicle_name, 
                           total_vehicles=total_vehicles,
                           max_capacity=max_capacity,
                           is_full=is_full)  # Pass the is_full flag to the template



@app.route('/add_vehicles', methods=['GET', 'POST'])
def add_vehicles_page():
    username = session.get('username')
    if request.method == 'POST':
        form_data = insert_vehicle()
        add_vehicle(form_data)
        return redirect(url_for('admin_vehicles_page', username=username))

    return render_template('add_vehicle.html', username=username)


@app.route('/user_records', methods=['GET', 'POST'])
def user_records_page():
    username = session.get('username')
    own_records = show_records()
    
    # Initialize variables with default values
    name_filter = ""
    start_date = None
    end_date = None

    if request.method == 'POST':
        # Get user input from the form
        name_filter = request.form.get('name', '').strip()  # Stripping leading/trailing whitespace
        start_date_filter = request.form.get('start_date')
        end_date_filter = request.form.get('end_date')

        # Convert date strings to date objects if provided
        if start_date_filter:
            start_date = datetime.strptime(start_date_filter, '%Y-%m-%d').date()
        if end_date_filter:
            end_date = datetime.strptime(end_date_filter, '%Y-%m-%d').date()

        # Filtering logic
        if name_filter:
            # Partial match (case insensitive)
            own_records = [record for record in own_records if name_filter.lower() in record['RequestedBy'].lower()]

        if start_date and end_date:
            own_records = [record for record in own_records if start_date <= record['DateFilled'] <= end_date]
        elif start_date:
            own_records = [record for record in own_records if record['DateFilled'] >= start_date]
        elif end_date:
            own_records = [record for record in own_records if record['DateFilled'] <= end_date]

    # Return filtered records to the template
    return render_template('user_records.html', own_records=own_records, username=username, name=name_filter, start_date=start_date, end_date=end_date)


@app.route('/user_records_detailed', methods=['GET'])
def user_records_detailed_page():
    
    # Fetch query parameters from the URL
    form_id = request.args.get('form_id')
    vehicle_type = request.args.get('vehicle_type')
    requested_by = request.args.get('requested_by')

    # Debug print statements to ensure the parameters are being passed correctly
    print(f"Form ID: {form_id}, Vehicle Type: {vehicle_type}, Requested By: {requested_by}")

    # If form_id, vehicle_type, or requested_by are missing, return a 400 error
    if not form_id or not vehicle_type or not requested_by:
        return "Missing parameters", 400

    # Call the function to get the complete details using form_id, vehicle_type, and requested_by
    complete_details = show_specific_record(form_id, vehicle_type, requested_by)

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

    if user_id == 'admin':
        insert_own_data(form_data, user_id)
        return redirect(url_for('admin_requests_page', username=username))
    
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

    if user_id == 'admin':
        insert_mcm_data(form_data, user_id)
        return redirect(url_for('admin_requests_page', username=username))
    
    if user_id is not None:
        insert_mcm_data(form_data, user_id)
        return redirect(url_for('user_records_page', username=username))
    else:
        print("UserID not found for the given username.")
        return redirect(url_for('trip_ticket_page', username=username))

@app.route('/approve_own_request', methods=['POST'])
def approve_own_form_request():
    return approve_own_form()

@app.route('/approve_mcm_request', methods=['POST'])
def approve_mcm_form_request():
    return approve_mcm_form()

@app.route('/deny_request', methods=['POST'])
def deny_form_request():
    return deny_form()

@app.route('/delete_entry', methods=['POST'])
def delete_entry_request():
    return delete_entry()

@app.route('/cancel_request', methods=['POST'])
def cancel_entry_request():
    return cancel_entry()

@app.route('/delete_vehicle/<username>/<vehicle_name>', methods=['POST'])
def delete_vehicle(username, vehicle_name):
    if request.method == 'POST':
        # Get the additional parameters from the form
        plate_number = request.form.get('plate_number')
        driver = request.form.get('driver')
        
        # Call the function to delete the vehicle with the additional filters
        delete_vehicle_from_db(vehicle_name, plate_number, driver)
        
        # Redirect back to the detailed vehicles page
        return redirect(url_for('admin_vehicles_detailed_page', username=username, vehicle_name=vehicle_name))

@app.route('/delete_vehicle/<vehicle_name>', methods=['POST'])
def delete_vehicles(vehicle_name):
    result = delete_specific_vehicle(vehicle_name)
    
    # Return JSON response instead of redirect
    return result

if __name__ == '__main__':
    app.run(debug=True)

