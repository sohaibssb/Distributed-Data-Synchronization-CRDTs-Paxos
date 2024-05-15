import requests
import socketio
import time
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

class WebSocketUser:
    def __init__(self, node_urls):
        self.clients = {}
        for url in node_urls:
            client = socketio.Client()
            client.connect(url)
            self.clients[url] = client
            print(f"Connected to WebSocket at {url}")

    def update_data(self, url, payload):
        """Send data through WebSocket to trigger Paxos update."""
        print(f"Sending data to {url}: {payload}")
        self.clients[url].emit('update_data', payload)

    def disconnect_all(self):
        for client in self.clients.values():
            client.disconnect()
        print("Disconnected all WebSockets.")

def check_synchronization(node_urls, expected_number):
    """Check if all nodes have synchronized to the expected maximum number."""
    for url in node_urls:
        try:
            response = requests.get(f"{url}/get_data")
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and data['data']:
                    max_numbers = [int(d['max_number']) for d in data['data'] if 'max_number' in d]
                    if max_numbers:
                        max_number = max(max_numbers)
                        if max_number != expected_number:
                            return False
                    else:
                        print(f"No max_number found in data from {url}")
                        return False
                else:
                    print(f"No data found in response from {url}")
                    return False
            else:
                print(f"Bad response {response.status_code} from {url}")
                return False
        except Exception as e:
            print(f"Error checking data from {url}: {e}")
            return False
    return True

def main():
    node_urls = ["http://10.5.48.205:5000", "http://10.5.48.205:5001", "http://10.5.48.205:5002"]
    ws_client = WebSocketUser(node_urls)

    synchronization_times = []
    request_counts = range(0, 201, 5)  # Generates requests from 0 to 200 in steps of 5
    current_number = 2000  # Starting number

    try:
        for count in request_counts:
            start_time = time.time()
            for i, url in enumerate(node_urls):
                current_max = current_number + count * 500 + i * 100 
                payload = {'name': None, 'number': current_max}
                ws_client.update_data(url, payload)
            time.sleep(0.5)  


            expected_max = current_number + count * 500 + (len(node_urls) - 1) * 100
            while not check_synchronization(node_urls, expected_max):
                time.sleep(0.5)  

            sync_time = time.time() - start_time
            synchronization_times.append(sync_time)
            print(f"Synchronization for {count} requests per node took {sync_time:.4f} seconds.")

    finally:
        ws_client.disconnect_all()

    plt.figure(figsize=(10, 5))
    plt.plot(request_counts, synchronization_times, marker='o')
    plt.title('Время синхронизации VS нагрузка')
    plt.xlabel('Количество запросов на каждый узел')
    plt.ylabel('Время синхронизации (секунды)')
    plt.grid(True)
    plt.show()

if __name__ == '__main__':
    main()
