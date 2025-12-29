from alpaca.trading.enums import OrderClass, OrderSide, OrderType, TimeInForce
from alpaca.trading.requests import (
    LimitOrderRequest,
    MarketOrderRequest,
    StopLossRequest,
    StopOrderRequest,
    TakeProfitRequest,
)


def create_entry_order(
    symbol: str,
    qty: int,
    side: OrderSide,
    is_option: bool = False,
) -> MarketOrderRequest:
    time_in_force = TimeInForce.GTC if not is_option else TimeInForce.DAY

    return MarketOrderRequest(
        symbol=symbol,
        qty=qty,
        side=side,
        time_in_force=time_in_force,
    )


def create_limit_order_with_stop(
    symbol: str,
    qty: int,
    side: OrderSide,
    stop_loss_price: float,
    take_profit_price: float,
) -> LimitOrderRequest:
    return LimitOrderRequest(
        symbol=symbol,
        qty=qty,
        side=side,
        type=OrderType.LIMIT,
        time_in_force=TimeInForce.GTC,
        order_class=OrderClass.OCO,
        take_profit=TakeProfitRequest(limit_price=take_profit_price),
        stop_loss=StopLossRequest(stop_price=stop_loss_price),
    )


def create_stop_order(
    symbol: str,
    qty: int,
    side: OrderSide,
    stop_loss_price: float,
) -> StopOrderRequest:
    return StopOrderRequest(
        symbol=symbol,
        qty=qty,
        side=side,
        time_in_force=TimeInForce.GTC,
        stop_price=stop_loss_price,
    )
