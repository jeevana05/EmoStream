from flask import Flask, request, jsonify
from pubsub_service import PubSubService

app = Flask(__name__)
pubsub_service = PubSubService()

# Define the WebSocket base URL for subscribers
WEBSOCKET_BASE_URL = "ws://localhost:5002/"  # Change the port if needed


@app.route('/register', methods=['POST'])
def register():
    """
    Handles the registration of a new client and assigns it to a subscriber.
    Returns the subscriber information and the WebSocket URL for communication.
    """
    print("Received registration request")  # Debugging log

    # Get the client_id from the JSON body
    client_id = request.json.get("client_id")
    if not client_id:
        print("Client ID is missing in the request.")  # Debugging log
        return jsonify({"error": "Client ID required"}), 400

    # Register the client and assign them to a subscriber
    assigned_subscriber = pubsub_service.register_client(client_id)
    print(f"Client {client_id} assigned to subscriber: {assigned_subscriber}")  # Debugging log

    # Provide the WebSocket URL for the assigned subscriber
    websocket_url = f"{WEBSOCKET_BASE_URL}{assigned_subscriber}?client_id={client_id}"
    print(f"WebSocket URL for client {client_id}: {websocket_url}")  # Debugging log

    # Return the response with the subscriber and WebSocket URL
    return jsonify({"subscriber": assigned_subscriber, "websocket_url": websocket_url})

@app.route('/unregister', methods=['POST'])
def unregister():
    """
    Endpoint for clients to unregister from their subscriber.
    """
    client_id = request.json.get("client_id")
    if not client_id:
        return jsonify({"error": "Client ID required"}), 400

    # Remove the client from their subscriber
    removed_subscriber = subscriber_manager.remove_client(client_id)

    if removed_subscriber:
        return jsonify({"status": f"Client {client_id} removed from {removed_subscriber}"}), 200
    else:
        return jsonify({"error": f"Client {client_id} not found"}), 400
        
if __name__ == '__main__':
    print("Starting registration server on port 5001...")  # Debugging log
    app.run(port=5001, debug=True)

