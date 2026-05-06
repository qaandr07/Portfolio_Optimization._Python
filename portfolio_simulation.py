import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import PercentFormatter

from common_utils import format_percent
from data_loader import select_frame
from project_config import NUM_PORTFOLIOS, TRADING_DAYS_PER_YEAR


def simulate_random_portfolios(
    daily_returns,
    *assets,
    num_portfolios=NUM_PORTFOLIOS,
    trading_days=TRADING_DAYS_PER_YEAR,
    risk_free_rate=0.0,
    random_state=42,
    show_plot=True,
    figsize=(12, 8),
    title=None,
    **scatter_kwargs,
):
    aligned_returns = select_frame(daily_returns, *assets).dropna()
    asset_names = aligned_returns.columns.tolist()
    num_assets = len(asset_names)

    annual_mean_returns = aligned_returns.mean() * trading_days
    annual_cov_matrix = aligned_returns.cov() * trading_days

    random_generator = np.random.default_rng(random_state)
    portfolio_weights = random_generator.random((num_portfolios, num_assets))
    portfolio_weights /= portfolio_weights.sum(axis=1, keepdims=True)

    portfolio_returns = portfolio_weights @ annual_mean_returns.to_numpy()
    portfolio_risks = np.sqrt(
        np.einsum(
            "ij,jk,ik->i",
            portfolio_weights,
            annual_cov_matrix.to_numpy(),
            portfolio_weights,
        )
    )

    portfolio_sharpes = np.divide(
        portfolio_returns - risk_free_rate,
        portfolio_risks,
        out=np.zeros_like(portfolio_returns),
        where=portfolio_risks != 0,
    )

    simulation = {
        "asset_names": asset_names,
        "num_assets": num_assets,
        "aligned_returns": aligned_returns,
        "annual_mean_returns": annual_mean_returns,
        "annual_cov_matrix": annual_cov_matrix,
        "portfolio_returns": portfolio_returns,
        "portfolio_risks": portfolio_risks,
        "portfolio_sharpes": portfolio_sharpes,
        "portfolio_weights": portfolio_weights,
        "risk_free_rate": risk_free_rate,
        "num_portfolios": num_portfolios,
    }

    if show_plot:
        plot_kwargs = {
            "c": portfolio_sharpes,
            "cmap": "viridis",
            "s": 10,
        }
        plot_kwargs.update(scatter_kwargs)

        plt.figure(figsize=figsize)
        scatter = plt.scatter(portfolio_risks, portfolio_returns, **plot_kwargs)
        plt.colorbar(scatter, label="Sharpe Ratio")
        plt.title(title or f"Monte Carlo: {num_portfolios} Random Portfolios")
        plt.xlabel("Annual Risk")
        plt.ylabel("Annual Return")
        plt.gca().xaxis.set_major_formatter(PercentFormatter(1.0))
        plt.gca().yaxis.set_major_formatter(PercentFormatter(1.0))
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    print("#part 3")
    print(f"Generated {num_portfolios} random portfolios.")
    print(
        f"Risk range: "
        f"{format_percent(float(portfolio_risks.min()))} .. "
        f"{format_percent(float(portfolio_risks.max()))}"
    )
    print(
        f"Return range: "
        f"{format_percent(float(portfolio_returns.min()))} .. "
        f"{format_percent(float(portfolio_returns.max()))}"
    )

    return simulation