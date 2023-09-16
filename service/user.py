def define_user(name:str, organization:str, emp_id:str, email:str, role:str, permissions:str):
    """
    Define a user with the provided attributes.

    Args:
        name (str): The user's name.
        organization (str): The organization to which the user belongs.
        emp_id (str): The employee ID of the user.
        email (str): The email address of the user.
        role (str): The role of the user within the organization.
        permissions (str): The permissions associated with the user.

    Returns:
        dict: A dictionary representing the user with the provided attributes.
    """
    user = {
        "name": name,
        "organization": organization,
        "emp_id" : emp_id,
        "email" : email,
        "role" : role,
        "permissions" : permissions,
    }
    return user

def is_emp_id_unique(new_emp_id:str, user_list:list):
    """
    Check if a new employee ID is unique among the users in the list.

    Args:
        new_emp_id (str): The employee ID to check.
        user_list (list): The list of user dictionaries.

    Returns:
        bool: True if the employee ID is unique, False otherwise.
    """
    return all(user["emp_id"] != new_emp_id for user in user_list)

def is_email_unique(new_email:str, user_list:list):
    """
    Check if a new email address is unique among the users in the list.

    Args:
        new_email (str): The email address to check.
        user_list (list): The list of user dictionaries.

    Returns:
        bool: True if the email address is unique, False otherwise.
    """
    return all(user["email"] != new_email for user in user_list)