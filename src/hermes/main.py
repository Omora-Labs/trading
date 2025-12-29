import asyncio
import json
import os

import polars as pl
from alpaca.trading.requests import GetOrdersRequest
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.shortcuts import PromptSession

from hermes.options.main import parsing_options
from hermes.session.alpaca import start_stream
from hermes.session.main import get_trading_context
from hermes.trading.orders.main import handle_order_entry
from hermes.trading.orders.utils import get_latest_price
from hermes.utils import arranging_orders_for_printing


async def main(ctx):
    session_details = f"""
    Trading Mode: {"Paper" if ctx.is_paper else "Live"}
    Risk Percentage: {ctx.risk_pct * 100}%
    Risk Reward: {ctx.risk_reward}
    Account Value: {ctx.account_currency} {ctx.account_value:,.2f}
    Methods:
        * <orders> lists all standing orders
        * <positions> lists all positions
        * <SPY> to get the current ask price
        * <SPY buy 123> to buy AAPL with stop loss 123
        * <SPY sell 123> to short AAPL with stop loss 123
        * <chain SPY> to list option expiries and create an option order
        * <help> to list available methods
        * <exit> to leave
    """

    print("\033]0;Hermes\007", end="")  # Set terminal title
    os.system("clear")
    print(
        f"""
            {session_details}
        """
    )

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
                            for p in positions:
                                print(
                                    f"{p.symbol} | {p.qty} @ {p.avg_entry_price} | Market Value: {float(p.market_value):,.2f}"
                                )
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
                            stop_price = float(stop_input)

                            print(
                                f"\nSubmitting order for {option_symbol} and stop price {stop_price}"
                            )
                            handle_order_entry(
                                ctx,
                                side="buy",
                                stop_loss_price=stop_price,
                                symbol=option_symbol,
                                is_options=True,
                            )
                        else:
                            print("No option symbol found")

                    elif len(input.split()) == 1:
                        try:
                            symbol = input.upper()
                            entry_price = get_latest_price(ctx, symbol, side="buy")
                            print(f"Entry price is {entry_price}")
                        except Exception as e:
                            error_data = json.loads(str(e))
                            print(f"Error submitting order: {error_data['message']}")
                    else:
                        symbol, side, stop_loss = input.split()
                        symbol = symbol.upper()
                        if side.lower() not in ["buy", "sell"]:
                            print("Side must be buy or sell")
                            continue
                        stop_loss_price = float(stop_loss)
                        handle_order_entry(
                            ctx, side, stop_loss_price, symbol, is_options=False
                        )
                except Exception as e:
                    print(f"Error: {e}")
                    continue
        finally:
            background_task.cancel()


def cli():
    ctx = get_trading_context()
    asyncio.run(main(ctx))


if __name__ == "__main__":
    cli()
