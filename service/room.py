from datetime import datetime
from service.booking import is_room_available

def define_room(room_number:int, capacity:str, floor_number:str):
    """
    Define a room with the provided room number, capacity, and floor number.

    Args:
        room_number (int): The unique room number.
        capacity (int): The capacity of the room.
        floor_number (int): The floor number where the room is located.

    Returns:
        dict: A dictionary representing the room with room_number, capacity, and floor_number.
    """
    room = {
        "room_number" : room_number,
        "capacity" : capacity,
        "floor_number" : floor_number,
    }
    return room

def list_rooms_with_availability(all_floors, all_bookings, start_time=None, end_time=None):
    """
    List all rooms with their availability status for a specified time slot.

    Args:
        all_floors (dict): A dictionary containing information about all floors and their rooms.
        all_bookings (dict): A dictionary containing all booking information.
        start_time (datetime, optional): The start time of the time slot. Defaults to current time.
        end_time (datetime, optional): The end time of the time slot. Defaults to current time.

    Returns:
        list: A list of dictionaries representing rooms with their availability status.
    """
    if start_time is None:
        start_time = datetime.now()
    if end_time is None:
        end_time = start_time

    rooms_with_availability = []
    
    for floor_number, floor_info in all_floors.items():
        rooms_on_floor = floor_info.get("rooms", {})
        
        for room_number, room_info in rooms_on_floor.items():
            availability = is_room_available(all_bookings, floor_number, room_number, start_time, end_time)
            room_info["currently_available"] = availability
            rooms_with_availability.append({"floor_number": floor_number, "room_info": room_info})
    
    return rooms_with_availability