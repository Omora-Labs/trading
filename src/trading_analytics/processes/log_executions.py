from typing import Union
from uuid import UUID

import polars as pl
from alpaca.trading.models import Order

from trading_order_entries.context import TradingContext


def get_open_positions_symbol(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df.group_by("symbol")
        .agg(pl.col("filled_qty").sum().alias("open_qty"))
        .filter(pl.col("open_qty") != 0)
    )


def order_to_df(order: Order) -> pl.DataFrame:
    order_dict = order.model_dump()
    return pl.DataFrame([order_dict])


def check_existing_trade_id(
    executions: pl.DataFrame, execution_id: UUID
) -> Union[int, None]:
    result = executions.filter(pl.col("order_id").cast(str) == str(execution_id))
    return result["trade_id"][0] if len(result) > 0 else None


def handle_trade_id(db_executions: pl.DataFrame, execution: Order) -> int:
    trade_id = check_existing_trade_id(db_executions, execution.id)

    if not trade_id:
        max_trade_id = db_executions["trade_id"].max()
        trade_id = (max_trade_id + 1) if isinstance(max_trade_id, int) else 1

    return trade_id


def inserting_stop_orders(
    ctx: TradingContext, stop_order: Order, trade_id: int
) -> None:
    df = order_to_df(stop_order)
    df = df.select(
        pl.col("client_order_id").alias("order_id"),
        pl.col("created_at"),
        pl.col("stop_price"),
        pl.col("qty"),
        pl.col("status"),
        pl.col("symbol"),
        pl.col("side"),
        pl.col("type"),
        pl.lit(ctx.account_id).alias("account_id"),
        pl.lit(trade_id).alias("trade_id"),
    )

    ctx.db.log_stop_orders(df)
    print("Stop orders inserted in DB")


def inserting_entry_executions(ctx: TradingContext, execution: Order) -> int:
    df = order_to_df(execution)
    executions = ctx.db.get_executions()
    trade_id = handle_trade_id(executions, execution)

    df = df.select(
        pl.col("client_order_id").alias("order_id"),
        pl.lit(str(execution.id)).alias("execution_id"),
        pl.col("created_at"),
        pl.col("filled_at"),
        pl.col("filled_avg_price"),
        pl.col("filled_qty"),
        pl.col("status"),
        pl.col("symbol"),
        pl.col("side"),
        pl.col("position_intent"),
        pl.lit(trade_id).alias("trade_id"),
        pl.lit(ctx.account_id).alias("account_id"),
    )

    ctx.db.log_executions(df)
    print("Executions inserted in DB")

    return trade_id


def inserting_closing_executions(ctx: TradingContext, execution: Order) -> None:
    df = order_to_df(execution)
    executions = ctx.db.get_executions()
    open_positions = get_open_positions_symbol(executions)

    trade_id = open_positions.filter(pl.col("symbol") == execution.symbol).item(
        0, "trade_id"
    )

    if not trade_id:
        trade_id = 9999

    df = df.select(
        pl.lit(str(execution.id)).alias("order_id"),
        pl.col("id").alias("execution_id"),
        pl.col("created_at"),
        pl.col("filled_at"),
        pl.col("filled_avg_price"),
        pl.col("filled_qty"),
        pl.col("status"),
        pl.col("symbol"),
        pl.col("side"),
        pl.col("position_intent"),
        pl.lit(trade_id).alias("trade_id"),
        pl.lit(ctx.account_id).alias("account_id"),
    )

    ctx.db.log_executions(df)
    print("Executions inserted in DB")
