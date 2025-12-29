from hermes.context import TradingContext
from hermes.session.alpaca import get_account_value, get_alpaca_clients
from hermes.session.session import setup_session


def get_trading_context() -> TradingContext:
    is_paper, risk_pct, risk_reward = setup_session()
    client, stock_data, option_data = get_alpaca_clients(is_paper)
    account_value, account_currency = get_account_value(client)

    session_type = "Paper" if is_paper else "Live"

    print(f"Starting a {session_type} session now... \n")

    return TradingContext(
        client=client,
        stock_data=stock_data,
        option_data=option_data,
        risk_pct=risk_pct,
        is_paper=is_paper,
        account_value=account_value,
        account_currency=account_currency,
        risk_reward=risk_reward,
        risk_amount=risk_pct * account_value,
    )
