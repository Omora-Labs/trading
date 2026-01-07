from unittest.mock import Mock

from alpaca.trading.enums import OrderSide, OrderType

from trading_order_entries.context import TradingContext
from trading_order_entries.trading.orders.main import handle_order_entry


def test_handle_order_entry_buy():
    mock_client = Mock()
    mock_response = Mock()
    mock_response.id = "test-order-123"
    mock_client.submit_order.return_value = mock_response

    mock_stock_data = Mock()
    mock_option_data = Mock()
    mock_db = Mock()

    risk_pct = 0.02
    account_value = 10000

    ctx = TradingContext(
        client=mock_client,
        stock_data=mock_stock_data,
        option_data=mock_option_data,
        db=mock_db,
        account_id=1,
        risk_pct=0.02,
        is_paper=True,
        account_value=10000,
        risk_reward=3,
        risk_amount=risk_pct * account_value,
        account_currency="USD",
    )

    handle_order_entry(
        ctx, side="buy", stop_loss_price=98, limit_price=100, symbol="AAPL", is_options=False
    )

    assert mock_client.submit_order.called
    order = mock_client.submit_order.call_args[0][0]
    assert order.symbol == "AAPL"
    assert order.side == OrderSide.BUY
    assert order.qty == 100  # risk_amount=200, delta=2, qty=100
    assert order.type == OrderType.LIMIT

    # Check pending_orders was populated
    assert "test-order-123" in ctx.pending_orders
    assert ctx.pending_orders["test-order-123"]["symbol"] == "AAPL"
    assert ctx.pending_orders["test-order-123"]["qty"] == 100
    assert ctx.pending_orders["test-order-123"]["side"] == "buy"
    assert ctx.pending_orders["test-order-123"]["stop_loss_price"] == 98
    assert ctx.pending_orders["test-order-123"]["take_profit_price"] == 106.0  # entry=100, stop=98, RR=3, TP=100+(2*3)=106


def test_handle_order_entry_sell():
    mock_client = Mock()
    mock_response = Mock()
    mock_response.id = "test-order-456"
    mock_client.submit_order.return_value = mock_response

    mock_stock_data = Mock()
    mock_option_data = Mock()
    mock_db = Mock()

    risk_pct = 0.02
    account_value = 10000

    ctx = TradingContext(
        client=mock_client,
        stock_data=mock_stock_data,
        option_data=mock_option_data,
        db=mock_db,
        account_id=1,
        risk_pct=0.02,
        is_paper=True,
        account_value=10000,
        risk_reward=3,
        risk_amount=risk_pct * account_value,
        account_currency="USD",
    )

    handle_order_entry(
        ctx, side="sell", stop_loss_price=205, limit_price=200, symbol="TSLA", is_options=False
    )

    assert mock_client.submit_order.called
    order = mock_client.submit_order.call_args[0][0]
    assert order.symbol == "TSLA"
    assert order.side == OrderSide.SELL
    assert order.qty == 40  # risk_amount=200, delta=5, qty=40
    assert order.type == OrderType.LIMIT

    # Check pending_orders was populated
    assert "test-order-456" in ctx.pending_orders
    assert ctx.pending_orders["test-order-456"]["symbol"] == "TSLA"
    assert ctx.pending_orders["test-order-456"]["qty"] == 40
    assert ctx.pending_orders["test-order-456"]["side"] == "sell"
    assert ctx.pending_orders["test-order-456"]["stop_loss_price"] == 205
    assert ctx.pending_orders["test-order-456"]["take_profit_price"] == 185.0  # entry=200, stop=205, RR=3, TP=200-(5*3)=185
