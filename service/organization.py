from datetime import datetime, timedelta


def define_organization(org_name:str, org_email:str):
    """
    Define an organization with the provided organization name, organization email,
    and an empty users dictionary.

    Args:
        org_name (str): The unique name of the organization.
        org_email (str): The email address associated with the organization.

    Returns:
        dict: A dictionary representing the organization with org_name, org_email, and an empty users dictionary.
    """
    organization = {
        "org_name" : org_name,
        "org_email" : org_email,
        "limit"
        "users" : {}
    }
    return organization


def reset_monthly_booking_hours(organization_booking_hours):
    """
    Reset the monthly booking hours for all organizations on the first day of each month.

    Args:
        organization_booking_hours (dict): A dictionary tracking booking hours for each organization.

    Returns:
        None
    """
    # Get the current date
    current_date = datetime.now()

    # Check if it's the first day of the month
    if current_date.day == 1:
        # Reset booking hours for all organizations
        organization_booking_hours.clear()
