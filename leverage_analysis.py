import matplotlib.pyplot as plt
import pandas as pd

from common_utils import format_percent, format_weights
from project_config import TRADING_DAYS_PER_YEAR


def build_leveraged_portfolio_returns(
    portfolio_daily_returns,
    leverage_ratio=2.0,
    risk_free_rate=0.0,
    trading_days=TRADING_DAYS_PER_YEAR,
):
    risk_free_daily = risk_free_rate / trading_days
    leveraged_daily_returns = (
        risk_free_daily
        + leverage_ratio * (portfolio_daily_returns - risk_free_daily)
    )
    leveraged_daily_returns = pd.Series(
        leveraged_daily_returns,
        index=portfolio_daily_returns.index,
    )
    leveraged_cumulative_returns = (1 + leveraged_daily_returns).cumprod()

    return leveraged_daily_returns, leveraged_cumulative_returns


def analyze_leverage(
    simulation,
    key_portfolios,
    leverage_ratio=2.0,
    risk_free_rate=0.0,
    trading_days=TRADING_DAYS_PER_YEAR,
    show_plot=True,
    figsize=(12, 8),
):
    tangency_portfolio = key_portfolios["Tangency"]
    tangency_daily_returns = pd.Series(
        tangency_portfolio["daily_returns"],
        index=simulation["aligned_returns"].index,
    )
    tangency_cumulative_returns = (1 + tangency_daily_returns).cumprod()

    leveraged_daily_returns, leveraged_cumulative_returns = (
        build_leveraged_portfolio_returns(
            tangency_daily_returns,
            leverage_ratio=leverage_ratio,
            risk_free_rate=risk_free_rate,
            trading_days=trading_days,
        )
    )

    leveraged_annual_return = float(
        leveraged_daily_returns.mean() * trading_days
    )
    leveraged_annual_risk = float(
        leveraged_daily_returns.std() * (trading_days ** 0.5)
    )
    leveraged_sharpe = 0.0
    if leveraged_annual_risk > 0:
        leveraged_sharpe = (
            leveraged_annual_return - risk_free_rate
        ) / leveraged_annual_risk

    leveraged_weights = tangency_portfolio["weights"] * leverage_ratio

    if show_plot:
        plt.figure(figsize=figsize)
        plt.plot(
            tangency_cumulative_returns.index,
            tangency_cumulative_returns,
            label="Tangency",
            linewidth=2,
        )
        plt.plot(
            leveraged_cumulative_returns.index,
            leveraged_cumulative_returns,
            label=f"{leverage_ratio}x Tangency",
            linewidth=2,
        )
        plt.title("Tangency vs Leveraged Tangency")
        plt.xlabel("Date")
        plt.ylabel("Growth of 1")
        plt.grid(True)
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    print("#part 7")
    print(f"Leverage ratio: {leverage_ratio}")
    print(
        "Leveraged tangency weights:",
        format_weights(leveraged_weights, simulation["asset_names"]),
    )
    print(
        f"Leveraged return={format_percent(leveraged_annual_return)}, "
        f"risk={format_percent(leveraged_annual_risk)}, "
        f"Sharpe={round(leveraged_sharpe, 3)}"
    )

    return {
        "leverage_ratio": leverage_ratio,
        "risk_free_rate": risk_free_rate,
        "risk_free_daily": risk_free_rate / trading_days,
        "leveraged_weights": leveraged_weights,
        "daily_returns": leveraged_daily_returns,
        "cumulative_returns": leveraged_cumulative_returns,
        "annual_return": leveraged_annual_return,
        "annual_risk": leveraged_annual_risk,
        "sharpe": leveraged_sharpe,
    }
