from trading_order_entries.context import TradingContext
from trading_order_entries.session.alpaca import get_account_value, get_alpaca_clients
from trading_order_entries.session.session import setup_session


def get_trading_context() -> TradingContext:
    is_paper, risk_pct, risk_reward = setup_session()
    client, stock_data, option_data = get_alpaca_clients(is_paper)
    account_value, account_currency, account_nr = get_account_value(client)

    return TradingContext(
        client=client,
        stock_data=stock_data,
        option_data=option_data,
        risk_pct=risk_pct,
        is_paper=is_paper,
        account_id=None,
        account_nr=account_nr,
        account_value=account_value,
        account_currency=account_currency,
        risk_reward=risk_reward,
        risk_amount=risk_pct * account_value,
        risk_log=None,
    )
