from typing import List


def arranging_orders_for_printing(orders) -> List:
    order_list = []
    for order in orders:
        handle_append_orders(order, order_list)

        if order.legs:
            for leg in order.legs:
                handle_append_orders(leg, order_list)

    return order_list


def arranging_positions_for_printing(positions) -> List:
    positions_list = []
    for position in positions:
        positions_list.append(
            {
                "symbol": position.symbol,
                "qty": position.quantity,
                "avg_entry_price": position.avg_entry_price,
                "market_value": float(position.market_value),
            }
        )

    return positions_list


def handle_append_orders(item, list: List) -> None:
    list.append(
        {
            "symbol": item.symbol,
            "side": item.side.value,
            "qty": item.qty,
            "price": item.limit_price or item.stop_price,
            "type": item.type.value,
            "tif": item.time_in_force.value.upper(),
        }
    )
