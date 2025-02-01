import os
from dotenv import load_dotenv
import json

load_dotenv()

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'crypto_market_data')
RECONNECT_DELAY = int(os.getenv('RECONNECT_DELAY'))
MAX_RETRIES = int(os.getenv('MAX_RETRIES'))

# Exchange Configuration
EXCHANGES = {
    'mexc': {
        'ws_url': os.getenv('MEXC_WS_URL'),
        'symbol': os.getenv('MEXC_SYMBOL', 'BTCUSDT'),
        'ping_interval': 30,
        'ping_message': json.dumps({"method": "PING"})
    },
    'bybit': {
        'ws_url': os.getenv('BYBIT_WS_URL'),
        'symbol': os.getenv('BYBIT_SYMBOL', 'BTCUSDT'),
        'ping_interval': 30,
        'ping_message': json.dumps({"op": "ping"})
    },
    'kucoin': {
        'ws_url': os.getenv('KUCOIN_WS_URL'),
        'symbol': os.getenv('KUCOIN_SYMBOL', 'BTC-USDT'),
        'ping_interval': 30,
        'ping_message': json.dumps({"type": "ping"})
    }
}