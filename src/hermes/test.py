from hermes.session.helpers import parsing_options
from hermes.session.main import get_trading_context

ctx = get_trading_context()
input = "chain AAPL"


parsing_options(ctx, input)
