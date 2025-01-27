from flask import Flask, request, jsonify
from kafka import KafkaProducer
from threading import Timer
import json

app = Flask(__name__)

# Kafka producer setup
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Buffer and flush interval
message_buffer = []
FLUSH_INTERVAL = 0.5  # 500ms

def flush_messages():
    global message_buffer
    if message_buffer:
        print(f"Flushing {len(message_buffer)} messages to Kafka.")
        for message in message_buffer:
            producer.send('emoji_topic', message)
        producer.flush()
        message_buffer = []  # Clear the buffer
    Timer(FLUSH_INTERVAL, flush_messages).start()

# Start the buffer flush timer
flush_messages()

@app.route('/send-emoji', methods=['POST'])
def send_emoji():
    print("Received emoji data request.")  # Debugging log
    data = request.get_json()
    user_id = data.get("user_id")
    emoji_type = data.get("emoji_type")
    timestamp = data.get("timestamp")

    if not user_id or not emoji_type or not timestamp:
        return jsonify({"error": "Invalid data"}), 400

    # Append message to the buffer
    message_buffer.append({
        "user_id": user_id,
        "emoji_type": emoji_type,
        "timestamp": timestamp
    })

    print(f"Added emoji to buffer: {data}")  # Debugging log
    return jsonify({"status": "Message received"}), 200

if __name__ == '__main__':
    app.run(port=5000)

