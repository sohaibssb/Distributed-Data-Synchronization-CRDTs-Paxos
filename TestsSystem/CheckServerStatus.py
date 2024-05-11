import requests

def check_server(url):
    try:
        response = requests.get(url)
        print('Server status:', response.status_code)
    except requests.exceptions.RequestException as e:
        print('Failed to connect:', e)

check_server('http://10.5.48.205:5000/')
