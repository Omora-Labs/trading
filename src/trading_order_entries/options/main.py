from trading_order_entries.context import TradingContext
from trading_order_entries.utils import (
    generate_option_request,
    get_contract_type_enum,
    get_option_contract_request,
    get_option_type,
    get_selected_date,
    get_strike,
    get_symbol_from_input,
)


async def parsing_options(ctx: TradingContext, input: str) -> str | None:
    underlying_symbol = get_symbol_from_input(input)
    request = get_option_contract_request(underlying_symbol)
    response = ctx.client.get_option_contracts(request)

    contracts = response.option_contracts
    if contracts:
        dates = sorted(set(str(c.expiration_date) for c in contracts))
        selected_date = await get_selected_date(dates)

        matching_contract = [
            c for c in contracts if str(c.expiration_date) == selected_date
        ]

        option_type = await get_option_type()
        type_enum = get_contract_type_enum(option_type)

        typed_contracts = [c for c in matching_contract if c.type == type_enum]

        strikes = sorted(set(c.strike_price for c in typed_contracts))
        selected_strike = await get_strike(ctx, underlying_symbol, strikes)

        final_contract = next(
            c for c in typed_contracts if c.strike_price == float(selected_strike)
        )

        option_symbol = final_contract.symbol

        quote_request = generate_option_request(option_symbol)
        quote = ctx.option_data.get_option_latest_quote(quote_request)
        ask_price = quote[option_symbol].ask_price
        print(f"Current ask: ${ask_price}")

        print(f"Option Symbol is: {option_symbol}")

        return option_symbol

    else:
        print("No option contracts found for that ticker.")
