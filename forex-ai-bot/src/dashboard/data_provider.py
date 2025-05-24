# Dashboard data provider
# src/dashboard/data_provider.py

from flask import Flask, jsonify
from flask_cors import CORS
import json
from datetime import datetime
import threading
import time

class DashboardDataProvider:
    def __init__(self, trading_bot):
        self.app = Flask(__name__)
        CORS(self.app)
        self.trading_bot = trading_bot
        self.setup_routes()
    
    def setup_routes(self):
        @self.app.route('/api/portfolio')
        def get_portfolio():
            portfolio = self.trading_bot.demo_broker.get_portfolio_summary()
            return jsonify(portfolio)
        
        @self.app.route('/api/positions')
        def get_positions():
            positions = []
            for pos in self.trading_bot.demo_broker.positions:
                if pos.status == "OPEN":
                    positions.append({
                        "symbol": pos.symbol,
                        "action": pos.action,
                        "units": pos.units,
                        "entry_price": pos.entry_price,
                        "current_pnl": pos.pnl,
                        "timestamp": pos.timestamp.isoformat()
                    })
            return jsonify(positions)
        
        @self.app.route('/api/trades')
        def get_trades():
            return jsonify(self.trading_bot.demo_broker.trade_history[-10:])  # Last 10 trades
        
        @self.app.route('/api/equity-curve')
        def get_equity_curve():
            return jsonify(self.trading_bot.demo_broker.equity_curve[-50:])  # Last 50 points
        
        @self.app.route('/api/market-data/<symbol>')
        def get_market_data(symbol):
            if symbol in self.trading_bot.market_data:
                df = self.trading_bot.market_data[symbol].tail(50)  # Last 50 candles
                return jsonify({
                    "timestamps": df.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                    "prices": df['close'].tolist(),
                    "rsi": df.get('rsi', []).tolist()
                })
            return jsonify({"error": "No data available"})
    
    def run_server(self, host='localhost', port=5000):
        self.app.run(host=host, port=port, debug=False, threaded=True)