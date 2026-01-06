from typing import Tuple

from alpaca.trading.enums import (
    OrderSide,
)


def validate_orders(side: str, entry_price: float, stop_loss_price: float) -> bool:
    if side == "buy":
        return False if entry_price < stop_loss_price else True
    elif side == "sell":
        return False if entry_price > stop_loss_price else True
    else:
        raise ValueError("Side needs to be buy or sell")


def get_entry_side_object(side: str) -> OrderSide:
    return OrderSide.BUY if side == "buy" else OrderSide.SELL


def get_exit_side_object(side: str) -> OrderSide:
    return OrderSide.SELL if side == "buy" else OrderSide.BUY


def get_qty_split(qty: int) -> Tuple:
    qty_partial_fills = int(round(qty * 0.5))
    remaining_qty = qty - qty_partial_fills

    return qty_partial_fills, remaining_qty
