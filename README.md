# Trading Order Entry & Analytics

CLI tool for managing trading orders on Alpaca with automated execution logging, analytics, and dbt transformations.

## Features

### CLI
- Real-time stock/options order entry with risk-reward calculations
- Paper and live trading modes via Alpaca API
- Live market data streaming and portfolio monitoring

## Setup

### Prerequisites
- Python 3.11+
- uv package manager
- Alpaca API credentials (paper or live)

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
uv run trader
```

## License

This project is licensed under the MIT License.
