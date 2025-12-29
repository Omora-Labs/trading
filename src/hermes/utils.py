from typing import List


def arranging_orders_for_printing(orders) -> List:
    order_list = []
    for order in orders:
        handle_append(order, order_list)

        if order.legs:
            for leg in order.legs:
                handle_append(leg, order_list)

    return order_list


def handle_append(item, list: List) -> None:
    list.append(
        {
            "symbol": item.symbol,
            "side": item.side.value,
            "qty": item.qty,
            "price": item.limit_price or item.stop_price,
            "type": item.type.value,
            "status": item.status.value,
            "tif": item.time_in_force.value.upper(),
        }
    )
