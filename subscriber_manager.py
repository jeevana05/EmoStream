from collections import defaultdict

class SubscriberManager:
    def __init__(self, subscriber_threshold=50):
        """
        Initializes the SubscriberManager with the given subscriber threshold.
        Each subscriber will accept up to `subscriber_threshold` clients before a new subscriber is created.
        """
        self.subscribers = defaultdict(list)  # Map of subscriber -> list of connected clients
        self.subscriber_threshold = subscriber_threshold
        self.active_subscribers = {}  # Map of subscriber -> connection details (e.g., WebSocket or HTTP info)
        self.client_subscriptions = {}  # Map of client_id -> subscriber

    def register_client(self, client_id):
        """
        Assigns a client to an available subscriber. Creates a new subscriber if all are full.
        """
        print(f"Registering client {client_id}...")  # Debugging log
        # Check if client is already registered
        if client_id in self.client_subscriptions:
            print(f"Client {client_id} is already registered to a subscriber.")
            return self.client_subscriptions[client_id]

        # Try to assign the client to an existing subscriber
        for subscriber, clients in self.subscribers.items():
            if len(clients) < self.subscriber_threshold:
                clients.append(client_id)
                self.client_subscriptions[client_id] = subscriber
                print(f"Client {client_id} assigned to existing subscriber {subscriber}.")
                return subscriber

        # Create a new subscriber if all current ones are full
        new_subscriber = f"subscriber_{len(self.subscribers) + 1}"
        self.subscribers[new_subscriber] = [client_id]
        self.client_subscriptions[client_id] = new_subscriber
        self.active_subscribers[new_subscriber] = None  # Placeholder for connection setup
        print(f"Created new subscriber {new_subscriber} and assigned client {client_id}.")
        return new_subscriber

    def set_active_subscriber(self, subscriber_name, connection):
        """
        Stores connection details for an active subscriber.
        """
        self.active_subscribers[subscriber_name] = connection
        print(f"Subscriber {subscriber_name} is now active with connection {connection}.")  # Debugging log

    def remove_client(self, client_id):
        """
        Removes a client from their assigned subscriber.
        """
        subscriber = self.client_subscriptions.pop(client_id, None)
        if not subscriber:
            print(f"Client {client_id} was not found.")
            return None
        
        # Remove the client from the subscriber's list
        self.subscribers[subscriber].remove(client_id)
        print(f"Client {client_id} removed from {subscriber}.")
        
        # Clean up empty subscriber if necessary
        if not self.subscribers[subscriber]:
            del self.subscribers[subscriber]
            del self.active_subscribers[subscriber]
            print(f"Subscriber {subscriber} is now empty and has been removed.")
        
        return subscriber

    def get_active_subscribers(self):
        """
        Returns a dictionary of active subscribers and their connections.
        """
        return self.active_subscribers

    def get_clients(self, subscriber_name):
        """
        Returns the list of clients connected to a specific subscriber.
        """
        return self.subscribers.get(subscriber_name, [])

# Example usage of SubscriberManager
if __name__ == "__main__":
    manager = SubscriberManager(subscriber_threshold=10)

    # Register clients
    for i in range(25):
        assigned_subscriber = manager.register_client(f"client_{i}")
        print(f"Client {i} assigned to {assigned_subscriber}")

    # Set active subscribers (mock connections)
    manager.set_active_subscriber("subscriber_1", {"connection": "WebSocket 1"})
    manager.set_active_subscriber("subscriber_2", {"connection": "WebSocket 2"})

    print("\nActive Subscribers:")
    print(manager.get_active_subscribers())

    print("\nClients in subscriber_1:")
    print(manager.get_clients("subscriber_1"))

    # Remove a client
    print("\nRemoving client_5...")
    removed_subscriber = manager.remove_client("client_5")
    print(f"Client removed from {removed_subscriber}")
    print(manager.get_clients(removed_subscriber))

