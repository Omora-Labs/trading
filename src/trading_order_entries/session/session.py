import questionary
from prompt_toolkit.shortcuts import prompt

def get_trading_mode():
    return (
        questionary.select("Select trading mode:", choices=["Paper", "Live"]).ask()
        == "Paper"
    )


def get_risk_pct():
    risk_pct_input = prompt("Risk Percentage (default: 0.25%).\n> ")
    risk_pct = float(risk_pct_input or "0.25") / 100
    print(f"Risk Percentage for the session is {round(risk_pct * 100, 2)}%")
    return risk_pct


def get_risk_reward():
    risk_reward_input = prompt("Risk/Reward Ratio. (default: 5).\n> ")
    risk_reward = float(risk_reward_input or "5")
    print(f"Risk Reward for the session is {risk_reward}")
    return risk_reward


def setup_session():
    is_paper = get_trading_mode()
    risk_pct = get_risk_pct()
    risk_reward = get_risk_reward()

    return is_paper, risk_pct, risk_reward
