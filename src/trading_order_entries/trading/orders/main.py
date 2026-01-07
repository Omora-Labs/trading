import json

from alpaca.trading.enums import TimeInForce

from trading_analytics.processes.log_executions import inserting_stop_orders
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
    trade_id,
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

    inserting_stop_orders(
        ctx, order_remaining_stop, trade_id
    )  # can ignore error raw_data is set as False in initiation


def handle_exit_orders_options(
    ctx: TradingContext,
    side: str,
    symbol: str,
    qty: int,
    stop_loss_price: float,
    take_profit_price: float,
    trade_id: int,
) -> None:
    side = get_exit_side_object(side)

    order_limit = create_limit_order(
        symbol, qty, side, take_profit_price, TimeInForce.DAY
    )
    order_stop = create_stop_order(symbol, qty, side, stop_loss_price, TimeInForce.DAY)

    ctx.client.submit_order(order_limit)
    order_stop_submitted = ctx.client.submit_order(order_stop)

    inserting_stop_orders(
        ctx, order_stop_submitted, trade_id
    )  # can ignore error raw_data is set as False in initiation


def handle_exit_orders(
    ctx: TradingContext,
    side: str,
    symbol: str,
    qty: int,
    stop_loss_price: float,
    take_profit_price: float,
    is_options: bool,
    trade_id: int,
):
    if is_options:
        handle_exit_orders_options(
            ctx, side, symbol, qty, stop_loss_price, take_profit_price, trade_id
        )
    else:
        handle_exit_orders_commons(
            ctx, side, symbol, qty, stop_loss_price, take_profit_price, trade_id
        )


def handle_order_entry(
    ctx: TradingContext,
    side: str,
    stop_loss_price: float,
    indicative_price_input: float,
    symbol: str,
    is_options: bool,
):
    try:
        validation = validate_orders(side, indicative_price_input, stop_loss_price)

        if not validation:
            print(
                f"Your entry price is {indicative_price_input} and your stop price is {stop_loss_price} for an order of side {side}. That's not correct."
            )
            return

        side = get_entry_side_object(side)
        print(
            f"Risk amount: {ctx.risk_amount}, Entry: {indicative_price_input}, Stop: {stop_loss_price}"
        )
        qty = set_qty(
            indicative_price_input, stop_loss_price, ctx.risk_amount, is_options
        )
        print(f"Calculated qty: {qty}")
        take_profit_price = define_take_profit_price(
            ctx, indicative_price_input, stop_loss_price, side
        )

        order = create_entry_order(symbol, qty, side, is_options)

        print(f"\nSubmitting order for {symbol}")

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
