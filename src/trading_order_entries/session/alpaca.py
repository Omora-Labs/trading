import os
from datetime import datetime
from typing import Tuple

import polars as pl
from alpaca.data.historical import OptionHistoricalDataClient, StockHistoricalDataClient
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import PositionIntent
from alpaca.trading.stream import TradingStream
from dotenv import load_dotenv

from trading_order_entries.context import TradingContext
from trading_order_entries.trading.orders.main import handle_exit_orders
from trading_order_entries.trading.risk_manager import assess_risk

order_locks = {}


def _get_api_keys(is_paper) -> Tuple:
    load_dotenv()

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

    return api_key, secret_key


def get_alpaca_clients(is_paper: bool, raw_data: bool = False) -> Tuple:
    api_key, secret_key = _get_api_keys(is_paper)
    client = TradingClient(api_key, secret_key, paper=is_paper, raw_data=raw_data)
    stock_data = StockHistoricalDataClient(api_key, secret_key)
    option_data = OptionHistoricalDataClient(api_key, secret_key)

    return client, stock_data, option_data


def get_account_value(client: TradingClient) -> Tuple:
    account = client.get_account()
    account_value = float(account.equity or 0)
    account_currency = account.currency
    account_nr = account.account_number

    return account_value, account_currency, account_nr


async def start_stream(ctx: TradingContext) -> None:
    api_key, secret_key = _get_api_keys(ctx.is_paper)
    trading_stream = TradingStream(api_key, secret_key, paper=ctx.is_paper)

    async def update_handler(data):
        order = data.order

        print(f"\n Order Update: {data.event.upper()}")
        print(
            f"   Symbol: {order.symbol} | Side: {order.side.value} | Type: {order.type.value}"
        )
        print(f"   Qty: {order.qty} | Status: {order.status.value}")
        if order.limit_price:
            print(f"   Limit Price: ${order.limit_price}")
        if order.stop_price:
            print(f"   Stop Price: ${order.stop_price}")

        if data.event == "fill":
            if order.filled_avg_price:
                print("Position opened!")
                print(f"   Filled Price: ${order.filled_avg_price}")

            if order.position_intent in [
                PositionIntent.BUY_TO_OPEN,
                PositionIntent.SELL_TO_OPEN,
            ]:
                pending = ctx.pending_orders[order.id]

                risk_pct = assess_risk(
                    float(order.filled_avg_price),
                    float(pending["stop_loss_price"]),
                    int(pending["qty"]),
                    ctx,
                    is_options=pending["is_options"],
                )

                ctx.risk_log.write(
                    "NEW POSITION:\n"
                    + pl.DataFrame(
                        {
                            "Symbol": [order.symbol],
                            "Opened At": [datetime.now()],
                            "Risk Pct %": [round(risk_pct, 2)],
                        }
                    ).__str__()
                    + "\n\n"
                )
                ctx.risk_log.flush()  # type: ignore

                print("Creating exit orders...")
                handle_exit_orders(
                    ctx,
                    side=pending["side"],
                    symbol=pending["symbol"],
                    qty=pending["qty"],
                    stop_loss_price=pending["stop_loss_price"],
                    take_profit_price=pending["take_profit_price"],
                    is_options=pending["is_options"],
                )

                del ctx.pending_orders[order.id]

        print()  # Add blank line after update

    trading_stream.subscribe_trade_updates(update_handler)
    await trading_stream._run_forever()
