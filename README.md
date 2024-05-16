# Distributed-Data-Synchronization-CRDTs-Paxos
Develop Dynamic Method for data consistency in distributed systems using advantages of CRDTs and Paxos Algorithms

Programmed by Sohaibssb for Master degree research under subject "Methods of Syncretization Data in Distribution System" at Bauman University (МГТУ им. Н. Э. Баумана), Moscow. 2023/2024.

------------------

About the Dynamic method:

This program presents and implements a method that combines the strengths of conflict-free replicated data types (CRDT) and Paxos algorithms, offering a dynamic approach to data consistency in distributed systems.

------------------

Libraries and Tchnologies used on this project:

Python, Flask, Flask-SocketIO, Flask-CORS, SQLite Database, Requests, Requests.adapters, urllib3.util, Collections, Threading, Time, Socket, HTML, CSS, JavaScript, WebSocket.

APIs:
- RESTful API routes created with Flask.
- HTTP communication via requests (prepare and accept phases).

JSON/HTTP Communication:
- JSON request and response formats using Flask's request and jsonify
- requests.post() and requests.get() for HTTP communication

------------------------------------------------------------

## Setup Instructions

1. Activate Virtual Environment: It's recommended to use a virtual environment to manage dependencies.
2. Install dependencies: "pip install -r requirements.txt".
3. Open separate terminal windows for each node and run Flask application "python main.py".
4. Access the application at `http://localhost:<port>` where `<port>` is the port number displayed in the console.

## Application Structure

- `main.py`: Contains the Flask application with Socket.IO integration.
- `templates/index.html`: HTML template for the home page.


## Functionality

- **CRDT (Conflict-free Replicated Data Types)**: Used for ensuring eventual consistency of person names across distributed systems.
- **Paxos**: Used for achieving consensus on the highest account number.
- **Socket.IO**: Enables real-time updates of data between clients and the server.

## API Endpoints

- `/`: Home page that displays the IP address and port of the server.
- `/get_data`: Returns all persons' data from the database.
- Socket.IO events:
- `update_data`: Updates the database with a new person's data.
- `get_socket_list`: Retrieves a list of active nodes (sockets).
- `get_data`: Sends all persons' data to the client.

## Example Usage

1. Open the application in a web browser.
2. Add a new person's name and account number.
3. The data will be synchronized in real-time with other connected clients.

## Instructions for Controlling the Dynamic Method

You can adjust the "HIGH_REQUEST" variable in main.py to control the dynamic method for data synchronization. When the number of incoming requests to the server reaches the value set in HIGH_REQUEST, the system will switch to using only CRDT for synchronizing all the data instead of using CRDT and Paxos. 

- REQUEST_COUNT = 0: Keeps track of all incoming requests made to the application.
- HIGH_REQUEST = 50: Threshold for switching to CRDT-only mode.
- USE_CRDT_ONLY = False: Indicates whether the system is currently using CRDT-only mode for data synchronization.
