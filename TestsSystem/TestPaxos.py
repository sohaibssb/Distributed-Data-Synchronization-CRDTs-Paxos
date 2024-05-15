import requests
import socketio
import time

class WebSocketUser:
    def __init__(self, node_urls):
        self.clients = {}
        for url in node_urls:
            client = socketio.Client()
            client.connect(url)
            self.clients[url] = client
            print(f"Узел, подключенный к {url}")

    def update_data(self, url, payload):
        """Send data through WebSocket to trigger Paxos update."""
        print(f"Отправка предложения на {url}: {payload}")
        self.clients[url].emit('update_data', payload)

    def disconnect_all(self):
        for client in self.clients.values():
            client.disconnect()
        print("Отключены все узлы")

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
                            print(f"Узел {url} количество принятых отчетов: {max_number}, Более низкое предложение отклонено")
                            return False
                        else:
                            print(f"Узел {url} сообщает о более высоком принятом числе: {max_number}, синхронизированных")
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
    print(f"Все узлы синхронизируются с числом {expected_number}.")
    return True

def main():
    node_urls = ["http://10.5.48.205:5000", "http://10.5.48.205:5001", "http://10.5.48.205:5002"]
    ws_client = WebSocketUser(node_urls)

    numbers_to_test = [800000, 300000]  # High and low values

    for number in numbers_to_test:
        print(f"Номер предложения: {number}")
        start_time = time.time()
        for url in node_urls:
            payload = {'имя': None, 'номер': number}
            ws_client.update_data(url, payload)
        
        time.sleep(2)

        if not check_synchronization(node_urls, number):
            print(f"Не удалось синхронизировать все узлы для номера {number}")
        else:
            sync_time = time.time() - start_time
            print(f"Все узлы синхронизированы с числом {number} в {sync_time:.4f} секундах")

    ws_client.disconnect_all()

if __name__ == '__main__':
    main()
