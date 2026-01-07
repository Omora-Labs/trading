from unittest.mock import Mock

from trading_order_entries.context import TradingContext
from trading_order_entries.trading.risk_manager import define_take_profit_price


def test_take_profit_buy():
    risk_pct = 0.01
    account_value = 10000
    risk_reward = 3
    ctx = TradingContext(
        client=None,
        stock_data=Mock(),
        option_data=None,
        db=Mock(),
        account_id=1,
        risk_pct=risk_pct,
        is_paper=True,
        account_value=account_value,
        risk_reward=risk_reward,
        risk_amount=risk_pct * account_value,
        account_currency="USD",
    )
    tp = define_take_profit_price(ctx, entry_price=100, stop_loss_price=98, side="buy")
    assert tp == 106  # delta=2, reward=2*3=6, 100+6=106


def test_take_profit_sell():
    risk_pct = 0.01
    account_value = 10000
    risk_reward = 3
    ctx = TradingContext(
        client=None,
        stock_data=Mock(),
        option_data=None,
        db=Mock(),
        account_id=1,
        risk_pct=risk_pct,
        is_paper=True,
        account_value=account_value,
        risk_reward=risk_reward,
        risk_amount=risk_pct * account_value,
        account_currency="USD",
    )
    tp = define_take_profit_price(
        ctx, entry_price=100, stop_loss_price=102, side="sell"
    )
    assert tp == 94  # delta=2, reward=2*3=6, 100-6=94
