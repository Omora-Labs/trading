from typing import List

import questionary
from alpaca.data.requests import OptionLatestQuoteRequest
from alpaca.trading.enums import ContractType
from alpaca.trading.requests import GetOptionContractsRequest


def get_option_contract_request(symbol) -> GetOptionContractsRequest:
    return GetOptionContractsRequest(underlying_symbols=[f"{symbol}"])


def get_symbol_from_input(input) -> str:
    return input.split()[1]


def get_strike(strikes) -> float:
    return questionary.select("Strike:", choices=[str(s) for s in strikes]).ask()


def get_option_type() -> str:
    return questionary.select("Expiration:", choices=["Call", "Put"]).ask()


def get_selected_date(dates: List) -> str:
    return questionary.select("Expiration:", choices=dates).ask()


def get_stop_price() -> float:
    return float(input("Stop price: "))


def get_contract_type_enum(option_type) -> ContractType:
    return ContractType.CALL if option_type == "Call" else ContractType.PUT


def generate_option_request(option_symbol) -> OptionLatestQuoteRequest:
    return OptionLatestQuoteRequest(symbol_or_symbols=option_symbol)
