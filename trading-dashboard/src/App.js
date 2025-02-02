import React, { useState, useEffect, useRef } from 'react';
import { io } from 'socket.io-client';

const TradingViewer = () => {
  const listRef = useRef(null);
  const [symbol, setSymbol] = useState('');
  const [priceData, setPriceData] = useState({});
  const [socket, setSocket] = useState(null);
  const [exchanges] = useState(['mexc', 'bybit', 'kucoin']);
  const watchList = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT",
    "BTCUSDC", "ETHUSDC", "BNBUSDC",
    "SOLUSDT", "XRPUSDT", "ADAUSDT",
    "DOGEUSDT", "MATICUSDT", "LTCUSDT",
    "DOTUSDT", "AVAXUSDT", "UNIUSDT",
    "LINKUSDT", "ATOMUSDT", "FILUSDT",
    "TRXUSDT", "ETCUSDT", "APTUSDT",
    "ARBUSDT", "OPUSDT", "NEARUSDT",
    "QNTUSDT", "AAVEUSDT", "ALGOUSDT",
    "XLMUSDT", "BCHUSDT", "ICPUSDT"
  ];

  const normalizeSymbol = (symbol) => {
    return symbol.replace(/-/g, '').toUpperCase();
  };


  useEffect(() => {
    if (symbol) {
      const socketConnection = io('http://localhost:5000');
      setSocket(socketConnection);
      socketConnection.on(`price_update`, (data) => {
        console.log(data);
        const normalizedDataSymbol = normalizeSymbol(data.symbol);
        const normalizedSelectedSymbol = normalizeSymbol(symbol);

        if (exchanges.includes(data.exchange) && normalizedDataSymbol === normalizedSelectedSymbol) {
          setPriceData((prevData) => ({
            ...prevData,
            [data.exchange]: data,
          }));
        }
      });
      return () => {
        socketConnection.disconnect();
      };
    }
  }, [symbol, exchanges]);

  const handleSubmit = async (event) => {
    setPriceData({});
    setSymbol(event);
    const url = `http://localhost:5000/get_latest_price?symbol=${event}`;
    await fetch(url, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
  };

  return (
    <div className="bg-gray-900 text-white min-h-screen font-sans flex flex-col">
      <header className="bg-gray-800 p-4 flex items-center justify-between">
        <div className="flex items-center space-x-6">
          <span className="text-2xl font-bold text-blue-500">TRADING DATA</span>
        </div>
      </header>
      <div className="bg-gray-900 text-white min-h-screen font-sans flex flex-col">
      <div className="w-full bg-gray-800 p-4" ref={listRef}>
  <h3 className="text-xl text-center font-semibold mb-4 text-blue-400">Trading Pair List</h3>
  
  <div className="relative overflow-x-auto hide-scrollbar">
    <ul className="flex space-x-4">
      {watchList.map((item) => (
        <li
          onClick={() => handleSubmit(item)}
          key={item}
          className={`cursor-pointer flex-shrink-0 p-2 rounded-lg transition-colors duration-200 ${
            item === symbol
              ? "bg-blue-500 hover:bg-blue-600" // Highlighted style
              : "bg-gray-700 hover:bg-gray-600" // Default style
          }`}
        >
          <span className="font-medium">{item}</span>
        </li>
      ))}
    </ul>
  </div>
</div>


        <main className="flex-grow p-6">
          <h2 className="text-2xl font-semibold mb-6 text-blue-400">Exchange Data</h2>
          {symbol ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {exchanges.map((exchange) => {
                const data = priceData[exchange];
                return (
                  <div key={exchange} className="bg-gray-800 p-4 rounded-lg shadow-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xl text-gray-400 capitalize">{exchange}</span>
                    </div>
                    {data ? (
                      <div>
                        <div className="text-lg font-semibold">{symbol}</div>
                        <div className="text-xl text-gray-400">Current Price: ${data.current_price}</div>
                        <div className="text-xl text-gray-400">High: ${data.high_price}</div>
                        <div className="text-xl text-gray-400">Low: ${data.low_price}</div>
                      </div>
                    ) : (
                      <div className="text-sm text-gray-400">Waiting for data...</div>
                    )}
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="flex items-center justify-center h-64">
              <p className="text-gray-400 text-center">
                Please select a trading pair from the watchlist to view the market summary.
              </p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default TradingViewer;
