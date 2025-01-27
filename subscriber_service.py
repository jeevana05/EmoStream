from flask import Flask, request
from flask_socketio import SocketIO, emit
from kafka import KafkaConsumer
import json
from threading import Thread

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # Allow cross-origin requests for WebSocket connections

# Active clients: client_id -> WebSocket session ID
connected_clients = {}

# Kafka Consumer setup
consumer = KafkaConsumer(
    'aggregated_emoji_topic',
    bootstrap_servers='localhost:9092',
    group_id='subscriber_group',
    auto_offset_reset='latest'
)

# WebSocket connection management
@socketio.on('connect')
def handle_connect():
    client_id = request.args.get("client_id")
    if client_id:
        connected_clients[client_id] = request.sid
        print(f"Client {client_id} connected with session ID {request.sid}.")
        emit('status', {'message': f'Connected to subscriber successfully as {client_id}'})
    else:
        print("Connection attempted without client_id.")
        emit('error', {'message': 'Client ID is required to connect.'})

@socketio.on('disconnect')
def handle_disconnect():
    # Remove disconnected client from the active list
    client_id = next((k for k, v in connected_clients.items() if v == request.sid), None)
    if client_id:
        del connected_clients[client_id]
        print(f"Client {client_id} disconnected.")
    else:
        print(f"Unknown session {request.sid} disconnected.")

# Kafka Consumer: Process messages from Kafka and broadcast to clients
def consume_and_broadcast():
    for message in consumer:
        try:
            # Parse Kafka message
            aggregated_data = json.loads(message.value)
            print(f"Received from Kafka: {aggregated_data}")  # Debugging log

            # Broadcast to all connected clients
            broadcast_to_clients(aggregated_data)
        except Exception as e:
            print(f"Error processing Kafka message: {e}")

def broadcast_to_clients(data):
    """
    Broadcast the given data to all connected clients.
    Prints emojis based on count, where for every 10, 1 emoji is printed.
    """
    emoji_type = data.get('emoji_type', '')
    count = data.get('count', 0)
    print_count = count // 10  # Determine how many times to print the emoji

    if print_count > 0:
        emoji_display = emoji_type * print_count  # Generate the string with emojis
        print(f"Broadcasting: {emoji_display}")  # Debugging log
    else:
        print(f"Broadcasting: No emojis to display for {emoji_type} with count {count}")  # Debugging log

    for client_id, session_id in connected_clients.items():
        try:
            print(f"Broadcasting to {client_id} (Session ID: {session_id})")  # Debugging log
            socketio.emit('update', data, to=session_id)
        except Exception as e:
            print(f"Failed to send data to client {client_id}: {e}")

if __name__ == '__main__':
    # Start the Kafka consumer in a separate thread
    kafka_thread = Thread(target=consume_and_broadcast)
    kafka_thread.daemon = True  # Ensure thread stops when the main program exits
    kafka_thread.start()

    # Start the WebSocket server
    print("Starting subscriber service...")
    socketio.run(app, port=5002)

