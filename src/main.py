import asyncio
import json
import logging
import time
import aiohttp
import websockets
import sys
import os
import re
from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO
from flask_cors import CORS
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.kafka_manager import KafkaManager
from src.config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC, EXCHANGES, RECONNECT_DELAY, MAX_RETRIES
import requests
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000"]}})
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:3000"])

class ExchangeWebsocketClient:
    def __init__(self, exchange_name, config, kafka_manager):
        self.exchange_name = exchange_name
        self.ws_url = config['ws_url']
        self.symbol = config['symbol']
        self.ping_interval = config.get('ping_interval', 30)
        self.ping_message = config.get('ping_message')
        self.kafka_manager = kafka_manager
        self.connected = False
        self.retry_count = 0
        self.max_retries = MAX_RETRIES
        self.low_price = float('inf')
        self.high_price = float('-inf')
        self.floor_price = float('inf')
        self.current_price = None

    async def connect(self):
        while self.retry_count < self.max_retries:
            try:
                if self.exchange_name == 'kucoin':
                    self.ws_url = await self.get_kucoin_token()
                async with websockets.connect(self.ws_url) as websocket:
                    self.connected = True
                    self.retry_count = 0
                    self.low_price = float('inf')
                    self.high_price = float('-inf')
                    self.floor_price = float('inf')
                    logger.info(f"Connected to {self.exchange_name}")
                    await self.subscribe(websocket)
                    await self.message_handler(websocket)
            except Exception as e:
                logger.error(f"Connection error for {self.exchange_name}: {str(e)}")
                self.connected = False
                self.retry_count += 1
                await asyncio.sleep(RECONNECT_DELAY * self.retry_count)

    async def get_kucoin_token(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post("https://api.kucoin.com/api/v1/bullet-public") as response:
                    data = await response.json()
                    if data.get('code') == '200000':
                        token = data['data']['token']
                        endpoint = data['data']['instanceServers'][0]['endpoint']
                        return f"{endpoint}?token={token}"
                    raise Exception("Failed to get KuCoin token")
        except Exception as e:
            logger.error(f"Error getting KuCoin token: {str(e)}")
            raise

    async def subscribe(self, websocket):
        messages = {
            'mexc': json.dumps({"method": "SUBSCRIPTION", "params": [f"spot@public.deals.v3.api@{self.symbol}"]}),
            'bybit': json.dumps({"op": "subscribe", "args": [f"publicTrade.{self.symbol}"]}),
            'kucoin': json.dumps({"id": int(time.time()), "type": "subscribe", "topic": f"/market/match:{self.symbol}", "privateChannel": False, "response": True})
        }
        await websocket.send(messages[self.exchange_name])
        logger.info(f"Subscribed to {self.exchange_name} for {self.symbol}")

    async def message_handler(self, websocket):
        try:
            async for message in websocket:
                data = json.loads(message)
                price = None

                if self.exchange_name == 'mexc' and "d" in data and "deals" in data["d"]:
                    price = float(data["d"]["deals"][0]["p"])
                elif self.exchange_name == 'bybit' and data.get('topic') == f"publicTrade.{self.symbol}":
                    price = float(data['data'][0]['p'])
                elif self.exchange_name == 'kucoin' and data.get('type') == 'message':
                    price = float(data['data']['price'])

                if price:
                    self.current_price = price
                    self.low_price = min(self.low_price, price)
                    self.high_price = max(self.high_price, price)
                    self.floor_price = min(self.floor_price, price)

                    trade_data = {
                        "exchange": self.exchange_name,
                        "symbol": self.symbol,
                        "current_price": self.current_price,
                        "low_price": self.low_price,
                        "high_price": self.high_price,
                        "floor_price": self.floor_price
                    }                    
                    # Send to Kafka
                    self.kafka_manager.send_message(trade_data)
                    # Emit to WebSocket clients using global socketio instance
                    socketio.emit("price_update", trade_data)

        except Exception as e:
            logger.error(f"Error in message_handler for {self.exchange_name}: {str(e)}")
            self.connected = False
    def get_prices(self):
        return {
            "exchange": self.exchange_name,
            "low_price": self.low_price,
            "high_price": self.high_price,
            "floor_price": self.floor_price
        }
active_clients = {}

def extract_quote_currency(symbol):
    """
    Extract the quote currency (e.g., USDT, USDC, BTC) from the symbol.
    Assumes the quote currency is at the end of the symbol.
    """
    # Match common quote currencies (e.g., USDT, USDC, BTC, ETH, etc.)
    match = re.search(r'(USDT|USDC|BTC|ETH|BNB|SOL|XRP|ADA|DOGE|MATIC|LTC|DOT|AVAX|UNI|LINK|ATOM|FIL|TRX|ETC|APT|ARB|OP|NEAR|QNT|AAVE|ALGO|XLM|BCH|ICP)$', symbol)
    if match:
        return match.group(1)
    return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_latest_price', methods=['GET'])
def get_latest_price():
    symbol = request.args.get('symbol')
    if not symbol:
        return jsonify({'error': 'Symbol is required'}), 400
    
    try:
        # Extract the quote currency (e.g., USDT, USDC, BTC, etc.)
        quote_currency = extract_quote_currency(symbol)
        if not quote_currency:
            return jsonify({'error': 'Invalid symbol format'}), 400
        
        # Update exchange configurations with the new symbol
        for exchange in EXCHANGES:
            if exchange == 'kucoin':
                # Convert symbol to KuCoin format (e.g., BTCUSDT -> BTC-USDT)
                base_currency = symbol[:-len(quote_currency)]  # Extract base currency
                EXCHANGES[exchange]['symbol'] = f"{base_currency}-{quote_currency}"
            else:
                # Keep the symbol as is for Bybit and MEXC
                EXCHANGES[exchange]['symbol'] = symbol

        # Stop existing clients if any
        for client in active_clients.values():
            client.connected = False
        active_clients.clear()

        # Initialize Kafka manager
        kafka_manager = KafkaManager(KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC)

        # Create new clients with updated symbols
        for exchange, config in EXCHANGES.items():
            active_clients[exchange] = ExchangeWebsocketClient(exchange, config, kafka_manager)

        def start_background_tasks():
            async def run_clients():
                try:
                    await asyncio.gather(*(client.connect() for client in active_clients.values()))
                except Exception as e:
                    logger.error(f"Error in run_clients: {str(e)}")

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(run_clients())
            loop.close()

        socketio.start_background_task(start_background_tasks)

        return jsonify({
            'status': 'success',
            'message': f'WebSocket connections established for symbol {symbol}',
            'exchanges': {
                exchange: {
                    'symbol': config['symbol'],
                    'ws_url': config['ws_url']
                } for exchange, config in EXCHANGES.items()
            }
        })

    except Exception as e:
        logger.error(f"Error in get_latest_price: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected')

if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)