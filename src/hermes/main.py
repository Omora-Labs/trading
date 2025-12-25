import asyncio

from prompt_toolkit.shortcuts import PromptSession

from hermes.session.alpaca import start_stream
from hermes.session.helpers import check_orders, select_order
from hermes.session.main import get_trading_context
from hermes.trading.order_entry import handle_order_entry


async def main(ctx):
    asyncio.create_task(start_stream(ctx.is_paper))

    print(
        f"""Creating session...
        Trading Mode: {ctx.is_paper}
        Risk Percentage: {ctx.risk_pct * 100}%
        Risk Reward: {ctx.risk_reward}
        Account Value: {ctx.account_value}
        Methods:
            * <orders> to get open orders
            * <positions> to get open positions
            * <cancel order> to cancel a specific order
            * <cancel all orders> to cancel all open orders
            * <AAPL buy 123> to buy AAPL with stop loss 123
            * <AAPL sell 123> to short AAPL with stop loss 123
            * <exit> to leave
        """
    )

    session = PromptSession()
    while True:
        input = await session.prompt_async("> ")

        if input == "orders":
            orders = ctx.client.get_orders()
            print(f"{orders}") if orders else print("No standing orders")
        elif input == "positions":
            positions = ctx.client.get_all_positions()
            print(f"{positions}") if positions else print("No standing orders")
        elif input == "cancel order":
            orders = check_orders(ctx)
            if not orders:
                print("No open orders")
                continue
            order_id = select_order(orders)
            ctx.client.cancel_order_by_id(order_id)
        elif input == "cancel all orders":
            ctx.client.cancel_orders()
            orders = ctx.client.get_orders()
            if not orders:
                print("No open orders")
                continue
        elif input == "exit":
            break
        else:
            symbol, side, stop_loss = input.split()
            if side.lower() not in ["buy", "sell"]:
                print("Side must be buy or sell")
                continue
            stop_loss_price = float(stop_loss)
            handle_order_entry(ctx, side, stop_loss_price, symbol)


def cli():
    ctx = get_trading_context()
    asyncio.run(main(ctx))


if __name__ == "__main__":
    cli()
