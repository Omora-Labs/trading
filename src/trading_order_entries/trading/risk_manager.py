from trading_order_entries.context import TradingContext


def set_qty(
    entry_price: float, stop_loss_price: float, risk_amount: float, is_options: bool
):
    if is_options:  # then it's options
        return round((risk_amount / abs(entry_price - stop_loss_price)) / 100)
    else:
        return round(risk_amount / abs(entry_price - stop_loss_price))


def define_take_profit_price(
    ctx: TradingContext, entry_price: float, stop_loss_price: float, side: str
) -> float:
    risk_reward = ctx.risk_reward
    price_delta = define_price_delta(entry_price, stop_loss_price)

    if side == "buy":
        take_profit_price = entry_price + price_delta * risk_reward
    else:
        take_profit_price = entry_price - price_delta * risk_reward

    return round(take_profit_price, 2)


def define_price_delta(entry_price: float, stop_loss_price: float) -> float:
    return abs(entry_price - stop_loss_price)
