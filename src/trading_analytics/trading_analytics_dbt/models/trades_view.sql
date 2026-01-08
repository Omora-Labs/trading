{{ config (materialized='view') }}

with trade_aggregates as (
    select * from {{ref('trade_aggregates')}}
    ),

account_snapshopts as (
    select * from {{source('stocksdb', 'account_snapshots')}}
    ),

first_execution as (
    select * from {{ref('first_execution')}}
    ),

entry_executions as (
    select * from {{ref('entry_executions')}}
    ),

exit_executions as (
    select * from {{ref('exit_executions')}}
    ),

stop_orders as (
    select * from {{source('stocksdb', 'stop_orders') }}
),

base_metrics as (
select
    ta.trade_id,
    fe.symbol,
    case
        when fe.position_intent = 'buy_to_open' then 'bullish'
        else 'bearish'
    end as direction,
    ta.date_opened,
    ta.total_qty as qty,
    entry.avg_entry_price as entry_price,
    so.stop_price,
    exit.avg_exit_price as exit_price,
    ta.date_closed,
    acc_snap.equity as account_size,
    ta.total_qty * entry.avg_entry_price as capital_required,
    datediff('day', ta.date_opened, ta.date_closed) as duration_days,
    abs(entry.avg_entry_price - so.stop_price) * ta.total_qty as risk_size,
    (exit.avg_exit_price - entry.avg_entry_price) / abs(entry.avg_entry_price - so.stop_price) as risk_reward
from trade_aggregates ta
join first_execution fe on ta.trade_id = fe.trade_id
join account_snapshots acc_snap on ta.date_opened = acc_snap.date
join entry_executions entry on ta.trade_id = entry.trade_id
left join exit_executions exit on ta.trade_id = exit.trade_id
left join stop_orders so on ta.trade_id = so.trade_id
    on so.symbol = fe.symbol
    and date(so.created_at) = date(fe.filled_at)
    and so.created_at > fe.filled_at
),

calculated_metrics as (
    select
        *,
        risk_size / account_size as risk_per_trade,
        (risk_size / account_size) * risk_reward as return_pct
    from base_metrics
)

select
    *,
    return_pct / case when duration_days = 0 then 1 else duration_days end as return_per_day_pct
from calculated_metrics
