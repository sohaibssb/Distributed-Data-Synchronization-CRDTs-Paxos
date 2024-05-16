import requests
import time


nodes = {
    "http://10.5.48.205:5000": False,
    "http://10.5.48.205:5001": False,
    "http://10.5.48.205:5002": False
}

def is_node_online(node):
    """ Check if a node is online by attempting to fetch data from it. """
    try:
       
        response = requests.get(f"{node}/get_data", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def check_network_partition():
    """ Check each node and update their status, logging changes. """
    partition_info = {}
    for node in nodes:
        current_status = is_node_online(node)
        if nodes[node] != current_status:
            nodes[node] = current_status
            state = "online" if current_status else "offline"
            print(f"{node} has gone {state}.")
            partition_info[node] = state

    if len(partition_info) > 1:  
        print("Potential network partition detected:")
        for node, status in partition_info.items():
            print(f" - {node} is {status}")
    else:
        print("No significant changes detected.")

def monitor_nodes():
    """ Continuously monitor the nodes. """
    try:
        while True:
            check_network_partition()
            time.sleep(10)  
    except KeyboardInterrupt:
        print("Monitoring stopped.")

if __name__ == "__main__":
    monitor_nodes()
