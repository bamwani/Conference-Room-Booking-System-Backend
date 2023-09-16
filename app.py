import threading
from datetime import datetime, timedelta
from service.floor import define_floor, calculate_available_capacity
from service.organization import define_organization, reset_monthly_booking_hours
from service.user import define_user, is_email_unique, is_emp_id_unique
from service.room import define_room, list_rooms_with_availability
from service.booking import define_booking, is_room_available, available_rooms_of_floor, list_bookings_for_organization, get_booking_by_organization_and_id
from flask import Flask, request, jsonify  


app = Flask(__name__)

# Define a lock for thread-safety
lock = threading.Lock()


all_rooms = {}
all_bookings = {}
all_floors = {}
all_orgs = {}
all_users = {}
organization_booking_hours = {}


@app.route('/floors', methods=['POST'])
def add_floor():
    """
    Add a new floor to the conference room booking system. It calculates the next available floor
    number, creates a new floor object, and adds it to the system's data.

    Returns:
        Flask Response: A JSON response indicating the success or failure of the operation.
    """
    try:
        with lock:
            floor_number = 0 if len(all_floors) == 0 else list(all_floors.keys())[-1] + 1
            try:
                new_floor = define_floor(floor_number=floor_number)
            except KeyError:
                return jsonify({"success":False, "message": "Insufficient data provided."}), 400
            all_floors[floor_number] = new_floor
        return jsonify({"message": "Floor added successfully"}), 201

    except Exception as e:
        return jsonify({"success":False, "message": str(e)}), 400

@app.route('/floors', methods=['GET'])
def get_floors():
    """
    Retrieve a list of all floors in the conference room booking system.

    This endpoint allows users to retrieve a list of all available floors in the system. It returns the floor data,
    including floor numbers, as well as the total count of floors.

    Returns:
        Flask Response: A JSON response containing the list of floors and the total count of floors.
    """
    try:
        return jsonify({"success": True, "data": all_floors, "count":len(all_floors)})
    except Exception as e:
        return jsonify({"success":False, "message": str(e)}), 400

@app.route('/floors/<int:floor_number>', methods=['GET'])
def get_floor(floor_number):
    """
    Retrieve details of a specific floor in the conference room booking system.

    This endpoint allows users to retrieve details of a specific floor by providing its floor number in the URL path.
    It returns information about the floor, including its number, capacity, and room details.

    Args:
        floor_number (int): The floor number for which details are requested.

    Returns:
        Flask Response: A JSON response containing the details of the requested floor.
    """
    try:
        return jsonify({"success": True, "data": all_floors[floor_number]})
    except Exception as e:
        return jsonify({"success":False, "message": str(e)}), 400

###########  ROOM  ROUTES  ###########

@app.route('/rooms', methods=['POST'])
def add_room():
    """
    Add a new room to a specific floor in the conference room booking system.

    This endpoint allows administrators to add a new room to a specified floor in the system. It performs various checks,
    including verifying that the floor exists, the room number is unique, and the available capacity on the floor is sufficient
    to accommodate the new room's capacity.

    Args:
        JSON Request Body:
            {
                "floor_number" (int): The floor number where the room should be added.
                "room_number" (int): The room number for the new room.
                "capacity" (int): The capacity of the new room.
            }

    Returns:
        Flask Response: A JSON response indicating the success or failure of the operation.
    """
    try:
        data = request.get_json()
        floor_number = data["floor_number"]
        if floor_number not in all_floors.keys():
            return jsonify({"success":False, "message": f"Floor {floor_number} has not beed added yet."}), 400
        room_number = data["room_number"]
        curr_floor = all_floors[floor_number]
        available_capacity = calculate_available_capacity(curr_floor)
        if room_number in all_floors[floor_number]["rooms"]:
            return jsonify({"success":False, "message": f"Room number {room_number} already exists."}), 400
        if available_capacity < data["capacity"]:
            return jsonify({"success":False, "message": f"Floor {floor_number} has {available_capacity} capacity available"}), 400
        try:
            new_room = define_room(**data)
        except KeyError:
            return jsonify({"success":False, "message": "Insufficient data provided."}), 400
        all_floors[floor_number]["rooms"][room_number] = new_room
        return jsonify({"success":True, "message": "Room added successfully"}), 201
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400


@app.route('/rooms', methods=['GET'])
def get_rooms():
    """
    Retrieve a list of available rooms with their availability status.

    This endpoint allows users to retrieve a list of all available rooms in the conference room booking system.
    It returns information about each room's availability status and other details.

    Returns:
        Flask Response: A JSON response containing the list of available rooms.
    """
    try:
        with lock:
            rooms = list_rooms_with_availability(all_floors=all_floors, all_bookings=all_bookings)
        return jsonify({"success": True, "data": rooms})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route('/rooms/search', methods=['GET'])
def search_rooms():
    """
    Search for available rooms based on specified filters and time slot.

    This endpoint allows users to search for available rooms based on filters such as floor number and capacity. Users
    can also specify a time slot (start and end time) to check room availability during that period.

    Query Parameters:
        - floor_number (int, optional): The floor number to filter rooms by.
        - capacity (int, optional): The minimum capacity required for the rooms.
        - start_time (str, required): The start time of the desired booking slot (in the format '%Y-%m-%d %H:%M:%S').
        - end_time (str, required): The end time of the desired booking slot (in the format '%Y-%m-%d %H:%M:%S').

    Returns:
        Flask Response: A JSON response containing the list of available rooms matching the specified filters.
    """
    try:
        floor_number = request.args.get('floor_number', type=int)
        capacity = request.args.get('capacity', type=int)
        start_time_str = request.args.get('start_time')
        end_time_str = request.args.get('end_time')
        start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')
        available_rooms = []
        for floor_number, floor_info in all_floors.items():
            rooms_on_floor = floor_info.get("rooms", {})

            for room_number, room_info in rooms_on_floor.items():
                # Check if the room matches the specified floor number (if provided)
                if floor_number == floor_number or floor_number is None:
                    # Check if the room matches the specified capacity (if provided)
                    if capacity is None or room_info["capacity"] >= capacity:
                        # Check if the room is available for the specified time slot
                        availability = is_room_available(all_bookings, floor_number, room_number, start_time, end_time)

                        # If available, add it to the results
                        if availability:
                            available_rooms.append({
                                "floor_number": floor_number,
                                "room_number": room_number,
                                "capacity": room_info["capacity"]
                            })
        return jsonify({"success": True, "data": available_rooms})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

###########  ORG  ROUTES  ###########

@app.route('/organizations', methods=['POST'])
def add_org():
    """
    Register a new organization in the conference room booking system.

    This endpoint allows administrators to register a new organization in the system. It checks if an organization with
    the same name already exists and adds the new organization if it's unique.

    Request Body:
        {
            "org_name" (str): The name of the organization (must be unique).
            ... (other organization details)
        }

    Returns:
        Flask Response: A JSON response indicating the success or failure of the operation.
    """
    try:
        with lock:
            data = request.get_json()
            data["org_name"] = data["org_name"].lower()
            if data["org_name"] in all_orgs:
                return jsonify({"success":False, "message": "Organization with the same name already exists."}), 400
            try:
                new_org = define_organization(**data)
            except KeyError:
                return jsonify({"success":False, "message": "Insufficient data provided."}), 400
            all_orgs[data["org_name"]] = new_org
            return jsonify({"success":True,  "message": "Organization added successfully"}), 201
    except Exception as e:
        return jsonify({"success":False, "message": str(e)}), 400

@app.route('/organizations', methods=['GET'])
def get_orgs():
    """
    Retrieve a list of all registered organizations in the conference room booking system.

    This endpoint allows users to retrieve a list of all registered organizations in the system. It returns the
    organization data, including organization names, as well as the total count of organizations.

    Returns:
        Flask Response: A JSON response containing the list of organizations and the total count of organizations.
    """
    try:
        return jsonify({"success": True, "data": list(all_orgs.values()), "count":len(all_orgs)})
    except Exception as e:
        return jsonify({"success":False, "message": str(e)}), 400

@app.route('/organizations/<string:org_name>', methods=['GET'])
def get_org(org_name):
    """
    Retrieve information about a specific organization in the conference room booking system.

    This endpoint allows users to retrieve information about a specific organization based on its name.
    It returns details about the organization, including its name, contact information, and a list of users
    associated with the organization.

    Args:
        org_name (str): The name of the organization to retrieve.

    Returns:
        Flask Response: A JSON response containing information about the specified organization.
    """
    org = all_orgs[org_name.lower()]
    org["users"] = list(org["users"].values())
    try:
        return jsonify({"success": True, "data": org})
    except Exception as e:
        return jsonify({"success":False, "message": str(e)}), 400


@app.route('/organizations/users', methods=['POST'])
def add_user():
    """
    Register a new user within an organization in the conference room booking system.

    This endpoint allows administrators to register a new user within a specific organization in the system.
    It checks if a user with the same email or employee ID already exists within the organization and adds
    the new user if both the email and employee ID are unique within the organization.

    Request Body:
        {
            "emp_id" (str): The employee ID of the user (must be unique within the organization).
            "email" (str): The email address of the user (must be unique within the organization).
            "organization" (str): The name of the organization to which the user belongs.
            "name" (str): The name of the user.
            "role" (str): Role of the user.
            "Permission" (str): Permissions assigned to the user.
        }

    Returns:
        Flask Response: A JSON response indicating the success or failure of the user registration.
    """
    try:
        data = request.get_json()
        with lock:
            data["email"] = data["email"].lower()
            data["emp_id"] = data["emp_id"].lower()
            email = data["email"]
            emp_id = data["emp_id"]
            organization = data["organization"]
            if organization not in all_orgs.keys():
                return jsonify({"success":False, "message": f"Organization {organization} not added"}), 400
            if is_email_unique(data["email"],all_orgs[organization]["users"]) == False:
                return jsonify({"success":False, "message": "User with the same email already exists."}), 400

            if is_emp_id_unique(data["emp_id"],all_orgs[organization]["users"]) == False:
                return jsonify({"success":False, "message": "User with the same emp_id already exists."}), 400

            try:
                new_user = define_user(**data)
            except KeyError:
                return jsonify({"success":False, "message": "Insufficient data provided."}), 400
            all_orgs[organization]["users"][email] = new_user
            return jsonify({"success":True,  "message": "User added successfully"}), 201
    except Exception as e:
        return jsonify({"success":False, "message": str(e)}), 400


@app.route('/organizations/<string:org_name>/users', methods=['GET'])
def get_users(org_name):
    """
    Retrieve a list of users belonging to a specific organization in the conference room booking system.

    This endpoint allows users to retrieve a list of all users belonging to a specific organization in the system.
    It returns user data, including details such as employee IDs, email addresses, roles, and permissions, for the
    organization. Additionally, it provides the total count of users within the organization.

    Args:
        org_name (str): The name of the organization for which to retrieve users.

    Returns:
        Flask Response: A JSON response containing the list of users and the total count of users within the organization.
    """
    try:
        return jsonify({"success": True, "data": list(all_orgs[org_name]["users"].values()), "count":len(all_orgs[org_name]["users"])})
    except Exception as e:
        return jsonify({"success":False, "message": str(e)}), 400


@app.route('/organizations/<string:org_name>/users/<string:email>', methods=['GET'])
def get_user(org_name, email):
    """
    Retrieve information about a specific user within an organization in the conference room booking system.

    This endpoint allows users to retrieve detailed information about a specific user within a particular organization
    in the system. It returns user data, including details such as employee IDs, email addresses, roles, and permissions.

    Args:
        org_name (str): The name of the organization to which the user belongs.
        email (str): The email address of the user to retrieve.

    Returns:
        Flask Response: A JSON response containing information about the specified user.
    """
    user = all_orgs.get(org_name)["users"][email.lower()]
    try:
        return jsonify({"success": True, "data": user})
    except Exception as e:
        return jsonify({"success":False, "message": str(e)}), 400


###########  BOOKING  ROUTES  ###########

@app.route('/bookings', methods=['POST'])
def add_boooking():
    """
    Create a new booking for a conference room in the conference room booking system.

    This endpoint allows users to create a new booking for a conference room in the system. It enforces several checks,
    including ensuring that the booking operates in hourly slots, that the specified floor and room exist, that the user
    belongs to a valid organization, and that the organization has not exceeded the 30-hour monthly booking limit.

    Args:
        None (Uses request data):
            - organization (str): The name of the organization making the booking.
            - floor_number (int): The floor number of the room to be booked.
            - room_number (int): The room number to be booked.
            - start_time (str): The start time of the booking in the format "%Y-%m-%d %H:%M:%S".
            - end_time (str): The end time of the booking in the format "%Y-%m-%d %H:%M:%S".
            - booked_by (dict): Information about the user making the booking, including name and email.

    Returns:
        Flask Response: A JSON response indicating whether the booking was successful or if there was an error.
    """
    try:
        with lock:
            reset_monthly_booking_hours(organization_booking_hours)
            data = request.get_json()
            start_time = datetime.strptime(data["start_time"], "%Y-%m-%d %H:%M:%S")
            end_time = datetime.strptime(data["end_time"], "%Y-%m-%d %H:%M:%S")
            data["start_time"] = start_time
            data["end_time"] = end_time
            organization = data["organization"].lower()
            if start_time.minute != 0 or start_time.second != 0 or end_time.minute != 0 or end_time.second != 0:
                return jsonify({"success":False, "message": "The booking system operates in hourly slots only. Please select start and end time to be a full hour"}), 400
            floor_number = data["floor_number"]
            if floor_number not in all_floors.keys():
                return jsonify({"success":False, "message": f"Floor {floor_number} not added"}), 400
            room_number = data["room_number"]
            if room_number not in all_floors[floor_number]["rooms"].keys():
                return jsonify({"success":False, "message": f"Room {room_number} not added"}), 400
            if data["booked_by"]["email"] not in all_orgs[organization]["users"].keys():
                return jsonify({"success":False, "message": f"No such user found"}), 400
            booking_duration = (end_time - start_time).total_seconds() / 3600
            if organization in organization_booking_hours:
                organization_booking_hours[organization] += booking_duration
            else:
                organization_booking_hours[organization] = booking_duration

            # Check if the organization has exceeded the 30-hour limit
            if organization_booking_hours[organization] > 30:
                return jsonify({"success":False, "message": f"Monthly limit of 30 hours of booking reached."}), 400

            if is_room_available(all_bookings=all_bookings, floor_number=floor_number, room_number=room_number, start_time=start_time, end_time=end_time) == False:
                return jsonify({"success":False, "message": "This room is already booked"}), 400

            try:
                new_booking = define_booking(**data)
            except KeyError:
                return jsonify({"success":False, "message": "Insufficient data provided."}), 400

            all_bookings[new_booking["booking_id"]] = new_booking
        return jsonify({"success": True, "message": "Room successfully booked.", "data": new_booking})
    except Exception as e:
        return jsonify({"success":False, "message": str(e)}), 400

@app.route('/organizations/<string:org_name>/bookings', methods=['GET'])
def get_bookings(org_name):
    """
    Retrieve all bookings for a specific organization in the conference room booking system.

    This endpoint allows users to retrieve a list of all bookings made by a specific organization. The organization's name
    is provided as a URL parameter, and the route returns a JSON response with the bookings' details.

    Args:
        org_name (str): The name of the organization for which bookings are to be retrieved.

    Returns:
        Flask Response: A JSON response containing the success status, the retrieved bookings' data, and the count of bookings.
    """
    try:
        bookings = list_bookings_for_organization(all_bookings, org_name)
        return jsonify({"success": True, "data": bookings, "count":len(bookings)})
    except Exception as e:
        return jsonify({"success":False, "message": str(e)}), 400

@app.route('/organizations/<string:org_name>/bookings/<string:booking_id>', methods=['GET'])
def get_booking(org_name, booking_id):
    """
    Retrieve a specific booking for a given organization by booking ID.

    This endpoint allows users to retrieve detailed information about a specific booking made by an organization.
    The organization's name and the booking ID are provided as URL parameters, and the route returns a JSON response
    with the booking's details.

    Args:
        org_name (str): The name of the organization that made the booking.
        booking_id (str): The unique identifier (booking ID) of the booking to retrieve.

    Returns:
        Flask Response: A JSON response containing the success status and the retrieved booking's data.
    """
    try:
        booking = get_booking_by_organization_and_id(organization_name=org_name.lower(), booking_id=booking_id)
        return jsonify({"success": True, "data": booking})
    except Exception as e:
        return jsonify({"success":False, "message": str(e)}), 400

@app.route('/organizations/<string:org_name>/bookings/<string:booking_id>', methods=['DELETE'])
def del_booking(org_name, booking_id):
    """
    Cancel a specific booking for a given organization by booking ID.

    This endpoint allows users to cancel a specific booking made by an organization using the booking's unique ID.
    The organization's name and the booking ID are provided as URL parameters. To successfully cancel a booking,
    the cancellation request must be made at least 15 minutes before the booking's start time.

    Args:
        org_name (str): The name of the organization that made the booking.
        booking_id (str): The unique identifier (booking ID) of the booking to be canceled.

    Returns:
        Flask Response: A JSON response indicating the success status and a message regarding the cancellation result.
    """
    try:
        with lock:
            if booking_id in all_bookings:
                booking = all_bookings[booking_id]
                
                # Check if the cancellation request is at least 15 minutes before the start_time
                current_time = datetime.now()
                start_time = booking["start_time"]
                if current_time < start_time - timedelta(minutes=15):
                    del all_bookings[booking_id]
                    return jsonify({"success": True, "message": "Booking cancelled."})
                else:
                    return jsonify({"success": False, "message": "Cancellation request must be at least 15 minutes before the start time."}), 400

            return jsonify({"success": False, "message": "Booking not found."}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)