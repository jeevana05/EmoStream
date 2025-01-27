from kafka import KafkaConsumer, KafkaProducer
from subscriber_manager import SubscriberManager
import json

class PubSubService:
    def __init__(self):
        self.consumer = KafkaConsumer(
            'aggregated_emoji_topic',
            bootstrap_servers=['localhost:9092'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='emoji_consumer_group',
            auto_offset_reset='earliest'
        )
        self.producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.manager = SubscriberManager(subscriber_threshold=2)  # Limit to 2 clients per subscriber

    def register_client(self, client_id):
        return self.manager.register_client(client_id)

    def distribute(self):
        for message in self.consumer:
            data = message.value
            for subscriber, clients in self.manager.subscribers.items():
                self.producer.send(subscriber, data)  # Publish to subscribers

if __name__ == "__main__":
    service = PubSubService()
    service.distribute()
