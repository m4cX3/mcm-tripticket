from flask import Flask, request
from configuration.sql_connections import get_vehicle_id_from_name

app = Flask(__name__)

form_data = {}
def custom_zip(iter1, iter2, iter3, iter4):
    return zip(iter1, iter2, iter3, iter4)

app.jinja_env.filters['zip'] = custom_zip

def own_vehicle():
    own_name = request.form.get('ownVehicle_Name')
    classification = request.form.get('ownVehicle_Classification')
    seating_capacity = request.form.get('ownVehicle_SeatingCapacity')
    plate_number = request.form.get('ownVehicle_PlateNumber')

    return own_name, classification, seating_capacity, plate_number

def own_details():
    start_date = request.form.getlist('start_date[]')
    start_time = request.form.getlist('start_time[]')
    estimated_returns = request.form.getlist('estimated_return[]')
    destinations = request.form.getlist('destinations[]')

    return start_date, start_time, estimated_returns, destinations

def mcm_vehicle():
    vehicle_names = request.form.getlist('vehicle_name[]')  # Use vehicle names instead of IDs
    vehicle_quantities = [request.form.get(f'mcmVehicleQuantity[{vehicle_name}]') for vehicle_name in vehicle_names]

    selected_vehicles = []
    for vehicle_name, quantity in zip(vehicle_names, vehicle_quantities):
        if quantity and int(quantity) > 0:  # Ensure only vehicles with non-zero quantities are processed
            selected_vehicles.append((vehicle_name, quantity))

    return selected_vehicles


def mcm_details():
    start_date = request.form.getlist('start_date[]')
    start_time = request.form.getlist('start_time[]')
    estimated_returns = request.form.getlist('estimated_return[]')
    destinations = request.form.getlist('destinations[]')

    return start_date, start_time, estimated_returns, destinations

def submitform():
    dateFilled = request.form.get('dateFilled')    
    requestedBy = request.form.get('requestedBy')
    department = request.form.get('department')
    purpose = request.form.get('purpose')
    vehicle = request.form.get('vehicle')
    
    if vehicle == "Own Vehicle":
        form_data = {}
        own_name, classification, seating_capacity, plate_number = own_vehicle()
        start_date, start_time, estimated_returns, destinations = own_details()    
        
        form_data = {
            'dateFilled': dateFilled,
            'requestedBy': requestedBy,
            'department': department,
            'purpose': purpose,
            'vehicle': vehicle,
            'ownVehicleName': own_name,
            'ownVehicleClassification': classification,
            'ownVehicleSeatingCapacity': seating_capacity,
            'ownVehiclePlateNumber': plate_number,
            'travel_details': list(zip(start_date, start_time, estimated_returns, destinations))
        }

    elif vehicle == "MCM Vehicle":
        form_data = {}
        selected_vehicles = mcm_vehicle()  # Will return a list of (VehicleName, Quantity)
        start_date, start_time, estimated_returns, destinations = mcm_details()

        form_data = {
            'dateFilled': dateFilled,
            'requestedBy': requestedBy,
            'department': department,
            'purpose': purpose,
            'vehicle': vehicle,
            'mcmVehicles': [{'name': v[0], 'quantity': v[1]} for v in selected_vehicles],  # Store vehicle names and quantities
            'travel_details': list(zip(start_date, start_time, estimated_returns, destinations))
        }

    return form_data

def insert_vehicle():
    # Get form data
    vehicleName = request.form.get('vehicleName')
    vehicleQuantity = request.form.get('vehicleQuantity')
    vehicleSeatingCapacity = request.form.get('vehicleSeatingCapacity')
    vehicleImage = request.files.get('vehicleImage')  # Use request.files for file uploads
    
    # Initialize form data dictionary
    form_data = {}

    # Handle the vehicle image (store as binary data if image is provided)
    if vehicleImage:
        img_data = vehicleImage.read()  # Read the image data as binary
    else:
        img_data = None  # No image uploaded, set to None

    # Populate form_data dictionary with form inputs
    form_data = {
        'vehicleName': vehicleName,
        'vehicleQuantity': vehicleQuantity,
        'vehicleSeatingCapacity': vehicleSeatingCapacity,
        'vehicleImage': img_data  # Store binary image data
    }

    return form_data  # Return the form data for debugging or further processing

def insert_specific_vehicle():
    # Get form data
    vehiclePlateNumber = request.form.get('vehiclePlateNumber')
    vehicleDriver = request.form.get('vehicleDriver')
    vehicleImage = request.files.get('vehicleImage')  # Use request.files for file uploads
    vehicleName = request.form.get('vehicle_name')  # Get the vehicle name from the hidden input field

    # Get vehicleID from mcm_listvehicles based on vehicle_name
    vehicleID = get_vehicle_id_from_name(vehicleName)
    
    if not vehicleID:
        print("Error: VehicleID not found for the given vehicle name.")
        return None  # If vehicleID is not found, return None to indicate failure
    
    # Initialize form data dictionary
    form_data = {}

    # Handle the vehicle image (store as binary data if image is provided)
    if vehicleImage:
        img_data = vehicleImage.read()  # Read the image data as binary
    else:
        img_data = None  # No image uploaded, set to None

    # Populate form_data dictionary with form inputs
    form_data = {
        'vehiclePlateNumber': vehiclePlateNumber,
        'vehicleDriver': vehicleDriver,
        'vehicleImage': img_data,  # Store binary image data
        'vehicleName': vehicleName,  # Store the vehicle name (string)
        'vehicleID': vehicleID  # Add the vehicleID
    }

    return form_data  # Return the form data for further processing




