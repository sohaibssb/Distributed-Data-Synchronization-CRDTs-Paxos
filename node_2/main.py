from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import sqlite3
import socket
import threading
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from collections import defaultdict, deque
from datetime import datetime, timedelta
import urllib3

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)
NODES = {
    "node1": "http://192.168.3.6:5000",
    "node2": "http://192.168.3.6:5001",
    "node3": "http://192.168.3.6:5002"
}
CURRENT_NODE = "node2" 
LEADER = None  
#LOAD_THRESHOLD = 100  # Threshold for high load
#TIME_WINDOW = 2  # Time window in minutes
#request_timestamps = deque()  # To hold request timestamps

REQUEST_COUNT = 0
HIGH_REQUEST =1000

# Network setup functions
def is_socket_online(host, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.connect((host, port))
        return True
    except socket.error:
        return False

def get_network_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80))
            return s.getsockname()[0]
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def get_port():
    ip_address = get_network_ip()
    if not ip_address:
        print("Unable to find IP. Service will stop.")
        exit()
    for port in range(5000, 5200):
        if not is_socket_online(ip_address, port):
            return port
    return port

# Used for Dynamic Method
@app.before_request
def before_request():
    global REQUEST_COUNT
    REQUEST_COUNT += 1

# Database setup functions
def create_connection():
    return sqlite3.connect(f'{CURRENT_NODE}.db') 

def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS person_names
                      (name_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS person_numbers
                      (number_id INTEGER PRIMARY KEY AUTOINCREMENT, number INTEGER)''')
    conn.commit()

with create_connection() as conn:
    create_tables(conn)

# CRDT Implementation for names and numbers
class CRDT:
    def __init__(self):
        self.added = set()
        self.removed = set()

    def insert(self, value, index=None):
        self.added.add((value, index))

    def delete(self, index):
        self.removed.add(index)

    def merge(self, other):
        self.added |= {(value, index) for value, index in other.added if index not in self.removed}
        self.removed |= {index for index in other.removed}

    def get_value(self):
        sorted_values = sorted(self.added, key=lambda x: x[1])
        return sorted_values[0][0] if sorted_values else ''

# Paxos Implementation for numbers
class Paxos:
    def __init__(self, num_nodes):
        self.num_nodes = num_nodes
        self.proposal_number = 0
        self.highest_promise = -1
        self.accepted_value = None
        self.accepted_proposal = -1
        self.promises = defaultdict(int)
        self.accepted_proposals = defaultdict(int)
        self.leader = None

    def prepare(self):
        self.proposal_number += 1
        return self.proposal_number

    def promise(self, proposal_number):
        if proposal_number > self.highest_promise:
            self.highest_promise = proposal_number
            return True, self.accepted_proposal, self.accepted_value
        return False, None, None

    def accept(self, proposal_number, value):
        if proposal_number >= self.highest_promise:
            self.highest_promise = proposal_number
            self.accepted_proposal = proposal_number
            self.accepted_value = value
            return True
        return False

    def learn(self):
        return self.accepted_value

    def reach_quorum(self, responses):
        return len([res for res in responses if res[0]]) >= (self.num_nodes // 2) + 1

    def elect_leader(self):
        sorted_nodes = sorted(NODES.keys())
        self.leader = sorted_nodes[self.proposal_number % len(sorted_nodes)]

# Person model class to integrate CRDT and Paxos data
class Person:
    def __init__(self, name, number, use_crdt_only=False):
        self.use_crdt_only = use_crdt_only
        self.name = CRDT()
        self.number = CRDT() if use_crdt_only else Paxos(len(NODES))
        if name:
            self.name.insert(name)
        if number is not None:
            if use_crdt_only:
                self.number.insert(number)
            else:
                self.number.accept(0, number)

    def save(self):
        with create_connection() as conn:
            cursor = conn.cursor()
            if self.name.get_value():
                cursor.execute("INSERT INTO person_names (name) VALUES (?)", (self.name.get_value(),))
            if self.use_crdt_only:
                cursor.execute("INSERT INTO person_numbers (number) VALUES (?)", (self.number.get_value(),))
            else:
                max_number = int(self.number.learn())
                cursor.execute("INSERT INTO person_numbers (number) VALUES (?)", (max_number,))
            conn.commit()

    @staticmethod
    def get_all(use_crdt_only=False):
        with create_connection() as conn:
            cursor = conn.cursor()
            if not use_crdt_only:
                cursor.execute("SELECT name FROM person_names")
            else:
                cursor.execute("SELECT name FROM person_names WHERE name NOT IN (SELECT name FROM person_numbers)")
            return cursor.fetchall()
        
    @staticmethod
    def switch_to_crdt_only():
        global USE_CRDT_ONLY
        USE_CRDT_ONLY = True        

# Paxos functions for proposer and acceptor
def proposer(paxos, value):
    paxos.elect_leader()
    if paxos.leader == CURRENT_NODE:
        proposal_number = paxos.prepare()
        promises = []
        for node_name, node_url in NODES.items():
            response = send_prepare_request(node_url, proposal_number)
            if response:
                promises.append(response)
        if paxos.reach_quorum(promises):
            for node_name, node_url in NODES.items():
                send_accept_request(node_url, proposal_number, value)

def send_prepare_request(node_url, proposal_number):
    try:
        response = requests.post(f"{node_url}/prepare", json={'proposal_number': proposal_number})
        if response.status_code == 200:
            return response.json()['promised'], response.json()['accepted_proposal'], response.json()['accepted_value']
    except requests.RequestException as e:
        print(f"Failed to send prepare request to {node_url}: {str(e)}")
    return None

def send_accept_request(node_url, proposal_number, value):
    try:
        response = requests.post(f"{node_url}/accept", json={'proposal_number': proposal_number, 'value': value})
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"Failed to send accept request to {node_url}: {str(e)}")
    return False

@app.route('/prepare', methods=['POST'])
def prepare_request():
    data = request.get_json()
    promised, accepted_proposal, accepted_value = paxos_instance.promise(data['proposal_number'])
    return jsonify({'promised': promised, 'accepted_proposal': accepted_proposal, 'accepted_value': accepted_value})

@app.route('/accept', methods=['POST'])
def accept_request():
    data = request.get_json()
    accepted = paxos_instance.accept(int(data['proposal_number']), int(data['value']))
    return jsonify({'accepted': accepted})

@app.route('/get_data', methods=['GET'])
def get_data():
    persons = Person.get_all()
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(number) FROM person_numbers")
        max_number = cursor.fetchone()[0]
    data = [{'name': person[0], "max_number": max_number} for person in persons]
    return jsonify({'data': data})

@app.route('/get_load', methods=['GET'])
def get_load():
    global REQUEST_COUNT
    return jsonify({'load': REQUEST_COUNT})


@app.route('/switch_to_crdt_only', methods=['POST'])
def switch_to_crdt_only():
    global REQUEST_COUNT
    initial_load = 1
    Person.switch_to_crdt_only()
    new_load = REQUEST_COUNT
    load_increased = new_load > initial_load
    if load_increased:
        REQUEST_COUNT = 0
    return jsonify({'message': 'Switched to using only CRDT for both names and numbers', 'load_increased': load_increased})


@app.route('/')
def index():
    ip = get_network_ip()
    data = {"ip": ip, "port": port}
    return render_template('index.html', data=data)

# Periodic data synchronization
def periodic_sync():
    print("Syncing data with other nodes...")
    proposer(paxos_instance, "new_value")
    threading.Timer(30, periodic_sync).start()



@socketio.on('update_data')
def update_data(data):
    if REQUEST_COUNT > HIGH_REQUEST:
        change_P_N = True
    else:
        change_P_N = False
    new_person = Person(data['name'], data['number'], change_P_N)
    new_person.save()
    socketio.emit('data_updated', data)
# Initialize Paxos with number of nodes


@socketio.on('get_socket_list')
def send_socket_list():
    ip_address = get_network_ip()

    if not ip_address:
        print("Unable to find IP. Service will stop.")
        exit()

    socket_list = [port for port in range(5000, 5200) if is_socket_online(ip_address, port)]
    socketio.emit('socket_list', {'sockets': socket_list})

@socketio.on('get_data')
def get_data_socket():
    persons = Person.get_all()
    data = [{'name': person[0]} for person in persons]
    socketio.emit('data', {'data': data})

@socketio.on('get_highest_number')
def get_highest_number():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(number) FROM person_numbers")
        max_number = cursor.fetchone()[0]
    socketio.emit('highest_number', {'number': max_number})
paxos_instance = Paxos(len(NODES))

@app.route('/data_transfer', methods=['GET'])
def hit_api_and_update_table():
    ip = get_network_ip()
    for i in range(5000, 6000):
        try:
            data = requests.get(f'http://{ip}:{i}/get_data')
        except (requests.exceptions.ConnectionError, urllib3.exceptions.NewConnectionError):
            continue

        try:
            response = data
            response.raise_for_status()
            data = response.json()
            person_names = {person['name'] for person in data['data']}
            with create_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM person_names")
                existing_names = {name for (name,) in cursor.fetchall()}
                new_names = person_names - existing_names
                if new_names:
                    cursor.executemany("INSERT INTO person_names (name) VALUES (?)", ((name,) for name in new_names))
                    conn.commit()
            max_number = [person['max_number'] for person in data['data']]
            if max_number:
                cursor.execute("SELECT MAX(number) FROM person_numbers")
                current_max_number = cursor.fetchone()[0]
                current_max_number = current_max_number if isinstance(
                    current_max_number, int) else 0
                if current_max_number < max(max_number):
                    if REQUEST_COUNT > HIGH_REQUEST:
                        change_P_N = True
                    else:
                        change_P_N = False
                    new_person = Person(None, max(max_number), change_P_N)
                    new_person.save()
        except Exception as error:
            pass
    return 'Done'

# Adding new route for Testing POST methods for CRDT, Posting names only
@app.route('/add_name', methods=['POST'])
def add_name():
    data = request.get_json()
    name = data.get('name') 

    if not name:
        return jsonify({'error': 'Name is required'}), 400  

    new_person = Person(name, None, use_crdt_only=True)
    new_person.save()

    return jsonify({'message': f'Name "{name}" added successfully'})


if __name__ == '__main__':
    port = 5001
    socketio.run(app, host='0.0.0.0', port=port)
