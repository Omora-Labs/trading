from .context import TradingContext


def define_risk_amount(ctx: TradingContext) -> float:
    return ctx.risk_pct * ctx.account_value


def define_take_profit_price(
    ctx: TradingContext, entry_price: float, stop_loss_price: float, side: str
) -> float:
    risk_reward = ctx.risk_reward
    price_delta = define_price_delta(entry_price, stop_loss_price)

    if side == "buy":
        take_profit_price = entry_price + price_delta * risk_reward
    else:
        take_profit_price = entry_price - price_delta * risk_reward

    return take_profit_price


def define_price_delta(entry_price: float, stop_loss_price: float) -> float:
    return abs(entry_price - stop_loss_price)
