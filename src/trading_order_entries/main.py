import asyncio
import os

import polars as pl
from alpaca.trading.requests import GetOrdersRequest
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.shortcuts import PromptSession

from trading_analytics.processes.log_account_info import (
    get_account_id,
    log_account_info,
    log_account_snapshots,
)
from trading_order_entries.options.main import parsing_options
from trading_order_entries.session.alpaca import start_stream
from trading_order_entries.session.main import get_trading_context
from trading_order_entries.trading.orders.main import handle_order_entry
from trading_order_entries.utils import (
    arranging_orders_for_printing,
    arranging_positions_for_printing,
)


async def main(ctx):
    session_details = f"""
    Trading Mode: {"Paper" if ctx.is_paper else "Live"}
    Risk Percentage: {ctx.risk_pct * 100}%
    Risk Reward: {ctx.risk_reward}
    Methods:
        * <orders> lists all standing orders
        * <positions> lists all positions
        * <SPY buy 123 321> to buy AAPL with stop loss 123 and limit price of 321
        * <SPY sell 123 321> to short AAPL with stop loss 123 and limit price of 321
        * <chain SPY> to list option expiries and create an option order
        * <help> to list available methods
        * <exit> to leave
    """

    print("\033]0;Omora Labs: Trading\007", end="")  # Set terminal title
    os.system("clear")
    print(
        f"""
            {session_details}
        """
    )

    print(f"Account ID is {ctx.account_id} and account nr is {ctx.account_nr}")

    with patch_stdout():
        background_task = asyncio.create_task(start_stream(ctx))
        session = PromptSession()

        try:
            while True:
                try:
                    input = await session.prompt_async("> ")

                    if input == "orders":
                        orders = ctx.client.get_orders(
                            filter=GetOrdersRequest(nested=True)
                        )
                        if orders:
                            orders_list = arranging_orders_for_printing(orders)
                            df = pl.DataFrame(orders_list)
                            print(df)

                        else:
                            print("No standing orders")
                    elif input == "positions":
                        positions = ctx.client.get_all_positions()
                        if positions:
                            positions_list = arranging_positions_for_printing(positions)
                            df = pl.DataFrame(positions_list)
                            print(df)

                        else:
                            print("No standing positions")
                    elif input == "help":
                        os.system("clear")
                        print(f"{session_details}")
                    elif input == "exit":
                        print("Exiting...")
                        break
                    elif "chain" in input:
                        option_symbol = await parsing_options(ctx, input)

                        if option_symbol:
                            stop_input = await session.prompt_async("Stop price: ")
                            indicative_price_input = await session.prompt_async(
                                "Indicative entry price: "
                            )
                            stop_price = float(stop_input)
                            indicative_price_input = float(indicative_price_input)
                            handle_order_entry(
                                ctx,
                                side="buy",
                                stop_loss_price=stop_price,
                                indicative_price_input=indicative_price_input,
                                symbol=option_symbol,
                                is_options=True,
                            )
                        else:
                            print("No option symbol found")
                    else:
                        symbol, side, stop_loss, indicative_price_input = input.split()
                        symbol = symbol.upper()
                        if side.lower() not in ["buy", "sell"]:
                            print("Side must be buy or sell")
                            continue
                        stop_loss_price = float(stop_loss)
                        indicative_price_input = float(indicative_price_input)
                        handle_order_entry(
                            ctx,
                            side,
                            stop_loss_price,
                            indicative_price_input,
                            symbol,
                            is_options=False,
                        )
                except Exception as e:
                    print(f"Error: {e}")
                    continue
        finally:
            background_task.cancel()


def cli():
    ctx = get_trading_context()
    log_account_info(ctx)
    account_id = get_account_id(ctx)
    ctx.account_id = account_id
    ctx.risk_log = open("risk.log", "a")
    log_account_snapshots(ctx)
    session_type = "Paper" if ctx.is_paper else "Live"
    print(f"Starting a {session_type} session now... \n")
    asyncio.run(main(ctx))


if __name__ == "__main__":
    cli()
