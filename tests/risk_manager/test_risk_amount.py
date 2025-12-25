from unittest.mock import Mock
from oec.risk_manager import define_risk_amount
from oec.main import TradingContext

def test_risk_amount():
    ctx = TradingContext(client=None, stock_data=Mock(), risk_pct=0.02, is_paper=True, account_value=50000, risk_reward=3)
    risk = define_risk_amount(ctx)
    assert risk == 1000  # 0.02 * 50000 = 1000
