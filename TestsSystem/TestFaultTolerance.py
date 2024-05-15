import requests
import time

def is_node_online(node):
    """ Check if a node is online by sending a simple GET request. """
    try:
        response = requests.get(f"{node}/get_data", timeout=5)  # Timeout to ensure prompt response
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"Error contacting {node}: {e}")
        return False

def fetch_data_from_node(node):
    """ Fetch data from a node to compare for synchronization. Includes error handling. """
    try:
        response = requests.get(f"{node}/get_data", timeout=5)
        if response.status_code == 200:
            return response.json()['data']  # Assuming the response contains a 'data' key
        else:
            print(f"Error fetching data from {node}: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Error fetching data from {node}: {e}")
        return None

def check_data_synchronization(nodes):
    """ Check if data is synchronized across all online nodes. """
    data_from_nodes = [fetch_data_from_node(node) for node in nodes if is_node_online(node)]
    if not data_from_nodes or any(data is None for data in data_from_nodes):
        print("No data available or one of the nodes failed to respond for synchronization check.")
        return False
    
    # Extracting names and comparing sets of names across nodes to ensure synchronization
    first_node_data_set = set(item['name'] for item in data_from_nodes[0])
    for node_data in data_from_nodes[1:]:
        current_data_set = set(item['name'] for item in node_data)
        if current_data_set != first_node_data_set:
            print("Data mismatch found. Synchronization error detected.")
            return False
    
    print("Data across all nodes is synchronized.")
    return True

def monitor_nodes(nodes):
    while True:
        print("Checking node statuses...")
        all_nodes_online = True
        for node in nodes:
            if not is_node_online(node):
                all_nodes_online = False
                print(f"{node} is offline.")
        
        if all_nodes_online:
            print("All nodes are online. Checking data synchronization...")
            check_data_synchronization(nodes)
        else:
            print("Not all nodes are online, skipping synchronization check...")

        time.sleep(10)  # Check every 10 seconds

if __name__ == "__main__":
    nodes = [
        "http://10.5.48.205:5000",
        "http://10.5.48.205:5001",
        "http://10.5.48.205:5002"
    ]
    monitor_nodes(nodes)
