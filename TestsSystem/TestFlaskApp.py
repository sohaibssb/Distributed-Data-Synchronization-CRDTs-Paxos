import unittest
import requests


class TestFlaskApp(unittest.TestCase):

    def setUp(self):
        self.base_url = 'http://10.5.48.205:5000/'

    def test_index_route(self):
        response = requests.get(f'{self.base_url}/')
        self.assertEqual(response.status_code, 200)

    def test_prepare_route(self):
        response = requests.post(
            f'{self.base_url}/prepare', json={'proposal_number': 1})
        self.assertEqual(response.status_code, 200)

    def test_accept_route(self):
        response = requests.post(
            f'{self.base_url}/accept', json={'proposal_number': 1, 'value': 5})
        self.assertEqual(response.status_code, 200)

    def test_get_data_route(self):
        response = requests.get(f'{self.base_url}/get_data')
        self.assertEqual(response.status_code, 200)

    def test_get_load_route(self):
        response = requests.get(f'{self.base_url}/get_load')
        self.assertEqual(response.status_code, 200)

    def test_switch_to_crdt_only_route(self):
        response = requests.post(f'{self.base_url}/switch_to_crdt_only')
        self.assertEqual(response.status_code, 200)

    def test_invalid_route(self):
        response = requests.get(f'{self.base_url}/invalid_route')
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()