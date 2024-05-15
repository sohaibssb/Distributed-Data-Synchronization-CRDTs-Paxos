import socketio
from faker import Faker
import requests
import time

# Create a Socket.IO client
sio = socketio.Client()

# Define the URL of the WebSocket server
url = 'http://10.5.48.205:5000/'  # Change this to match your WebSocket server URL

# Create a Faker instance
faker = Faker()
print("\033[1m*************** Start Testing *******************\033[0m")


# Event handler for 'connect' event
@sio.event
def connect():
    print('Connected to server')
    sio.emit('get_socket_list')  # Simulate 'get_socket_list' event
    sio.emit('get_data')  # Simulate 'get_data' event
    sio.emit('get_highest_number')  # Simulate 'get_highest_number' event
    send_fake_data()  # Send fake data after connecting

# Function to send fake data
def send_fake_data():
    name = faker.name()
    number = faker.random_number(digits=3)
    sio.emit('update_data', {'name': name, 'number': number})
    print('Sent fake data:', {'name': name, 'number': number}, "\n")

# Event handler for 'socket_list' event
@sio.event
def socket_list(data):
    print('Socket list received:', data, "\n")

# Event handler for 'data' event
@sio.event
def data(data):
    print('Data received:', data, "\n")

# Event handler for 'highest_number' event
@sio.event
def highest_number(data):
    print('Highest number received:', data, "\n")

# Function to disconnect from the server
def disconnect_from_server():
    sio.disconnect()
    print('Disconnect Connection from the server \n')

def test_all_apis(base_url):
    try:
        # Test /prepare
        response = requests.post(f"{base_url}/prepare", json={'proposal_number': 123})
        assert response.status_code == 200
        print("/prepare response:", response.json(), "\n")

        print("\033[1mData transfer occurs between every node and uses the Paxos algorithm to save the numbers.\033[0m")
        response = requests.get(f"{base_url}/data_transfer")
        assert response.status_code == 200
        print("/data_transfer response:", response.json(), "\n")


        # Test /accept
        response = requests.post(f"{base_url}/accept", json={'proposal_number': 123, 'value': 1})
        assert response.status_code == 200
        print("/accept response:", response.json())

        # Test /get_data
        response = requests.get(f"{base_url}/get_data")
        assert response.status_code == 200
        print("/get_data response:", response.json(), "\n")

        # Test /get_load
        print(" ***********  \033[1mHiting Server Request More than = 1000\033[0m  *********\n")

        for i in range(1000):
            response = requests.get(f"{base_url}/get_load")
            assert response.status_code == 200
        print("/get_load response:", response.json(), "\n")

        # Test /switch_to_crdt_only
        print("\033[1mSwiting the Paxos to CRDT alogrithm\033[0m\n")

        response = requests.post(f"{base_url}/switch_to_crdt_only")
        assert response.status_code == 200
        print("/switch_to_crdt_only response:", response.json(), "\n")

        # Test /data_transfer
        print("\033[1m Using CRDT algorithm to save the numbers.\033[0m")
        response = requests.get(f"{base_url}/data_transfer")
        assert response.status_code == 200
        print("/data_transfer response:", response.json(), "\n")

        print("\033[1mAll API tests passed successfully!\033[0m")

    except AssertionError:
        print("API test failed.")
    except requests.RequestException as e:
        print(f"An error occurred: {e}")

# Replace 'http://localhost:5000' with your actual base URL

if __name__ == '__main__':
    # Connect to the WebSocket server
    sio.connect(url)

    # Wait for events
    time.sleep(5)

    # Disconnect from the server
    test_all_apis(url)
    
    disconnect_from_server()
