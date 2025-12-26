from dataclasses import dataclass

from alpaca.data.historical import OptionHistoricalDataClient, StockHistoricalDataClient
from alpaca.trading.client import TradingClient


@dataclass
class TradingContext:
    client: TradingClient
    stock_data: StockHistoricalDataClient
    option_data: OptionHistoricalDataClient
    risk_pct: float
    is_paper: bool
    account_value: float
    risk_reward: float
    risk_amount: float
