from dataclasses import dataclass, field
from typing import Dict

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
    account_currency: str
    risk_reward: float
    risk_amount: float
    pending_orders: Dict = field(default_factory=dict)
