from locust import HttpUser, task, between

class Node1User(HttpUser):
    wait_time = between(1, 2)
    host = "http://192.168.3.6:5000"  # Base URL for Node 1

    @task(1)  # CRDT task for names
    def add_name(self):
        self.client.post('/update_data', json={'name': 'Alice', 'number': None})

    @task(2)  # Paxos task for numbers
    def add_number(self):
        self.client.post('/update_data', json={'name': None, 'number': 2000})

    @task(3)  # Fetch data
    def fetch_data(self):
        self.client.get('/get_data')