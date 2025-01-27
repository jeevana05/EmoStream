import requests
import random
import time
from datetime import datetime
from threading import Thread, Lock

# Global lock for thread-safe operations
lock = Lock()

# Subscriber manager to keep track of clients and their assigned subscribers
subscribers = {}
max_clients_per_subscriber = 2

def register_client(client_id):
    print(f"Registering client {client_id}...")  # Debugging log
    response = requests.post("http://localhost:5001/register", json={"client_id": client_id})
    print(f"Client {client_id} registration response: {response.status_code}, {response.json()}")  # Debugging log
    return response.json().get("subscriber")

def send_emoji(client_id):
    emoji_type = random.choice(["😀", "😢", "❤️", "🔥", "👍"])
    timestamp = datetime.now().isoformat()
    data = {
        "user_id": client_id,
        "emoji_type": emoji_type,
        "timestamp": timestamp
    }
    print(f"Client {client_id} sending emoji: {data}")  # Debugging log
    response = requests.post("http://localhost:5000/send-emoji", json=data)
    print(f"Client {client_id} sent emoji response: {response.status_code}, {response.json()}")  # Debugging log

def client_thread(client_id):
    subscriber = register_client(client_id)
    if subscriber:
        with lock:
            if subscriber not in subscribers:
                subscribers[subscriber] = []
            subscribers[subscriber].append(client_id)

        for _ in range(20):
            send_emoji(client_id)
            time.sleep(0.1)

        # Simulate client leaving
        with lock:
            subscribers[subscriber].remove(client_id)
            if not subscribers[subscriber]:  # Remove subscriber if no clients left
                del subscribers[subscriber]

if __name__ == "__main__":
    threads = []
    for i in range(8):  # Simulate 8 clients
        client_id = f"client_{random.randint(1, 1000)}"
        thread = Thread(target=client_thread, args=(client_id,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print("Final subscriber states:", subscribers)

