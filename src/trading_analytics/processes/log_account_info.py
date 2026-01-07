from datetime import datetime

import polars as pl

from trading_order_entries.context import TradingContext


def prepare_account_info(ctx: TradingContext) -> pl.DataFrame:
    return pl.DataFrame(
        {
            "account_number": ctx.account_nr,
            "currency": ctx.account_currency,
            "type": "Paper" if ctx.is_paper else "Live",
        }
    )


def prepare_snapshots(ctx: TradingContext) -> pl.DataFrame:
    return pl.DataFrame(
        {
            "account_id": ctx.account_id,
            "last_equity": ctx.account_value,
            "date": datetime.now().date(),
        }
    )


def log_account_info(ctx: TradingContext):
    print("Preparing account info")
    account_info_df = prepare_account_info(ctx)

    print("Preparing account snapshots info")
    account_snapshot_df = prepare_snapshots(ctx)

    print("Logging account info")
    ctx.db.log_account_info(account_info_df)
    print("Account info inserted!")

    print("Preparing snapshots")
    ctx.db.log_account_snapshots(account_snapshot_df)
    print("Account snapshots inserted!")
