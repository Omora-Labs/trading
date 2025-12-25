import os

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.trading.client import TradingClient
from alpaca.trading.stream import TradingStream
from dotenv import load_dotenv
from prompt_toolkit.shortcuts import prompt, radiolist_dialog
from prompt_toolkit.validation import ValidationError, Validator

from .context import TradingContext
from .order_entry import handle_order_entry


class SideValidator(Validator):
    def validate(self, document):
        if document.text.split()[1].lower() not in ["buy", "sell"]:
            raise ValidationError(message="Side must be buy or sell")


async def update_handler(data):
    # trade updates will arrive in our async handler
    trading_stream = TradingStream(api_key, secret_key, paper=is_paper)
    trading_stream.subscribe_trade_updates(update_handler)
    trading_stream.run()
    print(data)


if __name__ == "__main__":
    load_dotenv()

    is_paper = radiolist_dialog(
        title="Trading Mode",
        text="Select trading mode:",
        values=[(True, "Paper"), (False, "Live")],
    ).run()

    risk_pct = float(prompt("Risk Percentage ", default="0.25")) / 100

    risk_reward = float(prompt("Risk/Reward Ratio ", default="5"))

    api_key = (
        os.environ["ALPACA_API_KEY_PAPER"]
        if is_paper
        else os.environ["ALPACA_API_KEY_LIVE"]
    )
    secret_key = (
        os.environ["ALPACA_SECRET_KEY_PAPER"]
        if is_paper
        else os.environ["ALPACA_SECRET_KEY_LIVE"]
    )

    client = TradingClient(api_key, secret_key, paper=is_paper, raw_data=False)
    stock_data = StockHistoricalDataClient(api_key, secret_key)

    ctx = TradingContext(
        client=client,
        stock_data=stock_data,
        risk_pct=risk_pct,
        is_paper=is_paper,
        account_value=float(client.get_account().last_equity or 0),
        risk_reward=risk_reward,
    )

    while True:
        order_input = prompt(
            "Enter order (e.g., 'AAPL buy 143'): ", validator=SideValidator()
        )

        symbol, side, stop_loss = order_input.split()
        stop_loss_price = float(stop_loss)
        handle_order_entry(ctx, side, stop_loss_price, symbol)
