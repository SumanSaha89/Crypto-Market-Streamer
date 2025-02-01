from confluent_kafka import Producer
import json
import logging

logger = logging.getLogger(__name__)

class KafkaManager:
    def __init__(self, bootstrap_servers, topic):
        self.topic = topic
        self.producer = None
        self.conf = {
            'bootstrap.servers': bootstrap_servers,
            'client.id': 'crypto_market_producer',
            'retries': 5,
            'acks': 'all'
        }
        self.connect()

    def connect(self):
        try:
            self.producer = Producer(self.conf)
            logger.info("Successfully connected to Kafka")
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {str(e)}")
            raise

    def send_message(self, message):
        try:
            self.producer.produce(
                self.topic,
                value=json.dumps(message).encode('utf-8'),
                callback=self.delivery_report
            )
            self.producer.poll(0)
        except Exception as e:
            logger.error(f"Failed to send message to Kafka: {str(e)}")
            self.reconnect()

    def delivery_report(self, err, msg):
        if err is not None:
            logger.error(f'Message delivery failed: {err}')
        else:
            logger.debug(f'Message delivered to {msg.topic()}')

    def reconnect(self):
        logger.info("Attempting to reconnect to Kafka...")
        self.producer = Producer(self.conf)