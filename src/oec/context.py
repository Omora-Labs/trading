from dataclasses import dataclass

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.trading.client import TradingClient


@dataclass
class TradingContext:
    client: TradingClient
    stock_data: StockHistoricalDataClient
    risk_pct: float
    is_paper: bool
    account_value: float
    risk_reward: float
