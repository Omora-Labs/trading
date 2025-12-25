from alpaca.trading.enums import QueryOrderStatus
from alpaca.trading.requests import GetOrdersRequest

from .main import TradingContext


def get_open_orders(ctx: TradingContext):
    params = GetOrdersRequest(status=QueryOrderStatus.OPEN)
    return ctx.client.get_orders(filter=params)


def get_open_positions(ctx: TradingContext):
    return ctx.client.get_all_positions()
