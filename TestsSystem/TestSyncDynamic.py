import socketio
import time
import matplotlib.pyplot as plt
import requests

class WebSocketUser:
    def __init__(self, nodes, max_requests, step):
        self.nodes = nodes
        self.max_requests = max_requests
        self.step = step
        self.sio_clients = {node: socketio.Client() for node in nodes}
        self.sync_times = []
        self.connect_all_nodes()

    def connect_all_nodes(self):
        for node, client in self.sio_clients.items():
            @client.event
            def connect():
                print(f"Connected to {node}")

            @client.event
            def disconnect():
                print(f"Disconnected from {node}")

            client.connect(node, wait_timeout=10)

    def send_and_verify_data(self):
        num_requests = self.step
        while num_requests <= self.max_requests:
            start_time = time.time() 
            print(f"Sending {num_requests} requests per node...")
            for node, client in self.sio_clients.items():
                for i in range(num_requests):
                    data = {'name': f'TestUser {num_requests * 1 + i}', 'number': num_requests * 1 + i} # was 100 100 
                    if client.connected:
                        client.emit('update_data', data)
                        #print(f"Sending data to {node}: {data}")

            synchronized = False
            while not synchronized:
                time.sleep(5)  
                synchronized = self.verify_sync()
                if not synchronized:
                    print("Data not synchronized, waiting...")
                else:
                    sync_time = time.time() - start_time
                    self.sync_times.append(sync_time)
                    print(f"Data synchronized correctly for {num_requests} requests. Synchronization time: {sync_time:.4f} seconds.")
            num_requests += self.step

    def verify_sync(self):
        all_data = [self.fetch_data_from_node(node) for node in self.nodes]
        if None not in all_data and all(set(entry['name'] for entry in data['data']) == set(entry['name'] for entry in all_data[0]['data']) for data in all_data):
            return True
        return False

    def fetch_data_from_node(self, node):
        try:
            response = requests.get(f'{node}/get_data')
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            print(f"Error fetching data from {node}: {e}")
            return None

    def disconnect_all(self):
        for client in self.sio_clients.values():
            if client.connected:
                client.disconnect()
                print("WebSocket disconnected")

    def plot_sync_times(self):
        if not self.sync_times:
            print("No synchronization times recorded.")
            return
        x_values = range(self.step, self.max_requests + 1, self.step)
        plt.figure(figsize=(10, 5))
        plt.plot(x_values, self.sync_times, marker='o', linestyle='-', color='b')
        plt.title('Время синхронизации VS нагрузка')
        plt.xlabel('Количество запросов на каждый узел')
        plt.ylabel('Время синхронизации (секунды)')
        plt.grid(True)
        plt.show()

def main():
    nodes = ["http://10.5.48.205:5000", "http://10.5.48.205:5001", "http://10.5.48.205:5002"]
    max_requests = 600
    step = 150
    ws_client = WebSocketUser(nodes, max_requests, step)
    try:
        ws_client.send_and_verify_data()
    finally:
        ws_client.disconnect_all()
        ws_client.plot_sync_times()

if __name__ == '__main__':
    main()
