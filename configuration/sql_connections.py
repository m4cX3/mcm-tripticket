from flask import session, request
import mysql.connector
from mysql.connector import Error

class Config:
    MYSQL_HOST = 'localhost'  # Your MySQL host
    MYSQL_USER = 'root'  # Your MySQL username
    MYSQL_PASSWORD = 'Viva@MCM!'  # Your MySQL password
    MYSQL_DB = 'mcm_trip_ticket'  # Your database name

def config_connection():
    connection = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB
    )
    return connection

def check_mysql_connection():
    try:
        connection = config_connection()
        if connection.is_connected():
            print("MySQL server is open and reachable.")
            print("Successfully connected to MySQL.")
            return config_connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None
    finally:
        if connection.is_connected():
            connection.close()

def insert_own_data(form_data, user_id):
    try:
        connection = config_connection()
        cursor = connection.cursor()

        # Log the values before the insert
        print(f"Inserting data: UserID={user_id}, DateFilled={form_data['dateFilled']}, RequestedBy={form_data['requestedBy']}, ...")

        cursor.execute(''' 
            INSERT INTO own_ticketform (UserID, DateFilled, RequestedBy, Department, Purpose_Of_Trip, VehicleType, VehicleName, 
            Classification, SeatingCapacity, PlateNumber)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            user_id,
            form_data['dateFilled'],
            form_data['requestedBy'],
            form_data['department'],
            form_data['purpose'],
            form_data['vehicle'],
            form_data['ownVehicleName'],
            form_data['ownVehicleClassification'],
            form_data['ownVehicleSeatingCapacity'],
            form_data['ownVehiclePlateNumber'],
        ))
        # Get the last inserted ID (primary key for ticketform_own)
        own_ticketformid = cursor.lastrowid

        # Insert travel details into `ticketform_travel_details`
        for travel in form_data['travel_details']:
            start_date, start_time, estimated_return, destination = travel

            # Check if any of the travel details are empty or None
            if start_date and start_time and estimated_return and destination:
                cursor.execute(''' 
                    INSERT INTO own_traveldetails (FormID, UserID, StartDate, StartTime, EstimatedReturns, Destinations)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (own_ticketformid, user_id, start_date, start_time, estimated_return, destination))


        # Commit the changes
        connection.commit()

        if connection.is_connected():
            print("Data inserted successfully.")

    except Exception as e:
        print(f"Error inserting data: {str(e)}")
        connection.rollback()

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def insert_mcm_data(form_data, user_id):
    try:
        connection = config_connection()
        cursor = connection.cursor()

        # Log the values before the insert
        print(f"Inserting data: UserID={user_id}, DateFilled={form_data['dateFilled']}, RequestedBy={form_data['requestedBy']}, ...")

        cursor.execute(''' 
            INSERT INTO mcm_ticketform (UserID, DateFilled, RequestedBy, Department, Purpose_Of_Trip, VehicleType)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (
            user_id,
            form_data['dateFilled'],
            form_data['requestedBy'],
            form_data['department'],
            form_data['purpose'],
            form_data['vehicle'],
        ))
        
        # Get the last inserted ID (primary key for ticketform_own)
        mcm_ticketformid = cursor.lastrowid

        # Insert vehicle details into a separate table or ensure vehicle details are handled correctly
        for vehicle in form_data['mcmVehicles']:
            cursor.execute(''' 
                SELECT VehicleID FROM mcm_listvehicles WHERE VehicleName = %s
            ''', (vehicle['name'],))
            vehicle_result = cursor.fetchone()
            
            if vehicle_result:
                vehicle_id = vehicle_result[0]  # Get the vehicleID from the result
                print(f"Found VehicleID: {vehicle_id} for VehicleName: {vehicle['name']}")
                
                # Instead of an update, consider inserting into a separate table for vehicle details
                cursor.execute(''' 
                    INSERT INTO mcm_vehicledetails (FormID, VehicleID, VehicleName, VehicleQuantity)
                    VALUES (%s, %s, %s, %s)
                ''', (mcm_ticketformid, vehicle_id, vehicle['name'], vehicle['quantity']))
            else:
                print(f"Vehicle '{vehicle['name']}' not found. Skipping this vehicle.")

        # Insert travel details into `mcm_traveldetails`
        for travel in form_data['travel_details']:
            start_date, start_time, estimated_return, destination = travel
            
            if all([start_date, start_time, estimated_return, destination]):  # Check if all fields are present
                cursor.execute(''' 
                    INSERT INTO mcm_traveldetails (FormID, UserID, StartDate, StartTime, EstimatedReturns, Destinations)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (mcm_ticketformid, user_id, start_date, start_time, estimated_return, destination))
            else:
                print(f"Travel detail incomplete: {travel}. Skipping this entry.")

        # Commit the changes
        connection.commit()
        print("Data inserted successfully.")

    except Exception as e:
        print(f"Error inserting data: {str(e)}")
        connection.rollback()

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def show_mcm_vehicles():
    try:
        connection = config_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT VehicleID, VehicleName, VehicleQuantity, VehicleSeatingCapacity, VehicleImage FROM mcm_listvehicles")
        vehicles = cursor.fetchall()
        
        return vehicles

    except Exception as e:
        print(f"Error retrieving vehicles: {str(e)}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def show_records():
    try:
        connection = config_connection()
        cursor = connection.cursor(dictionary=True)

        email = f"{session['username']}@mcm.edu.ph"
        cursor.execute("SELECT UserId FROM accounts WHERE Email = %s", (email,))
        user = cursor.fetchone()

        if not user:
            print(f"No user found with email: {email}")
            return []

        user_id = user['UserId']  # Change from 'id' to 'UserId'

        # Fetch records from own_ticketform and mcm_ticketform
        cursor.execute(""" 
            SELECT t.DateFilled, t.RequestedBy, t.VehicleType, d.StartDate, d.Destinations
            FROM own_ticketform t
            JOIN own_traveldetails d ON t.FormID = d.FormID
            WHERE t.UserID = %s
            UNION ALL
            SELECT m.DateFilled, m.RequestedBy, 'MCM Vehicle' AS VehicleType, md.StartDate, md.Destinations
            FROM mcm_ticketform m
            JOIN mcm_traveldetails md ON m.FormID = md.FormID
            WHERE m.UserID = %s
        """, (user_id, user_id))

        own_records = cursor.fetchall()

        # Group records by StartDate, VehicleType, and Destinations
        grouped_records = {}
        for record in own_records:
            # Create a unique key by combining StartDate, VehicleType, and Destinations
            unique_key = (record['StartDate'], record['VehicleType'], record['RequestedBy'])
            if unique_key not in grouped_records:
                grouped_records[unique_key] = {
                    'DateFilled': record['DateFilled'],
                    'RequestedBy': record['RequestedBy'],
                    'VehicleType': record['VehicleType'],
                    'Destinations': [record['Destinations']]
                }
            else:
                grouped_records[unique_key]['Destinations'].append(record['Destinations'])

        # Prepare the final output
        final_records = []
        for (start_date, vehicle_type, requested_by), details in grouped_records.items():
            first_destination = details['Destinations'][0]
            additional_count = len(details['Destinations']) - 1
            details['Destinations'] = f"{first_destination} +{additional_count}" if additional_count > 0 else first_destination
            details['StartDate'] = start_date
            details['VehicleType'] = vehicle_type
            final_records.append(details)

        return final_records
    except Exception as e:
        print(f"Error retrieving own_ticketform and mcm_ticketform data: {str(e)}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def show_all_records():
    try:
        connection = config_connection()
        cursor = connection.cursor(dictionary=True)

        # Fetch all records from own_ticketform and mcm_ticketform (no filtering by user)
        cursor.execute(""" 
            SELECT t.DateFilled, t.RequestedBy, t.VehicleType, d.StartDate, d.Destinations
            FROM own_ticketform t
            JOIN own_traveldetails d ON t.FormID = d.FormID
            UNION ALL
            SELECT m.DateFilled, m.RequestedBy, 'MCM Vehicle' AS VehicleType, md.StartDate, md.Destinations
            FROM mcm_ticketform m
            JOIN mcm_traveldetails md ON m.FormID = md.FormID
        """)

        own_records = cursor.fetchall()

        # Group records by StartDate, VehicleType, and Destinations
        grouped_records = {}
        for record in own_records:
            # Create a unique key by combining StartDate, VehicleType, and RequestedBy
            unique_key = (record['StartDate'], record['VehicleType'], record['RequestedBy'])
            if unique_key not in grouped_records:
                grouped_records[unique_key] = {
                    'DateFilled': record['DateFilled'],
                    'RequestedBy': record['RequestedBy'],
                    'VehicleType': record['VehicleType'],
                    'Destinations': [record['Destinations']]
                }
            else:
                grouped_records[unique_key]['Destinations'].append(record['Destinations'])

        # Prepare the final output
        final_records = []
        for (start_date, vehicle_type, requested_by), details in grouped_records.items():
            first_destination = details['Destinations'][0]
            additional_count = len(details['Destinations']) - 1
            details['Destinations'] = f"{first_destination} +{additional_count}" if additional_count > 0 else first_destination
            details['StartDate'] = start_date
            details['VehicleType'] = vehicle_type
            final_records.append(details)

        return final_records
    except Exception as e:
        print(f"Error retrieving own_ticketform and mcm_ticketform data: {str(e)}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def show_specific_record():
    try:
        connection = config_connection()
        cursor = connection.cursor(dictionary=True)

        start_date = request.args.get('start_date')
        vehicle_type = request.args.get('vehicle_type')
        requested_by = request.args.get('requested_by')

        if vehicle_type == 'Own Vehicle':
            cursor.execute("""
                SELECT * FROM own_ticketform t
                JOIN own_traveldetails d ON t.FormID = d.FormID
                WHERE d.StartDate = %s AND t.RequestedBy = %s
            """, (start_date, requested_by))

            vehicle = cursor.fetchall()
            
            return vehicle
        
        else:  # Assuming vehicle_type is 'MCM Vehicle'
            cursor.execute("""
                SELECT * FROM mcm_ticketform m
                JOIN mcm_traveldetails md ON m.FormID = md.FormID
                WHERE md.StartDate = %s AND m.RequestedBy = %s
            """, (start_date, requested_by))
            
            vehicle = cursor.fetchall()

            return vehicle
        
    except Exception as e:
        print(f"Error retrieving complete details: {str(e)}")
        return []
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()