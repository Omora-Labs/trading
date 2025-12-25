from unittest.mock import Mock

from oec.order_entry import get_quote


def test_get_quote():
    mock_quote = Mock()
    mock_stock_data = Mock()
    mock_stock_data.get_latest_quote.return_value = {"AAPL": mock_quote}

    ctx = Mock()
    ctx.stock_data = mock_stock_data

    result = get_quote(ctx, "AAPL")

    assert result == mock_quote
    mock_stock_data.get_latest_quote.assert_called_once()
