# Conference Room Booking System

## Overview

The Booking System Project is a Python-based application that allows organizations to manage their room bookings efficiently. This project provides a flexible and scalable solution for booking rooms within an organization, with features such as user registration, room booking, organization management, and more.

## Methodology and Data Representation

In this project, we have primarily used dictionaries (dicts) as our data structures to represent entities such as rooms, floors, organizations, and users. While this approach differs from traditional Object-Oriented Programming (OOP), it was chosen intentionally based on the project's requirements and goals.

**Why Dictionaries Over Objects:**

1. **Simplicity and Efficiency:** Dictionaries provide a straightforward and efficient way to manage and manipulate data. They are well-suited for smaller-scale projects where the complexity of defining and maintaining classes and objects may not be necessary.

2. **Flexibility:** Dicts offer flexibility in terms of data representation. You can easily add, modify, or remove attributes without the need to update class definitions or migrations.

3. **Data Serialization:** Dictionaries are a natural choice for data serialization and deserialization, making it simpler to work with data when reading from or writing to external sources like databases or JSON files.

4. **Interoperability:** Using dicts can enhance interoperability with external libraries and tools. For instance, dictionaries align well with the JSON format, which is widely used for data exchange.

While this project doesn't follow a strict Object-Oriented Programming paradigm, the decision to use dictionaries is in line with the project's objectives to keep code simple, efficient, and focused on achieving its core functionality.

Feel free to explore the codebase to see how dictionaries are used to represent and manipulate data efficiently.


## Installation

To run the Booking System Project, follow these steps:

1. **Clone the Repository**: Clone this repository to your local machine using `git clone`.

2. **Install Dependencies**: Use `pip` to install project dependencies. You can do this by running the following command:

```pip install -r requirements.txt```

3. **Run the Application**: Start the Flask application by running the main script:

```python app.py```

The application should now be running locally.

4. **API Documentation**: Refer to the provided Postman & Insomnia collections (`API collections`) for API endpoints and usage examples.

## Usage

The Booking System Project provides the following features:

- **User Management**: Administrators can register new users within an organization. The system checks for unique employee IDs and email addresses.

- **Organization Management**: Administrators can create and manage organizations. Organizations can join the booking system and manage their bookings.

- **Room Booking**: Users can book rooms within their organization. The system checks for room availability and organization booking limits.

- **Room and Floor Management**: Administrators can add and manage rooms and floors. The system calculates available capacity and ensures data integrity.

- **Booking Listing**: Users can list all available rooms or view their organization's bookings.

- **Booking Cancellation**: Users can cancel bookings, subject to a 15-minute cancellation policy.

## Contributors

- [Shubham Wani](https://github.com/bamwani)

## License

This project is licensed under the Apache License, Version 2.0 - see the [LICENSE](LICENSE) file for details.

