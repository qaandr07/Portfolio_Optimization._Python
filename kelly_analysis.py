import matplotlib.pyplot as plt
import pandas as pd

from leverage_analysis import build_leveraged_portfolio_returns
from project_config import TRADING_DAYS_PER_YEAR


def analyze_kelly(
    simulation,
    key_portfolios,
    risk_free_rate=0.0,
    fixed_leverage_ratio=2.0,
    max_leverage=3.0,
    trading_days=TRADING_DAYS_PER_YEAR,
    show_plot=True,
    figsize=(12, 8),
):
    tangency_daily_returns = pd.Series(
        key_portfolios["Tangency"]["daily_returns"],
        index=simulation["aligned_returns"].index,
    )

    expected_return = float(tangency_daily_returns.mean() * trading_days)
    variance = float(tangency_daily_returns.var() * trading_days)

    if variance <= 0:
        kelly_fraction = 0.0
    else:
        kelly_fraction = (expected_return - risk_free_rate) / variance
        kelly_fraction = min(max(kelly_fraction, 0.0), max_leverage)

    tangency_cumulative_returns = (1 + tangency_daily_returns).cumprod()
    fixed_daily_returns, fixed_cumulative_returns = (
        build_leveraged_portfolio_returns(
            tangency_daily_returns,
            leverage_ratio=fixed_leverage_ratio,
            risk_free_rate=risk_free_rate,
            trading_days=trading_days,
        )
    )
    kelly_daily_returns, kelly_cumulative_returns = (
        build_leveraged_portfolio_returns(
            tangency_daily_returns,
            leverage_ratio=kelly_fraction,
            risk_free_rate=risk_free_rate,
            trading_days=trading_days,
        )
    )

    if show_plot:
        plt.figure(figsize=figsize)
        plt.plot(
            tangency_cumulative_returns.index,
            tangency_cumulative_returns,
            label="Tangency",
            linewidth=2,
        )
        plt.plot(
            fixed_cumulative_returns.index,
            fixed_cumulative_returns,
            label=f"Fixed {fixed_leverage_ratio}x",
            linewidth=2,
        )
        plt.plot(
            kelly_cumulative_returns.index,
            kelly_cumulative_returns,
            label=f"Kelly {round(kelly_fraction, 3)}x",
            linewidth=2,
        )
        plt.title("Tangency vs Fixed Leverage vs Kelly Leverage")
        plt.xlabel("Date")
        plt.ylabel("Growth of 1")
        plt.grid(True)
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    print("#part 9")
    print(f"Kelly leverage = {round(kelly_fraction, 3)}")
    print(
        f"Expected return={round(expected_return, 3)}, "
        f"Variance={round(variance, 3)}, "
        f"Max leverage cap={max_leverage}"
    )

    return {
        "kelly_leverage": kelly_fraction,
        "expected_return": expected_return,
        "variance": variance,
        "fixed_leverage_ratio": fixed_leverage_ratio,
        "max_leverage": max_leverage,
        "daily_returns": kelly_daily_returns,
        "cumulative_returns": kelly_cumulative_returns,
        "fixed_daily_returns": fixed_daily_returns,
        "fixed_cumulative_returns": fixed_cumulative_returns,
        "tangency_daily_returns": tangency_daily_returns,
        "tangency_cumulative_returns": tangency_cumulative_returns,
    }
