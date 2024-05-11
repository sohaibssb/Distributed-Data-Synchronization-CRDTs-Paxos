import requests
import random
import string
import time
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


def generate_name():
    """Generate a random 4-letter name."""
    return ''.join(random.choices(string.ascii_letters, k=4))

def post_data(node_url, name):
    """Post data to a single node and handle the response."""
    try:
        response = requests.post(f"{node_url}/add_name", json={"name": name}, timeout=10)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def check_synchronization(node_urls, delay=2):
    """Check if data is synchronized across all nodes."""
    while True:
        data_sets = []
        for url in node_urls:
            try:
                response = requests.get(f"{url}/get_data", timeout=10)
                data_sets.append(response.json())
            except requests.exceptions.RequestException:
                continue
        
        if all(data == data_sets[0] for data in data_sets):
            return True
        time.sleep(delay)

def run_test(node_urls, max_requests, step):
    synchronization_times = []
    request_counts = range(0, max_requests + step, step) 
    
    for count in request_counts:
        for _ in range(count):
            name = generate_name()
            for url in node_urls:
                post_data(url, name)
        
        start_time = time.time()
        if check_synchronization(node_urls):
            end_time = time.time()
            sync_time = end_time - start_time
            synchronization_times.append(sync_time)
            print(f"Synchronization for {count} requests per node took {sync_time:.4f} seconds.")
        else:
            synchronization_times.append(None)

    plt.figure(figsize=(10, 5))
    plt.plot(request_counts, synchronization_times, marker='o')
    plt.title('Время синхронизации VS нагрузка')
    plt.xlabel('Количество запросов на каждый узел')
    plt.ylabel('Время синхронизации (секунды)')
    plt.gca().yaxis.set_major_formatter(ticker.FormatStrFormatter('%.4f')) 
    plt.grid(True)
    plt.show()
    display_duration = 20  # In Seconds
    time.sleep(display_duration)
    plt.close()

    for req, time_sync in zip(request_counts, synchronization_times):
        print(f"{req} requests per node: {time_sync:.4f} seconds to synchronize.")

node_urls = ["http://10.5.48.205:5000/", "http://10.5.48.205:5001/", "http://10.5.48.205:5002/"]
max_requests = 200
step = 5 
run_test(node_urls, max_requests, step)


