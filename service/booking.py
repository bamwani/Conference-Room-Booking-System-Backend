from uuid import uuid4


def define_booking(floor_number, room_number, organization, booked_by, start_time, end_time):
    """
    Define a booking with the provided details.

    Args:
        floor_number (int): The floor number where the booking is made.
        room_number (int): The room number within the floor.
        organization (str): The name of the organization making the booking.
        booked_by (dict): Information about the user who booked the room.
        start_time (datetime): The start time of the booking.
        end_time (datetime): The end time of the booking.

    Returns:
        dict: A dictionary representing the booking with unique booking_id.
    """
    booking = {
        "booking_id": str(uuid4()),
        "floor_number": floor_number,
        "room_number": room_number,
        "organization": organization,
        "booked_by": booked_by,
        "start_time": start_time,
        "end_time": end_time
    }
    return booking

def is_room_available(all_bookings, floor_number, room_number, start_time, end_time):
    """
    Check if a room is available for booking within the specified time slot.

    Args:
        all_bookings (dict): A dictionary containing all bookings.
        floor_number (int): The floor number where the room is located.
        room_number (int): The room number within the floor.
        start_time (datetime): The start time of the desired booking.
        end_time (datetime): The end time of the desired booking.

    Returns:
        bool: True if the room is available; False if it's already booked during the specified time slot.
    """
    # Get the bookings for the specified floor and room
    floor_bookings = [booking for booking in all_bookings.values() if booking["floor_number"] == floor_number and booking["room_number"] == room_number]

    # Check if the room is available for the specified time slot
    for booking in floor_bookings:
        if start_time < booking["end_time"] and end_time > booking["start_time"]:
            return False  # Room is already booked for the specified time slot
    return True  # Room is available

def available_rooms_of_floor(all_bookings, floor_number, start_time, end_time):
    """
    Get a list of available room numbers on a specific floor for a given time slot.

    Args:
        all_bookings (dict): A dictionary containing all bookings.
        floor_number (int): The floor number to check for available rooms.
        start_time (datetime): The start time of the desired booking.
        end_time (datetime): The end time of the desired booking.

    Returns:
        list: A list of available room numbers on the specified floor.
    """
    available_rooms = []
    # Get the rooms on the specified floor
    rooms_on_floor = all_floors.get(floor_number, {}).get("rooms", {})
    
    for room_number, room_info in rooms_on_floor.items():
        if is_room_available(all_bookings, floor_number, room_number, start_time, end_time):
            available_rooms.append(room_number)
    
    return available_rooms

def list_all_available_rooms(all_bookings, start_time, end_time):
    """
    Get a list of all available rooms across all floors for a given time slot.

    Args:
        all_bookings (dict): A dictionary containing all bookings.
        start_time (datetime): The start time of the desired booking.
        end_time (datetime): The end time of the desired booking.

    Returns:
        list: A list of dictionaries representing available rooms with floor and room numbers.
    """
    available_rooms = []
    
    for floor_number, floor_info in all_floors.items():
        rooms_on_floor = floor_info.get("rooms", {})
        
        for room_number, room_info in rooms_on_floor.items():
            if is_room_available(all_bookings, floor_number, room_number, start_time, end_time):
                available_rooms.append({"floor_number": floor_number, "room_number": room_number})
    
    return available_rooms

def list_bookings_for_organization(all_bookings, organization_name):
    """
    Get a list of bookings made by a specific organization.

    Args:
        all_bookings (dict): A dictionary containing all bookings.
        organization_name (str): The name of the organization to filter bookings.

    Returns:
        list: A list of bookings made by the specified organization.
    """
    bookings_for_organization = []
    
    for booking_id, booking in all_bookings.items():
        if booking["organization"].lower() == organization_name:
            bookings_for_organization.append(booking)
    return bookings_for_organization

def get_booking_by_organization_and_id(organization_name, booking_id):
    """
    Get a specific booking by organization name and booking ID.

    Args:
        organization_name (str): The name of the organization associated with the booking.
        booking_id (str): The unique ID of the booking to retrieve.

    Returns:
        dict or None: The booking dictionary if found; None if not found.
    """
    for booking in all_bookings.values():
        if booking["organization"] == organization_name and booking["booking_id"] == booking_id:
            return booking
    return None