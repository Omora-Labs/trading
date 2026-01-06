import json

from trading_order_entries.context import TradingContext
from trading_order_entries.trading.orders.orders import (
    create_entry_order,
    create_limit_order,
    create_limit_order_with_stop,
    create_stop_order,
)
from trading_order_entries.trading.orders.utils import (
    get_entry_side_object,
    get_exit_side_object,
    get_qty_split,
    validate_orders,
)
from trading_order_entries.trading.risk_manager import (
    define_take_profit_price,
    set_qty,
)


def handle_exit_orders_commons(
    ctx: TradingContext,
    side: str,
    symbol: str,
    qty: int,
    stop_loss_price: float,
    take_profit_price: float,
) -> None:
    qty_partial_fills, remaining_qty = get_qty_split(qty)
    side = get_exit_side_object(side)

    order_partial_fills_one = create_limit_order_with_stop(
        symbol, qty_partial_fills, side, stop_loss_price, take_profit_price
    )
    order_remaining_stop = create_stop_order(
        symbol, remaining_qty, side, stop_loss_price
    )

    ctx.client.submit_order(order_partial_fills_one)
    ctx.client.submit_order(order_remaining_stop)


def handle_exit_orders_options(
    ctx: TradingContext,
    side: str,
    symbol: str,
    qty: int,
    stop_loss_price: float,
    take_profit_price: float,
) -> None:
    side = get_exit_side_object(side)

    order_limit = create_limit_order(symbol, qty, side, take_profit_price)
    order_stop = create_stop_order(symbol, qty, side, stop_loss_price)

    ctx.client.submit_order(order_limit)
    ctx.client.submit_order(order_stop)


def handle_exit_orders(
    ctx: TradingContext,
    side: str,
    symbol: str,
    qty: int,
    stop_loss_price: float,
    take_profit_price: float,
    is_options: bool,
):
    if is_options:
        handle_exit_orders_options(
            ctx, side, symbol, qty, stop_loss_price, take_profit_price
        )
    else:
        handle_exit_orders_commons(
            ctx, side, symbol, qty, stop_loss_price, take_profit_price
        )


def handle_order_entry(
    ctx: TradingContext,
    side: str,
    stop_loss_price: float,
    limit_price: float,
    symbol: str,
    is_options: bool,
):
    try:
        validate_orders(side, limit_price, stop_loss_price)
        side = get_entry_side_object(side)
        print(
            f"Risk amount: {ctx.risk_amount}, Entry: {limit_price}, Stop: {stop_loss_price}"
        )
        qty = set_qty(limit_price, stop_loss_price, ctx.risk_amount, is_options)
        print(f"Calculated qty: {qty}")
        take_profit_price = define_take_profit_price(
            ctx, limit_price, stop_loss_price, side
        )

        order = create_entry_order(symbol, qty, side, limit_price, is_options)
        response = ctx.client.submit_order(order)

        ctx.pending_orders[response.id] = {
            "side": side,
            "symbol": symbol,
            "qty": qty,
            "stop_loss_price": stop_loss_price,
            "take_profit_price": take_profit_price,
            "is_options": is_options,
        }

    except Exception as e:
        try:
            error_data = json.loads(str(e))
            print(f"Error submitting order: {error_data['message']}")
        except Exception:
            print(f"Error submitting order: {e}")
