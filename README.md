# Crypto Market Streamer

A real-time cryptocurrency market data streaming platform that aggregates live trading data from multiple major cryptocurrency exchanges (MEXC, ByBit, and KuCoin) through WebSocket connections. The application processes and streams this data through Apache Kafka for reliable data handling and provides a real-time interactive dashboard for market analysis.

## 🚀 Features

- **Multi-Exchange Integration**: Real-time WebSocket connections to MEXC, ByBit, and KuCoin
- **Live Data Streaming**: Continuous streaming of market data through Apache Kafka
- **Real-Time Dashboard**: Interactive web interface for monitoring live cryptocurrency prices
- **Price Analytics**: Track current prices, highs, lows, and floor prices across exchanges
- **Flexible Symbol Support**: Support for multiple trading pairs
- **Automated Recovery**: Built-in reconnection mechanisms for handling connection failures
- **Containerized Deployment**: Full Docker support for easy deployment and scaling

## 🏗️ Architecture

```
crypto-market-streamer/
├── src/                    # Backend Python application
│   ├── config.py          # Configuration settings
│   ├── kafka_consumer.py  # Kafka consumer implementation
│   ├── kafka_manager.py   # Kafka producer implementation
│   └── main.py           # Main application logic
├── trading-dashboard/     # Frontend React application
│   ├── public/
│   ├── src/
│   └── ...
└── docker/               # Docker configuration files
```

## 🔧 Prerequisites

- Docker and Docker Compose
- Node.js (v14 or higher)
- Python 3.9
- Git

## 🛠️ Installation & Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/crypto-market-streamer.git
cd crypto-market-streamer
```

2. **Configure environment variables**
```bash
cp .env.example .env
```
Update the `.env` file with your configuration:
```env
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC=crypto_market_data
RECONNECT_DELAY=5
MAX_RETRIES=5
MEXC_WS_URL=wss://wbs.mexc.com/ws
BYBIT_WS_URL=wss://stream.bybit.com/v5/public/spot
KUCOIN_WS_URL=wss://ws-api.kucoin.com
```

3. **Build and start the services**
```bash
docker-compose up --build
```

## 🌐 Accessing the Application

Once all services are running, you can access:

- **Trading Dashboard**: http://localhost:3000
- **Kafka UI**: http://localhost:8080
- **Backend API**: http://localhost:5000



## 📊 Available Trading Pairs

The application supports major cryptocurrency pairs including:
- BTCUSDT
- ETHUSDT
- BNBUSDT
- And many more...

## 🔍 Monitoring & Debugging

### Viewing Logs

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs kafka
```

### Health Checks

- Backend Health: http://localhost:5000/health
- Kafka UI: http://localhost:8080

## 🧪 Development Setup

### Running Services Locally

1. **Backend**
```bash
cd src
pip install -r requirements.txt
python src/main.py
```

2. **Frontend**
```bash
cd trading-dashboard
npm install
npm start
```

3. **Kafka Consumer**
```bash
python src/kafka_consumer.py
```

## 📝 API Documentation

### REST Endpoints

- `GET /get_latest_price`
  - Query Parameters:
    - `symbol` (required): Trading pair symbol (e.g., BTCUSDT)
  - Returns: Latest price data from all exchanges

### WebSocket Events

- `price_update`: Real-time price updates
  ```javascript
  {
    exchange: string,
    symbol: string,
    current_price: number,
    high_price: number,
    low_price: number
  }
  ```

## 🔒 Security Considerations

- API keys and secrets should be stored securely
- The application implements rate limiting for exchange APIs
- WebSocket connections are monitored for stability

## 🐛 Troubleshooting

Common issues and solutions:

1. **Kafka Connection Issues**
   - Verify Kafka service is running
   - Check broker configuration
   - Ensure correct ports are exposed

2. **WebSocket Connection Failures**
   - Check exchange API status
   - Verify network connectivity
   - Review rate limit status

## 📈 Performance

The application is designed to handle:
- Multiple concurrent WebSocket connections
- Real-time data processing
- Efficient message streaming
- Low-latency updates

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request


## 🙏 Acknowledgments

- MEXC Exchange API
- ByBit Exchange API
- KuCoin Exchange API
- Apache Kafka
- React.js Community