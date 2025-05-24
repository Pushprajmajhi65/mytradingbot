# src/trading/demo_broker.py
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class Position:
    def __init__(self, symbol: str, action: str, units: int, entry_price: float, timestamp: datetime):
        self.symbol = symbol
        self.action = action  # BUY or SELL
        self.units = units
        self.entry_price = entry_price
        self.timestamp = timestamp
        self.exit_price: Optional[float] = None
        self.exit_timestamp: Optional[datetime] = None
        self.pnl: float = 0.0
        self.status = "OPEN"  # OPEN, CLOSED
    
    def close_position(self, exit_price: float, timestamp: datetime):
        self.exit_price = exit_price
        self.exit_timestamp = timestamp
        self.status = "CLOSED"
        
        # Calculate P&L
        if self.action == "BUY":
            self.pnl = (exit_price - self.entry_price) * self.units
        else:  # SELL
            self.pnl = (self.entry_price - exit_price) * self.units

class DemoBroker:
    def __init__(self, initial_balance: float = 10000.0):
        self.balance = initial_balance
        self.initial_balance = initial_balance
        self.positions: List[Position] = []
        self.trade_history: List[Dict] = []
        self.equity_curve: List[Dict] = []
    
    def execute_trade(self, symbol: str, action: str, units: int, current_price: float) -> bool:
        """Execute a demo trade"""
        try:
            # Create new position
            position = Position(
                symbol=symbol,
                action=action,
                units=units,
                entry_price=current_price,
                timestamp=datetime.now()
            )
            
            self.positions.append(position)
            
            # Log trade
            trade_record = {
                "timestamp": datetime.now(),
                "symbol": symbol,
                "action": action,
                "units": units,
                "price": current_price,
                "balance": self.balance
            }
            self.trade_history.append(trade_record)
            
            logger.info(f"Demo trade executed: {action} {units} {symbol} @ {current_price}")
            return True
            
        except Exception as e:
            logger.error(f"Trade execution failed: {e}")
            return False
    
    def update_positions(self, current_prices: Dict[str, float]):
        """Update P&L for open positions"""
        total_pnl = 0
        
        for position in self.positions:
            if position.status == "OPEN" and position.symbol in current_prices:
                current_price = current_prices[position.symbol]
                
                if position.action == "BUY":
                    unrealized_pnl = (current_price - position.entry_price) * position.units
                else:
                    unrealized_pnl = (position.entry_price - current_price) * position.units
                
                position.pnl = unrealized_pnl
                total_pnl += unrealized_pnl
        
        # Update equity curve
        current_equity = self.balance + total_pnl
        self.equity_curve.append({
            "timestamp": datetime.now(),
            "balance": self.balance,
            "equity": current_equity,
            "pnl": total_pnl
        })
    
    def get_portfolio_summary(self) -> Dict:
        """Get current portfolio status"""
        open_positions = [p for p in self.positions if p.status == "OPEN"]
        total_pnl = sum(p.pnl for p in open_positions)
        
        return {
            "balance": self.balance,
            "equity": self.balance + total_pnl,
            "unrealized_pnl": total_pnl,
            "open_positions": len(open_positions),
            "total_trades": len(self.trade_history),
            "win_rate": self._calculate_win_rate()
        }
    
    def _calculate_win_rate(self) -> float:
        closed_positions = [p for p in self.positions if p.status == "CLOSED"]
        if not closed_positions:
            return 0.0
        
        winning_trades = sum(1 for p in closed_positions if p.pnl > 0)
        return (winning_trades / len(closed_positions)) * 100