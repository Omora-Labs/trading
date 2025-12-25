from unittest.mock import Mock
from oec.risk_manager import define_take_profit_price
from oec.main import TradingContext

def test_take_profit_buy():
    ctx = TradingContext(client=None, stock_data=Mock(), risk_pct=0.01, is_paper=True, account_value=10000, risk_reward=3)
    tp = define_take_profit_price(ctx, entry_price=100, stop_loss_price=98, side="buy")
    assert tp == 106  # delta=2, reward=2*3=6, 100+6=106

def test_take_profit_sell():
    ctx = TradingContext(client=None, stock_data=Mock(), risk_pct=0.01, is_paper=True, account_value=10000, risk_reward=3)
    tp = define_take_profit_price(ctx, entry_price=100, stop_loss_price=102, side="sell")
    assert tp == 94  # delta=2, reward=2*3=6, 100-6=94
