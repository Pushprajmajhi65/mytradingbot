# Enhanced main trading bot
# src/bot/enhanced_trading_bot.py
import asyncio
import pandas as pd
import json
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
from telegram import Bot
from src.data.twelve_data import TwelveDataClient
from src.trading.demo_broker import DemoBroker
from src.utils.config import Config
from openai import OpenAI
import logging
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)

class EnhancedTradingBot:
    def __init__(self):
        self.config = Config()
        self.data_client = TwelveDataClient(self.config.TWELVEDATA_KEY)
        self.telegram_bot = Bot(token=self.config.TELEGRAM_TOKEN)
        self.openai_client = OpenAI(api_key=self.config.OPENAI_API_KEY)
        self.demo_broker = DemoBroker()
        self.market_data: Dict[str, pd.DataFrame] = {}
        self.current_prices: Dict[str, float] = {}
        
    async def analyze_market(self, symbol: str) -> dict:
        """Enhanced market analysis with more indicators"""
        try:
            df = self.data_client.get_historical_data(symbol)
            self.market_data[symbol] = df
            
            # Calculate indicators
            df['rsi'] = RSIIndicator(df['close'], window=14).rsi()
            df['ema_12'] = EMAIndicator(df['close'], window=12).ema_indicator()
            df['ema_26'] = EMAIndicator(df['close'], window=26).ema_indicator()
            
            # Additional indicators
            df['sma_50'] = df['close'].rolling(window=50).mean()
            df['bb_upper'] = df['close'].rolling(window=20).mean() + (df['close'].rolling(window=20).std() * 2)
            df['bb_lower'] = df['close'].rolling(window=20).mean() - (df['close'].rolling(window=20).std() * 2)
            
            latest = df.iloc[-1]
            self.current_prices[symbol] = latest['close']
            
            # Enhanced prompt with more context
            prompt = f"""You are an expert forex trading AI. Analyze this data:

Symbol: {symbol}
Current Price: {latest['close']:.5f}
RSI (14): {latest['rsi']:.2f}
EMA 12: {latest['ema_12']:.5f}
EMA 26: {latest['ema_26']:.5f}
SMA 50: {latest.get('sma_50', 0):.5f}
Bollinger Upper: {latest.get('bb_upper', 0):.5f}
Bollinger Lower: {latest.get('bb_lower', 0):.5f}

Previous 3 candles trend: {df['close'].tail(3).pct_change().mean():.4f}

Trading Rules:
- RSI > 70: Overbought (consider SELL)
- RSI < 30: Oversold (consider BUY)
- EMA12 > EMA26: Bullish trend
- Price near Bollinger bands: Potential reversal

Respond ONLY in JSON format:
{{"action": "BUY|SELL|HOLD", "units": 1000, "confidence": 0.75, "reason": "detailed explanation"}}"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            if content.startswith("```"):
                content = content.strip("`").split("json")[-1].strip()
            
            decision = json.loads(content)
            
            # Add market data to decision
            decision.update({
                "symbol": symbol,
                "price": latest['close'],
                "rsi": latest['rsi'],
                "timestamp": datetime.now().isoformat()
            })
            
            return decision
            
        except Exception as e:
            logger.error(f"Analysis failed for {symbol}: {e}")
            return {"action": "HOLD", "reason": "Analysis error", "confidence": 0.0}
    
    async def execute_trade(self, symbol: str, decision: dict):
        """Execute trade and send comprehensive alert"""
        if decision["action"] == "HOLD":
            return
            
        # Execute in demo broker
        success = self.demo_broker.execute_trade(
            symbol=symbol,
            action=decision["action"],
            units=decision.get("units", 1000),
            current_price=self.current_prices[symbol]
        )
        
        if success:
            # Get portfolio status
            portfolio = self.demo_broker.get_portfolio_summary()
            
            # Send detailed alert
            message = f"""🚀 TRADE EXECUTED
            
Symbol: {symbol}
Action: {decision['action']} {decision.get('units', 1000)} units
Price: {self.current_prices[symbol]:.5f}
Confidence: {decision.get('confidence', 0):.1%}
Reason: {decision['reason']}

📊 PORTFOLIO STATUS
Balance: ${portfolio['balance']:,.2f}
Equity: ${portfolio['equity']:,.2f}
Unrealized P&L: ${portfolio['unrealized_pnl']:,.2f}
Open Positions: {portfolio['open_positions']}
Total Trades: {portfolio['total_trades']}
Win Rate: {portfolio['win_rate']:.1f}%

📈 TECHNICAL DATA
RSI: {decision.get('rsi', 0):.1f}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

            await self.telegram_bot.send_message(
                chat_id=self.config.TELEGRAM_CHAT_ID,
                text=message
            )
            
            logger.info(f"Trade executed and alert sent for {symbol}")
    
    async def send_daily_summary(self):
        """Send daily portfolio summary"""
        portfolio = self.demo_broker.get_portfolio_summary()
        
        summary = f"""📊 DAILY PORTFOLIO SUMMARY
        
💰 Account Balance: ${portfolio['balance']:,.2f}
📈 Current Equity: ${portfolio['equity']:,.2f}
💹 Total P&L: ${portfolio['equity'] - self.demo_broker.initial_balance:,.2f}
📊 Win Rate: {portfolio['win_rate']:.1f}%
🔢 Total Trades: {portfolio['total_trades']}
🎯 Open Positions: {portfolio['open_positions']}

🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
        
        await self.telegram_bot.send_message(
            chat_id=self.config.TELEGRAM_CHAT_ID,
            text=summary
        )
    
    async def run(self):
        """Main trading loop"""
        logger.info("Enhanced Trading Bot started...")
        
        cycle_count = 0
        while True:
            try:
                # Update positions with current prices
                self.demo_broker.update_positions(self.current_prices)
                
                # Analyze each symbol
                for symbol in self.config.SYMBOLS:
                    decision = await self.analyze_market(symbol)
                    await self.execute_trade(symbol, decision)
                    await asyncio.sleep(2)  # Rate limiting
                
                cycle_count += 1
                
                # Send summary every 12 cycles (1 hour if 5min intervals)
                if cycle_count % 12 == 0:
                    await self.send_daily_summary()
                
                logger.info(f"Cycle {cycle_count} completed. Sleeping for {self.config.POLLING_INTERVAL} seconds...")
                await asyncio.sleep(self.config.POLLING_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error