from flask import Flask, request

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