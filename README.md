# Trading Order Entry & Analytics

CLI tool for managing trading orders on Alpaca with automated execution logging, analytics, and dbt transformations.

## Features

### CLI
- Real-time stock/options order entry with risk-reward calculations
- Paper and live trading modes via Alpaca API
- Live market data streaming and portfolio monitoring

### Analytics
- Automated execution and stop order logging to DuckDB/MotherDuck
- Trade tracking with unique trade IDs for entry/exit correlation
- dbt transformations for trade metrics and performance analysis
- Watchlist and account snapshot tracking

## Setup

### Prerequisites
- Python 3.11+
- uv package manager
- Alpaca API credentials (paper or live)
- DuckDB/MotherDuck database

### Installation
```bash
uv sync
```

### Configuration
Set environment variables for Alpaca API and database connection (see `.env` file requirements).

## Usage

### Trading Operations
Run trading scripts from project root:
```bash
uv run src/trading_analytics/processes/log_watchlists.py
```

### Analytics
Run dbt transformations:
```bash
cd src/trading_analytics/trading_analytics_dbt
uv run dbt run
```

### Key Models
- `entry_executions`: Aggregated entry-level execution data
- `exit_executions`: Aggregated exit-level execution data
- `trade_executions`: Combined entry/exit data per trade
- `closed_trades`: Fully closed positions only
- `trades_view`: Enhanced trade metrics with risk/reward calculations
- `avg_performance_month`: Monthly aggregated performance metrics

## License

This project is licensed under the [MIT License](https://opensource.org/license/MIT)
