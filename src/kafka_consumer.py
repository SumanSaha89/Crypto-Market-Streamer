from confluent_kafka import Consumer, KafkaError
import json
import logging
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_kafka_consumer(bootstrap_servers, topic):
    """Create a Kafka consumer and subscribe to a topic."""
    conf = {
        'bootstrap.servers': bootstrap_servers,
        'group.id': 'market-data-verification-group',
        'auto.offset.reset': 'earliest',  # Consume from the beginning if no offsets exist
        'enable.auto.commit': True,       # Automatically commit offsets
    }
    
    try:
        consumer = Consumer(conf)
        consumer.subscribe([topic])
        logger.info(f"Kafka consumer connected to {bootstrap_servers} and subscribed to topic: {topic}")
        return consumer
    except Exception as e:
        logger.error(f"Failed to create Kafka consumer: {e}")
        return None

def consume_market_data(consumer, duration=None):
    """Consume messages from Kafka and log them."""
    try:
        start_time = time.time()
        message_count = 0

        while True:
            msg = consumer.poll(1.0)  # Poll Kafka for messages

            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                logger.error(f"Consumer error: {msg.error()}")
                break

            try:
                # Decode and process the message
                market_data = json.loads(msg.value().decode('utf-8'))
                logger.info(f"Received Market Data:\n{json.dumps(market_data, indent=2)}")

                # Validate required fields
                if all(key in market_data for key in ["exchange", "symbol", "current_price"]):
                    logger.info("Data verification successful")
                else:
                    logger.warning("Data verification failed: Missing required fields")

                message_count += 1

                # Stop after duration
                if time.time() - start_time > duration:
                    break

            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode message: {e}")

    except KeyboardInterrupt:
        logger.info("Consumer interrupted by user.")
    except Exception as e:
        logger.error(f"Error consuming messages: {e}")
    finally:
        consumer.close()
        logger.info(f"✅ Consumed {message_count} messages in {duration} seconds.")

def validate_kafka_config(bootstrap_servers, topic):
    """Ensure Kafka configuration is valid."""
    if not bootstrap_servers:
        raise ValueError("KAFKA_BOOTSTRAP_SERVERS is not set.")
    if not topic:
        raise ValueError("KAFKA_TOPIC is not set.")

if __name__ == "__main__":
    try:
        # Load Kafka configuration from environment
        KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
        KAFKA_TOPIC = os.getenv('KAFKA_TOPIC')

        # Validate configuration
        validate_kafka_config(KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC)

        # Create and run the consumer
        consumer = create_kafka_consumer(KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC)
        if consumer:
            consume_market_data(consumer)
        else:
            logger.error("Failed to initialize Kafka consumer.")

    except Exception as e:
        logger.error(f"Error in main: {e}")
