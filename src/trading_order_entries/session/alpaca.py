import asyncio
import os
from datetime import datetime
from typing import Tuple

from alpaca.data.historical import OptionHistoricalDataClient, StockHistoricalDataClient
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import PositionIntent
from alpaca.trading.stream import TradingStream
from dotenv import load_dotenv

from trading_analytics.processes.log_executions import (
    inserting_closing_executions,
    inserting_entry_executions,
)
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
            lock = order_locks.setdefault(order.id, asyncio.Lock())
            if order.filled_avg_price:
                print("Position opened!")
                print(f"   Filled Price: ${order.filled_avg_price}")

            if order.position_intent in [
                PositionIntent.BUY_TO_OPEN,
                PositionIntent.SELL_TO_OPEN,
            ]:
                pending = ctx.pending_orders[order.id]

                async with lock:
                    print("Logging entry executions...")
                    trade_id = inserting_entry_executions(ctx, order)

                risk_pct = assess_risk(
                    order.filled_avg_price,
                    pending["stop_loss_price"],
                    pending["qty"],
                    ctx,
                )

                ctx.risk_log.write(f"""
                    Risk for recent open positions {datetime.now()}:
                    Risk Pct: {risk_pct}%
                    Symbol: {order.symbol}

                    """)
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
                    trade_id=trade_id,
                )

                del ctx.pending_orders[order.id]

            else:  # it's buy or sell to close:
                async with lock:
                    print("Logging exit executions...")
                    trade_id = inserting_closing_executions(ctx, order)

        print()  # Add blank line after update

    trading_stream.subscribe_trade_updates(update_handler)
    await trading_stream._run_forever()
