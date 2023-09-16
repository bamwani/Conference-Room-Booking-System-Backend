def define_floor(floor_number:int):
    """
    Define a floor with the provided floor number and an initial capacity of 100.

    Args:
        floor_number (int): The unique floor number.

    Returns:
        dict: A dictionary representing the floor with floor_number and an empty rooms dictionary.
    """
    floor = {
        "floor_number" : floor_number,
        "capacity" : 100,
        "rooms" : {},
    }
    return floor

def calculate_available_capacity(floor:dict):
    """
    Calculate the available capacity on a floor based on the rooms added to the floor.

    Args:
        floor (dict): A dictionary representing a floor, including its rooms.

    Returns:
        int: The available capacity on the floor after subtracting the used capacity by existing rooms.
    """
    used_capacity = 0
    for room in floor["rooms"].keys():
        print(floor["rooms"][room]["capacity"])
        used_capacity+= floor["rooms"][room]["capacity"]
    return floor["capacity"] - used_capacity