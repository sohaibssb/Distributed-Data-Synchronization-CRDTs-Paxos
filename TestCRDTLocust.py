# This file testing only one node performance via Locust

from locust import HttpUser, task, between
import random
import string

class FlaskLoadTester(HttpUser):
    wait_time = between(1, 2)  # wait time in seconds between tasks
    host = "http://10.5.48.205:5000" 

    @task
    def test_add_name_route(self):
        """Test the /add_name POST route to add a new CRDT name."""
        name = ''.join(random.choices(string.ascii_lowercase, k=4)) 
        payload = {"name": name} 

        self.client.post('/add_name', json=payload).raise_for_status()

    @task
    def test_get_data_route(self):
        """Test retrieving all data via HTTP GET."""
        self.client.get('/get_data').raise_for_status()

    @task
    def test_get_load_route(self):
        """Test retrieving the server load via HTTP GET."""
        self.client.get('/get_load').raise_for_status()
