from flask import session, request, jsonify
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

        # Get the last inserted ID (primary key for mcm_ticketform)
        mcm_ticketformid = cursor.lastrowid

        # Insert vehicle details into mcm_vehicledetails
        for vehicle in form_data['mcmVehicles']:
            cursor.execute(''' 
                SELECT VehicleID FROM mcm_listvehicles WHERE VehicleName = %s
            ''', (vehicle['name'],))
            vehicle_result = cursor.fetchone()
            
            if vehicle_result:
                vehicle_id = vehicle_result[0]  # Get the vehicleID from the result
                print(f"Found VehicleID: {vehicle_id} for VehicleName: {vehicle['name']}")
                
                # Insert vehicle details into mcm_vehicledetails
                cursor.execute(''' 
                    INSERT INTO mcm_vehicledetails (FormID, VehicleID, VehicleName, VehicleQuantity)
                    VALUES (%s, %s, %s, %s)
                ''', (mcm_ticketformid, vehicle_id, vehicle['name'], vehicle['quantity']))
            else:
                print(f"Vehicle '{vehicle['name']}' not found. Skipping this vehicle.")

        # Insert travel details into mcm_traveldetails
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

        # Updated SQL query to check vehicleisused on mcm_vehicles
        query = """
            SELECT 
                v.VehicleID, 
                v.VehicleName, 
                v.VehicleQuantity, 
                v.VehicleSeatingCapacity, 
                v.VehicleImage,
                SUM(CASE WHEN mv.VehicleIsUsed = 1 THEN 1 ELSE 0 END) AS UsedQuantity  -- Reference VehicleIsUsed from mcm_vehicles
            FROM 
                mcm_listvehicles v
            LEFT JOIN 
                mcm_vehicledetails vd ON v.VehicleID = vd.VehicleID
            LEFT JOIN 
                mcm_vehicles mv ON mv.VehicleID = v.VehicleID  -- Join with mcm_vehicles to check VehicleIsUsed
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

        # Debug output to check the fetched vehicles and query
        print("Executed Query:", query)  # Print the query to ensure it's correct
        print("Fetched Vehicles:", vehicles)  # Check the output here

        # If no vehicles are fetched, print a message
        if not vehicles:
            print("No vehicles found in the database!")

        # Calculate available quantity considering vehicleisused
        for vehicle in vehicles:
            if vehicle['VehicleImage']:
                vehicle['VehicleImage'] = base64.b64encode(vehicle['VehicleImage']).decode('utf-8')

            # Start with the used quantity based on vehicleisused
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
                v.VehicleImage,
                v.VehicleIsUsed
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
            SELECT t.FormID, t.DateFilled, t.RequestedBy, t.VehicleType, d.StartDate, d.Destinations, COALESCE(t.Approval, 0) AS Approval, t.Remarks
            FROM own_ticketform t
            JOIN own_traveldetails d ON t.FormID = d.FormID
            WHERE t.UserID = %s
            UNION ALL
            SELECT m.FormID, m.DateFilled, m.RequestedBy, 'MCM Vehicle' AS VehicleType, md.StartDate, md.Destinations, COALESCE(m.Approval, 0) AS Approval, m.Remarks
            FROM mcm_ticketform m
            JOIN mcm_traveldetails md ON m.FormID = md.FormID
            WHERE m.UserID = %s
        """, (user_id, user_id))

        own_records = cursor.fetchall()

        # Group records by DateFilled, StartDate, VehicleType, and RequestedBy
        grouped_records = {}
        for record in own_records:
            # Create a unique key by combining DateFilled, StartDate, VehicleType, and RequestedBy
            unique_key = (record['DateFilled'], record['StartDate'], record['VehicleType'], record['RequestedBy'])
            if unique_key not in grouped_records:
                grouped_records[unique_key] = {
                    'FormID': record['FormID'],  # Add FormID to grouped data
                    'DateFilled': record['DateFilled'],
                    'RequestedBy': record['RequestedBy'],
                    'VehicleType': record['VehicleType'],
                    'Destinations': [record['Destinations']],
                    'Approval': record['Approval'],
                    'Remarks': record['Remarks']
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



def show_all_records():
    try:
        connection = config_connection()
        cursor = connection.cursor(dictionary=True)

        # Fetch all records from own_ticketform and mcm_ticketform (no filtering by user)
        cursor.execute("""
            SELECT t.FormID, t.DateFilled, t.RequestedBy, t.VehicleType, d.StartDate, d.Destinations, COALESCE(t.Approval, 0) AS Approval, t.Remarks, 
                   NULL AS VehicleName, NULL AS VehicleQuantity
            FROM own_ticketform t
            JOIN own_traveldetails d ON t.FormID = d.FormID
            UNION ALL
            SELECT m.FormID, m.DateFilled, m.RequestedBy, 'MCM Vehicle' AS VehicleType, md.StartDate, md.Destinations, COALESCE(m.Approval, 0) AS Approval, m.Remarks, 
                   vd.VehicleName, vd.VehicleQuantity
            FROM mcm_ticketform m
            JOIN mcm_traveldetails md ON m.FormID = md.FormID
            JOIN mcm_vehicledetails vd ON m.FormID = vd.FormID  -- Make sure this join includes the correct FormID from mcm_vehicledetails
        """)

        own_records = cursor.fetchall()

        # Group records by DateFilled, StartDate, VehicleType, and RequestedBy
        grouped_records = {}
        for record in own_records:
            # Debugging to check the record
            print(record)  # Debugging line

            unique_key = (record['DateFilled'], record['StartDate'], record['VehicleType'], record['RequestedBy'])
            if unique_key not in grouped_records:
                grouped_records[unique_key] = {
                    'FormID': record['FormID'],
                    'DateFilled': record['DateFilled'],
                    'RequestedBy': record['RequestedBy'],
                    'VehicleType': record['VehicleType'],
                    'Destinations': [record['Destinations']],
                    'Approval': record['Approval'],
                    'Remarks': record['Remarks'],
                    'VehicleName': record['VehicleName'],  # Debugging line to check VehicleName for MCM vehicles
                    'VehicleQuantity': record['VehicleQuantity'],  # Debugging line to check VehicleQuantity for MCM vehicles
                }
            else:
                grouped_records[unique_key]['Destinations'].append(record['Destinations'])

        # Debugging grouped records
        print(grouped_records)  # Debugging line

        # Prepare the final output
        final_records = []
        for (date_filled, start_date, vehicle_type, requested_by), details in grouped_records.items():
            first_destination = details['Destinations'][0]
            additional_count = len(details['Destinations']) - 1
            details['Destinations'] = f"{first_destination} +{additional_count}" if additional_count > 0 else first_destination
            details['StartDate'] = start_date
            details['DateFilled'] = date_filled
            details['VehicleType'] = vehicle_type
            # Ensure VehicleName and VehicleQuantity are included for MCM
            if vehicle_type == 'MCM Vehicle':
                details['VehicleName'] = details['VehicleName']  # Ensure VehicleName is included for MCM
                details['VehicleQuantity'] = details['VehicleQuantity']  # Ensure VehicleQuantity is included for MCM
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


def show_specific_record(form_id, vehicle_type, requested_by):
    try:
        connection = config_connection()
        cursor = connection.cursor(dictionary=True)

        # Adjust query based on vehicle type
        if vehicle_type == 'Own Vehicle':
            cursor.execute("""
                SELECT * FROM own_ticketform t
                JOIN own_traveldetails d ON t.FormID = d.FormID
                WHERE t.FormID = %s AND t.RequestedBy = %s
            """, (form_id, requested_by))
            vehicle = cursor.fetchall()
        else:  # For MCM Vehicle
            cursor.execute("""
                SELECT * FROM mcm_ticketform m
                JOIN mcm_traveldetails md ON m.FormID = md.FormID
                JOIN mcm_vehicledetails vd ON m.FormID = vd.FormID
                WHERE m.FormID = %s AND m.RequestedBy = %s
            """, (form_id, requested_by))
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

        if not remarks:
            return {"success": False, "error": "Remarks are required."}

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
                """, (remarks, *form_ids))  # Pass remarks and FormIDs

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
                """, (remarks, *form_ids))  # Pass remarks and FormIDs

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



def approve_mcm_form():
    try:
        data = request.get_json()
        # Extract form_id from the JSON data using 'formID' key
        form_id = data.get('formID')  # Corrected line
        vehicle_name = data.get('vehicleName')
        vehicle_plate_number = data.get('vehiclePlateNumber')
        vehicle_driver = data.get('vehicleDriver')
        vehicle_type = data.get('vehicleType')
        requested_by = data.get('requestedBy')

        # Check for missing fields including form_id
        if not (vehicle_name and vehicle_plate_number and vehicle_driver and form_id and vehicle_type and requested_by):
            return {"success": False, "error": "Missing parameters in request."}

            

        connection = config_connection()
        cursor = connection.cursor(dictionary=True)

        # Log the received data
        print(f"Received Data: {data}")

        # Query to get the VehicleID from mcm_vehicles based on VehicleName and VehiclePlateNumber
        query = """
            SELECT VehicleID
            FROM mcm_vehicles
            WHERE TRIM(LOWER(VehiclePlateNumber)) = TRIM(LOWER(%s)) 
              AND TRIM(LOWER(VehicleName)) = TRIM(LOWER(%s))
        """
        print(f"Executing Query to fetch VehicleID: {query} with values: PlateNumber: '{vehicle_plate_number}', VehicleName: '{vehicle_name}'")
        
        cursor.execute(query, (vehicle_plate_number, vehicle_name))
        vehicle_result = cursor.fetchone()

        # Consume the result to avoid unread result error
        cursor.fetchall()  # Add this to consume any remaining result set

        # Check if the vehicle exists
        if not vehicle_result:
            return {"success": False, "error": f"Vehicle '{vehicle_name}' with plate number '{vehicle_plate_number}' not found."}

        vehicle_id = vehicle_result['VehicleID']
        print(f"Fetched VehicleID: {vehicle_id}")

        # Now, use the VehicleID to fetch the FormID from mcm_vehicledetails and mcm_traveldetails
        query_form_id = """
            SELECT t.FormID
            FROM mcm_vehicledetails d
            JOIN mcm_traveldetails t ON d.FormID = t.FormID
            WHERE d.VehicleID = %s
        """
        print(f"Executing Query to fetch FormID for VehicleID {vehicle_id}")
        
        cursor.execute(query_form_id, (vehicle_id,))
        form_id_result = cursor.fetchone()

        # Consume the result to avoid unread result error
        cursor.fetchall()  # Add this to consume any remaining result set

        # Check if FormID exists
        if not form_id_result:
            return {"success": False, "error": "No travel details found for this vehicle."}

        form_id = form_id_result['FormID']
        print(f"Fetched FormID: {form_id}")

        # Update mcm_ticketform to set Approval = 1 based on form_id and requested_by
        cursor.execute("""
            UPDATE mcm_ticketform t
            JOIN mcm_traveldetails d ON t.FormID = d.FormID
            SET t.Approval = 1 
            WHERE t.FormID = %s AND t.RequestedBy = %s
        """, (form_id, requested_by))

        # Update mcm_vehicledetails based on FormID for the vehicle
        cursor.execute("""
            UPDATE mcm_vehicledetails
            SET VehiclePlateNumber = %s, VehicleDriver = %s
            WHERE FormID = %s
        """, (vehicle_plate_number, vehicle_driver, form_id))

        # Mark the vehicle as used in mcm_vehicles table
        cursor.execute("""
            UPDATE mcm_vehicles
            SET VehicleIsUsed = 1
            WHERE VehicleID = %s AND VehiclePlateNumber = %s AND VehicleDriver = %s
        """, (vehicle_id, vehicle_plate_number, vehicle_driver))

        # Commit the transaction
        connection.commit()
        return {"success": True}

    except Exception as e:
        print("Error occurred:", str(e))
        return {"success": False, "error": str(e)}

def approve_own_form():
    try:
        # Debug: print all query parameters
        print(f"Query Parameters: {request.args}")

        # Retrieve query parameters from the URL
        form_id = request.args.get('form_id')
        vehicle_type = request.args.get('vehicle_type')
        requested_by = request.args.get('requested_by')

        # Log the received parameters
        print(f"Form ID: {form_id}, Vehicle Type: {vehicle_type}, Requested By: {requested_by}")

        # Check if any of the parameters are None or missing
        if form_id is None or vehicle_type is None or requested_by is None:
            return {"success": False, "error": "Missing or invalid parameters in URL."}

        connection = config_connection()
        cursor = connection.cursor(dictionary=True)

        # Step 1: Check if the formID exists in the 'own_ticketform' table based on the received form_id
        cursor.execute("""
            SELECT t.FormID FROM own_ticketform t
            JOIN own_traveldetails d ON t.FormID = d.FormID
            WHERE t.FormID = %s AND t.RequestedBy = %s
        """, (form_id, requested_by))
        form_ids = cursor.fetchall()

        # Step 2: If formID exists, update the corresponding record to approve it
        if form_ids:
            cursor.execute("""
                UPDATE own_ticketform 
                SET Approval = 1 
                WHERE FormID = %s
            """, (form_id,))  # Directly update the specific formID

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



def delete_entry():
    try:
        # Extract data from the request with corrected parameter names
        data = request.json
        username = data.get('username')
        form_id = data.get('formID')  # Changed from form_id to formID
        vehicle_type = data.get('vehicle_type')  # Changed from vehicle_type
        requested_by = data.get('requested_by')  # Changed from requested_by

        # Validate required fields
        if not all([username, form_id, vehicle_type, requested_by]):
            return jsonify({"success": False, "error": "Missing required fields."}), 400

        connection = config_connection()
        cursor = connection.cursor(dictionary=True)

        if vehicle_type == "Own Vehicle":
            # Updated to use FormID instead of StartDate
            sql_delete_travel = """
            DELETE otd
            FROM own_traveldetails otd
            INNER JOIN own_ticketform otf
                ON otd.FormID = otf.FormID
            WHERE otf.FormID = %s
            """
            cursor.execute(sql_delete_travel, (form_id,))

            sql_delete_ticket = """
            DELETE FROM own_ticketform
            WHERE FormID = %s  # Use FormID directly
            """
            cursor.execute(sql_delete_ticket, (form_id,))

        else:  # For MCM vehicles
            # Simplified query using FormID from request
            sql_delete_vehicle_details = """
            DELETE FROM mcm_vehicledetails
            WHERE FormID = %s
            """
            cursor.execute(sql_delete_vehicle_details, (form_id,))

            sql_delete_travel = """
            DELETE FROM mcm_traveldetails
            WHERE FormID = %s
            """
            cursor.execute(sql_delete_travel, (form_id,))

            sql_delete_ticket = """
            DELETE FROM mcm_ticketform
            WHERE FormID = %s
            """
            cursor.execute(sql_delete_ticket, (form_id,))

        connection.commit()
        return jsonify({"success": True}) if cursor.rowcount > 0 else \
               jsonify({"success": False, "error": "Entry not found."}), 404

    except Exception as e:
        print("Error deleting entry:", e)
        return jsonify({"success": False, "error": str(e)}), 500


def cancel_entry():
    try:
        data = request.json
        username = data.get('username')
        remarks = data.get('remarks')
        start_date = request.args.get('start_date')
        vehicle_type = request.args.get('vehicle_type')
        requested_by = request.args.get('requested_by')

        if not all([username, remarks, start_date, vehicle_type, requested_by]):
            return jsonify({"success": False, "error": "Missing required fields."}), 400

        connection = config_connection()
        cursor = connection.cursor(dictionary=True)

        if vehicle_type == "Own Vehicle":
            sql = """
            SELECT ot.FormID
            FROM own_traveldetails otd
            JOIN own_ticketform ot ON otd.FormID = ot.FormID
            WHERE otd.StartDate = %s AND ot.RequestedBy = %s
            """
            cursor.execute(sql, (start_date, requested_by))
            result = cursor.fetchone()

            if result is None:
                return jsonify({"success": False, "error": "Travel details not found."}), 404

            form_id = result['FormID']

            update_sql = """
            UPDATE own_ticketform
            SET Approval = 0, Remarks = %s
            WHERE FormID = %s
            """
            cursor.execute(update_sql, (remarks, form_id))

        else:
            sql = """
            SELECT mt.FormID, v.VehicleName, v.VehiclePlateNumber, v.VehicleDriver
            FROM mcm_traveldetails mtd
            JOIN mcm_ticketform mt ON mtd.FormID = mt.FormID
            JOIN mcm_vehicledetails v ON v.FormID = mt.FormID
            WHERE mtd.StartDate = %s AND mt.RequestedBy = %s
            """
            cursor.execute(sql, (start_date, requested_by))
            result = cursor.fetchone()

            if result is None:
                return jsonify({"success": False, "error": "Travel details not found."}), 404

            form_id = result['FormID']
            vehicle_name = result['VehicleName']
            plate_number = result['VehiclePlateNumber']
            driver_name = result['VehicleDriver']

            update_sql = """
            UPDATE mcm_ticketform
            SET Approval = 0, Remarks = %s
            WHERE FormID = %s
            """
            cursor.execute(update_sql, (remarks, form_id))

            # Update the vehicle usage in mcm_vehicles based on extracted driver and plate number
            is_used_sql = """
            UPDATE mcm_vehicles
            SET VehicleIsUsed = 0
            WHERE VehicleName = %s AND VehiclePlateNumber = %s AND VehicleDriver = %s
            """
            cursor.execute(is_used_sql, (vehicle_name, plate_number, driver_name))

        connection.commit()

        if cursor.rowcount > 0:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Request not found."}), 404

    except Exception as e:
        print("Error canceling request:", e)
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_max_capacity_from_mcm_listvehicles(vehicle_name):
    connection = config_connection()  # Assuming you're using mysql.connector
    cursor = connection.cursor()
    query = "SELECT VehicleQuantity FROM mcm_listvehicles WHERE VehicleName = %s"
    cursor.execute(query, (vehicle_name,))
    result = cursor.fetchone()
    connection.close()

    if result:
        return int(result[0])  # Ensure that the VehicleQuantity is returned as an integer
    return 0  # Return 0 if no vehicle found for the given name

def delete_vehicle_from_db(vehicle_name, plate_number, driver):
    try:
        connection = config_connection()
        cursor = connection.cursor()
        
        # Delete the vehicle from the database using the additional filters
        query = """
            DELETE FROM mcm_vehicles 
            WHERE VehicleName = %s 
            AND VehiclePlateNumber = %s 
            AND VehicleDriver = %s
        """
        cursor.execute(query, (vehicle_name, plate_number, driver))
        
        connection.commit()
        connection.close()
    except Exception as e:
        print(f"Error deleting vehicle: {str(e)}")