from flask import session, request
import mysql.connector
from mysql.connector import Error
import base64

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

def add_vehicle(form_data):
    try:
        connection = config_connection()
        cursor = connection.cursor()

        insert_vehicle_query = """
            INSERT INTO mcm_listvehicles (VehicleName, VehicleQuantity, VehicleSeatingCapacity, VehicleImage)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_vehicle_query, (
            form_data['vehicleName'],
            form_data['vehicleQuantity'],
            form_data['vehicleSeatingCapacity'],
            form_data['vehicleImage']
        ))
        connection.commit()

        print("Vehicle added successfully!")

    except Exception as e:
        print(f"Error adding vehicle: {str(e)}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_vehicle_id_from_name(vehicle_name):
    try:
        connection = config_connection()
        cursor = connection.cursor()

        query = "SELECT VehicleID FROM mcm_listvehicles WHERE VehicleName = %s"
        cursor.execute(query, (vehicle_name,))
        result = cursor.fetchone()

        if result:
            return result[0]  # Return the VehicleID
        else:
            return None  # Return None if no match is found

    except Exception as e:
        print(f"Error fetching VehicleID: {str(e)}")
        return None

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def add_specific_vehicle(form_data):
    try:
        print("Inserting vehicle data into the database...")
        connection = config_connection()  # Make sure this function correctly sets up your DB connection
        cursor = connection.cursor()

        insert_vehicle_query = """
            INSERT INTO mcm_vehicles (VehicleID, VehiclePlateNumber, VehicleDriver, VehicleImage, VehicleName)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_vehicle_query, (
            form_data['vehicleID'],  # Insert the VehicleID
            form_data['vehiclePlateNumber'],
            form_data['vehicleDriver'],
            form_data['vehicleImage'],  # Insert the binary image data
            form_data['vehicleName'],  # Insert the vehicle name (string)
        ))
        connection.commit()
        print("Vehicle added successfully!")
    except Exception as e:
        print(f"Error adding vehicle: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def show_mcm_vehicles():
    try:
        connection = config_connection()
        cursor = connection.cursor(dictionary=True)

        # Updated SQL query
        query = """
            SELECT 
                v.VehicleID, 
                v.VehicleName, 
                v.VehicleQuantity, 
                v.VehicleSeatingCapacity, 
                v.VehicleImage,
                COUNT(CASE WHEN t.Approval = 1 OR (t.Approval = 0 AND t.Remarks IS NOT NULL) THEN vd.VehicleID END) AS UsedQuantity
            FROM 
                mcm_listvehicles v
            LEFT JOIN 
                mcm_vehicledetails vd ON v.VehicleID = vd.VehicleID
            LEFT JOIN 
                mcm_ticketform t ON t.FormID = vd.FormID
            GROUP BY 
                v.VehicleID, 
                v.VehicleName, 
                v.VehicleQuantity, 
                v.VehicleSeatingCapacity, 
                v.VehicleImage
        """
        cursor.execute(query)
        vehicles = cursor.fetchall()

        # Debug output to check fetched vehicles
        print("Fetched Vehicles:", vehicles)  # Check the output here

        # Calculate available quantity considering approval and remarks
        for vehicle in vehicles:
            if vehicle['VehicleImage']:
                vehicle['VehicleImage'] = base64.b64encode(vehicle['VehicleImage']).decode('utf-8')
            
            # Start with the used quantity from count
            used_quantity = int(vehicle['UsedQuantity'])
            vehicle['AvailableQuantity'] = int(vehicle['VehicleQuantity']) - used_quantity

        return vehicles

    except Exception as e:
        print(f"Error retrieving vehicles: {str(e)}")
        return []

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def show_vehicles_detailed(vehicle_name=None):
    try:
        connection = config_connection()
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT 
                v.VehicleID, 
                v.VehiclePlateNumber,
                v.VehicleDriver,
                vd.VehicleName,
                v.VehicleImage
            FROM 
                mcm_vehicles v
            INNER JOIN 
                mcm_listvehicles vd ON v.VehicleID = vd.VehicleID
            WHERE 
                vd.VehicleName = %s
        """
        cursor.execute(query, (vehicle_name,))
        result = cursor.fetchall()
        
        # Encode the image data
        for row in result:
            if row['VehicleImage']:
                row['VehicleImage'] = base64.b64encode(row['VehicleImage']).decode('utf-8')

        connection.close()
        return result
    except Exception as e:
        print(f"Error retrieving vehicles: {str(e)}")
        return []



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

        # Fetch records from own_ticketform and mcm_ticketform, including the Remarks column
        cursor.execute(""" 
            SELECT t.DateFilled, t.RequestedBy, t.VehicleType, d.StartDate, d.Destinations, t.Approval, t.Remarks
            FROM own_ticketform t
            JOIN own_traveldetails d ON t.FormID = d.FormID
            WHERE t.UserID = %s
            UNION ALL
            SELECT m.DateFilled, m.RequestedBy, 'MCM Vehicle' AS VehicleType, md.StartDate, md.Destinations, m.Approval, m.Remarks
            FROM mcm_ticketform m
            JOIN mcm_traveldetails md ON m.FormID = md.FormID
            WHERE m.UserID = %s
        """, (user_id, user_id))

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
                    'Destinations': [record['Destinations']],
                    'Approval': record['Approval'],  # Add Approval field
                    'Remarks': record['Remarks']      # Add Remarks field
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
            SELECT t.DateFilled, t.RequestedBy, t.VehicleType, d.StartDate, d.Destinations, COALESCE(t.Approval, 0) AS Approval, t.Remarks
            FROM own_ticketform t
            JOIN own_traveldetails d ON t.FormID = d.FormID
            UNION ALL
            SELECT m.DateFilled, m.RequestedBy, 'MCM Vehicle' AS VehicleType, md.StartDate, md.Destinations, COALESCE(m.Approval, 0) AS Approval, m.Remarks
            FROM mcm_ticketform m
            JOIN mcm_traveldetails md ON m.FormID = md.FormID
        """)

        own_records = cursor.fetchall()

        # Group records by DateFilled, StartDate, VehicleType, and RequestedBy
        grouped_records = {}
        for record in own_records:
            # Create a unique key by combining DateFilled, StartDate, VehicleType, and RequestedBy
            unique_key = (record['DateFilled'], record['StartDate'], record['VehicleType'], record['RequestedBy'])
            if unique_key not in grouped_records:
                grouped_records[unique_key] = {
                    'DateFilled': record['DateFilled'],
                    'RequestedBy': record['RequestedBy'],
                    'VehicleType': record['VehicleType'],
                    'Destinations': [record['Destinations']],
                    'Approval': record['Approval'],  # Add Approval field
                    'Remarks': record['Remarks']      # Add Remarks field
                }
            else:
                grouped_records[unique_key]['Destinations'].append(record['Destinations'])

        # Prepare the final output
        final_records = []
        for (date_filled, start_date, vehicle_type, requested_by), details in grouped_records.items():
            first_destination = details['Destinations'][0]
            additional_count = len(details['Destinations']) - 1
            details['Destinations'] = f"{first_destination} +{additional_count}" if additional_count > 0 else first_destination
            details['StartDate'] = start_date
            details['DateFilled'] = date_filled
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
            cursor.execute(f"""
                SELECT * FROM own_ticketform t
                JOIN own_traveldetails d ON t.FormID = d.FormID
                WHERE d.StartDate = %s AND t.RequestedBy = %s
            """, (start_date, requested_by))

            vehicle = cursor.fetchall()
            
            return vehicle
        
        else:  # Assuming vehicle_type is 'MCM Vehicle'
            cursor.execute(f"""
                SELECT * FROM mcm_ticketform m
                JOIN mcm_traveldetails md ON m.FormID = md.FormID
                JOIN mcm_vehicledetails v ON v.FormID = md.FormID
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

def deny_form():
    try:
        # Retrieve query parameters from the URL
        start_date = request.args.get('start_date')
        vehicle_type = request.args.get('vehicle_type')
        requested_by = request.args.get('requested_by')

        # Log the received parameters
        print(f"Start Date: {start_date}, Vehicle Type: {vehicle_type}, Requested By: {requested_by}")

        # Log if parameters are None
        if not start_date or not vehicle_type or not requested_by:
            return {"success": False, "error": "Missing parameters in URL."}

        connection = config_connection()
        cursor = connection.cursor(dictionary=True)

        # Get the request body data
        data = request.get_json()
        remarks = data.get('remarks')

        # Log received data
        print(f"Data received: {data}")

        if vehicle_type == 'Own Vehicle':
            # Step 1: First, get the FormIDs that match the conditions
            cursor.execute("""
                SELECT t.FormID FROM own_ticketform t
                JOIN own_traveldetails d ON t.FormID = d.FormID
                WHERE d.StartDate = %s AND t.RequestedBy = %s
            """, (start_date, requested_by))
            form_ids = cursor.fetchall()

            # Step 2: Update only the matching FormIDs in the 'own_ticketform'
            if form_ids:
                form_ids = [form['FormID'] for form in form_ids]  # Extract FormID values
                cursor.execute(f"""
                    UPDATE own_ticketform 
                    SET Remarks = %s 
                    WHERE FormID IN ({', '.join(['%s'] * len(form_ids))})
                """, [remarks] + form_ids)
        else:  # Assuming vehicle_type is 'MCM Vehicle'
            cursor.execute("""
                SELECT m.FormID FROM mcm_ticketform m
                JOIN mcm_traveldetails md ON m.FormID = md.FormID
                WHERE md.StartDate = %s AND m.RequestedBy = %s
            """, (start_date, requested_by))
            form_ids = cursor.fetchall()

            if form_ids:
                form_ids = [form['FormID'] for form in form_ids]
                cursor.execute(f"""
                    UPDATE mcm_ticketform 
                    SET Remarks = %s 
                    WHERE FormID IN ({', '.join(['%s'] * len(form_ids))})
                """, [remarks] + form_ids)

        connection.commit()
        affected_rows = cursor.rowcount
        print(f"Affected rows: {affected_rows}")

        if affected_rows > 0:
            return {"success": True}
        else:
            return {"success": False, "error": "No matching records found."}

    except Exception as e:
        print(f"Error denying the request: {str(e)}")
        return {"success": False, "error": str(e)}

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def approve_form():
    try:
        # Retrieve query parameters from the URL
        start_date = request.args.get('start_date')
        vehicle_type = request.args.get('vehicle_type')
        requested_by = request.args.get('requested_by')

        # Log the received parameters
        print(f"Start Date: {start_date}, Vehicle Type: {vehicle_type}, Requested By: {requested_by}")

        # Log if parameters are None
        if not start_date or not vehicle_type or not requested_by:
            return {"success": False, "error": "Missing parameters in URL."}

        connection = config_connection()
        cursor = connection.cursor(dictionary=True)

        # Get the request body data (username if needed)
        data = request.get_json()
        username = data.get('username')  # You can log this if needed

        if vehicle_type == 'Own Vehicle':
            # Step 1: First, get the FormIDs that match the conditions
            cursor.execute("""
                SELECT t.FormID FROM own_ticketform t
                JOIN own_traveldetails d ON t.FormID = d.FormID
                WHERE d.StartDate = %s AND t.RequestedBy = %s
            """, (start_date, requested_by))
            form_ids = cursor.fetchall()

            # Step 2: Update only the matching FormIDs in the 'own_ticketform'
            if form_ids:
                form_ids = [form['FormID'] for form in form_ids]  # Extract FormID values
                cursor.execute(f"""
                    UPDATE own_ticketform 
                    SET Approval = 1 
                    WHERE FormID IN ({', '.join(['%s'] * len(form_ids))})
                """, form_ids)
        else:  # Assuming vehicle_type is 'MCM Vehicle'
            cursor.execute("""
                SELECT m.FormID FROM mcm_ticketform m
                JOIN mcm_traveldetails md ON m.FormID = md.FormID
                WHERE md.StartDate = %s AND m.RequestedBy = %s
            """, (start_date, requested_by))
            form_ids = cursor.fetchall()

            if form_ids:
                form_ids = [form['FormID'] for form in form_ids]
                cursor.execute(f"""
                    UPDATE mcm_ticketform 
                    SET Approval = 1 
                    WHERE FormID IN ({', '.join(['%s'] * len(form_ids))})
                """, form_ids)

        connection.commit()
        affected_rows = cursor.rowcount
        print(f"Affected rows: {affected_rows}")

        if affected_rows > 0:
            return {"success": True}
        else:
            return {"success": False, "error": "No matching records found."}

    except Exception as e:
        print(f"Error approving the request: {str(e)}")
        return {"success": False, "error": str(e)}

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
