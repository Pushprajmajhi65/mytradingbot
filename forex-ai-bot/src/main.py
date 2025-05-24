import asyncio
import pandas as pd
import json
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
from telegram import Bot
from src.data.twelve_data import TwelveDataClient
from src.utils.config import Config
from openai import OpenAI
import logging

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TradingBot:
    def __init__(self):
        self.config = Config()
        self.data_client = TwelveDataClient(self.config.TWELVEDATA_KEY)
        self.telegram_bot = Bot(token=self.config.TELEGRAM_TOKEN)
        self.openai_client = OpenAI(api_key=self.config.OPENAI_API_KEY)

    async def analyze_market(self, symbol: str) -> dict:
        """Fetch data → Calculate indicators → Query OpenAI for decision"""
        try:
            df = self.data_client.get_historical_data(symbol)
            df['rsi'] = RSIIndicator(df['close'], window=14).rsi()
            df['ema_12'] = EMAIndicator(df['close'], window=12).ema_indicator()
            df['ema_26'] = EMAIndicator(df['close'], window=26).ema_indicator()
            latest = df.iloc[-1]

            prompt = f"""You are a forex trading assistant.
Given:
- Pair: {symbol}
- Price: {latest['close']}
- RSI: {latest['rsi']}
- EMA12: {latest['ema_12']}
- EMA26: {latest['ema_26']}

Respond ONLY in this exact JSON format:
{{"action": "BUY" | "SELL" | "HOLD", "units": 100, "reason": "short explanation"}}"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )

            content = response.choices[0].message.content.strip()

            # Strip markdown code blocks if present
            if content.startswith("```"):
                content = content.strip("`").split("json")[-1].strip()

            return json.loads(content)

        except Exception as e:
            logger.error(f"Analysis failed for {symbol}: {e}")
            return {"action": "HOLD", "reason": "Error"}

    async def execute_trade(self, symbol: str, decision: dict):
        """Send alert to Telegram"""
        message = (
            f"🚀 Trade Signal: {symbol}\n"
            f"Action: {decision['action']}\n"
            f"Reason: {decision['reason']}\n"
            f"Time: {pd.Timestamp.now()}"
        )
        await self.telegram_bot.send_message(
            chat_id=self.config.TELEGRAM_CHAT_ID,
            text=message
        )
        logger.info(f"Sent alert: {message}")

    async def run(self):
        while True:
            for symbol in self.config.SYMBOLS:
                decision = await self.analyze_market(symbol)
                if decision["action"] != "HOLD":
                    await self.execute_trade(symbol, decision)
            await asyncio.sleep(self.config.POLLING_INTERVAL)

if __name__ == "__main__":
    bot = TradingBot()
    asyncio.run(bot.run())