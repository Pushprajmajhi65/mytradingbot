# src/data/twelve_data.py
import requests
import pandas as pd
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class TwelveDataClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.twelvedata.com"
    
    def get_historical_data(self, symbol: str, interval: str = "5min", outputsize: int = 100) -> pd.DataFrame:
        """Fetch historical forex data"""
        try:
            # Convert forex symbol format (EUR/USD -> EURUSD)
            clean_symbol = symbol.replace("/", "")
            
            url = f"{self.base_url}/time_series"
            params = {
                "symbol": clean_symbol,
                "interval": interval,
                "outputsize": outputsize,
                "apikey": self.api_key,
                "format": "JSON"
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if "values" not in data:
                logger.error(f"API Error: {data}")
                return self._generate_mock_data(symbol)
            
            df = pd.DataFrame(data["values"])
            df["datetime"] = pd.to_datetime(df["datetime"])
            df = df.set_index("datetime").sort_index()
            
            # Convert to numeric
            numeric_cols = ["open", "high", "low", "close", "volume"]
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            
            return df.dropna()
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return self._generate_mock_data(symbol)
    
    def _generate_mock_data(self, symbol: str) -> pd.DataFrame:
        """Generate mock data for demo purposes"""
        import numpy as np
        
        dates = pd.date_range(end=datetime.now(), periods=100, freq="5min")
        base_price = 1.1000 if "EUR" in symbol else 150.0
        
        # Generate realistic price movements
        returns = np.random.normal(0, 0.001, 100)
        prices = [base_price]
        
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))
        
        df = pd.DataFrame({
            "open": prices,
            "high": [p * (1 + abs(np.random.normal(0, 0.0005))) for p in prices],
            "low": [p * (1 - abs(np.random.normal(0, 0.0005))) for p in prices],
            "close": prices,
            "volume": np.random.randint(1000, 10000, 100)
        }, index=dates)
        
        return df