from typing import List

import questionary
from alpaca.trading.enums import ContractType
from alpaca.trading.requests import GetOptionContractsRequest
from prompt_toolkit.shortcuts import prompt


def get_option_contract_request(
    symbol: str, contract_type: ContractType
) -> GetOptionContractsRequest:
    return GetOptionContractsRequest(
        underlying_symbols=[f"{symbol}"], type=contract_type
    )


def get_symbol_from_input(input) -> str:
    return input.split()[1].upper()


def get_closest_strike(strikes: List[float], underlying_price: float) -> float:
    return min(strikes, key=lambda x: abs(x - underlying_price))


async def get_strike(strikes: List[float]) -> float:
    underlying_price = await get_underlying_price()
    closest_strike = get_closest_strike(strikes, underlying_price)

    return await questionary.select(
        "Strike:", choices=[str(s) for s in strikes], default=str(closest_strike)
    ).ask_async()


async def get_option_type() -> str:
    return await questionary.select("Expiration:", choices=["Call", "Put"]).ask_async()


async def get_underlying_price() -> float:
    price = prompt("Insert current underlying price")
    return float(price)


async def get_selected_date(dates: List) -> str:
    return await questionary.select("Expiration:", choices=dates).ask_async()


def get_contract_type_enum(option_type) -> ContractType:
    return ContractType.CALL if option_type == "Call" else ContractType.PUT
