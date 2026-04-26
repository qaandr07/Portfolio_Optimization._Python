import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import PercentFormatter
from scipy.optimize import minimize

from common_utils import format_percent


def calculate_portfolio_return(weights, mean_returns):
    return weights @ mean_returns


def calculate_portfolio_risk(weights, covariance_matrix):
    portfolio_variance = weights @ covariance_matrix @ weights
    return np.sqrt(portfolio_variance)


def minimize_portfolio_risk_for_target_return(
    target_return,
    mean_returns,
    covariance_matrix,
):
    number_of_assets = len(mean_returns)

    initial_weights = np.full(number_of_assets, 1 / number_of_assets)

    bounds = tuple((0.0, 1.0) for _ in range(number_of_assets))

    constraints = (
        {
            "type": "eq",
            "fun": lambda weights: np.sum(weights) - 1.0,
        },
        {
            "type": "eq",
            "fun": lambda weights: calculate_portfolio_return(
                weights,
                mean_returns,
            ) - target_return,
        },
    )

    result = minimize(
        calculate_portfolio_risk,
        initial_weights,
        args=(covariance_matrix,),
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
    )

    if not result.success:
        return None

    return result.x


def calculate_long_only_frontier(
    annual_mean_returns,
    annual_cov_matrix,
    target_returns_count=200,
):
    mean_returns = annual_mean_returns.to_numpy()
    covariance_matrix = annual_cov_matrix.to_numpy()

    min_asset_return = float(np.min(mean_returns))
    max_asset_return = float(np.max(mean_returns))

    target_returns = np.linspace(
        min_asset_return,
        max_asset_return,
        target_returns_count,
    )

    frontier_returns = []
    frontier_risks = []
    frontier_weights = []

    for target_return in target_returns:
        weights = minimize_portfolio_risk_for_target_return(
            target_return,
            mean_returns,
            covariance_matrix,
        )

        if weights is None:
            continue

        portfolio_return = calculate_portfolio_return(weights, mean_returns)
        portfolio_risk = calculate_portfolio_risk(weights, covariance_matrix)

        frontier_returns.append(portfolio_return)
        frontier_risks.append(portfolio_risk)
        frontier_weights.append(weights)

    frontier_returns = np.array(frontier_returns)
    frontier_risks = np.array(frontier_risks)
    frontier_weights = np.array(frontier_weights)

    min_risk_index = int(np.argmin(frontier_risks))

    efficient_risks = frontier_risks[min_risk_index:]
    efficient_returns = frontier_returns[min_risk_index:]
    efficient_weights = frontier_weights[min_risk_index:]

    return {
        "frontier_risks": efficient_risks,
        "frontier_returns": efficient_returns,
        "frontier_weights": efficient_weights,
        "all_frontier_risks": frontier_risks,
        "all_frontier_returns": frontier_returns,
        "all_frontier_weights": frontier_weights,
    }


def build_efficient_frontier(
    simulation,
    show_plot=True,
    figsize=(12, 8),
    title="Efficient Frontier",
):
    portfolio_returns = simulation["portfolio_returns"]
    portfolio_risks = simulation["portfolio_risks"]
    portfolio_sharpes = simulation["portfolio_sharpes"]
    annual_mean_returns = simulation["annual_mean_returns"]
    annual_cov_matrix = simulation["annual_cov_matrix"]

    frontier = calculate_long_only_frontier(
        annual_mean_returns,
        annual_cov_matrix,
    )

    frontier_risks = frontier["frontier_risks"]
    frontier_returns = frontier["frontier_returns"]

    if show_plot:
        plt.figure(figsize=figsize)

        scatter = plt.scatter(
            portfolio_risks,
            portfolio_returns,
            c=portfolio_sharpes,
            cmap="viridis",
            s=10,
            alpha=0.45,
            label="Random Portfolios",
        )

        plt.plot(
            frontier_risks,
            frontier_returns,
            linewidth=3,
            color="red",
            label="Efficient Frontier",
        )

        plt.colorbar(scatter, label="Sharpe Ratio")
        plt.title(title)
        plt.xlabel("Annual Risk")
        plt.ylabel("Annual Return")

        plt.gca().xaxis.set_major_formatter(PercentFormatter(1.0))
        plt.gca().yaxis.set_major_formatter(PercentFormatter(1.0))

        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    min_risk_index = int(np.argmin(frontier_risks))

    print("#part 4")
    print("Built long-only Efficient Frontier.")
    print(
        f"Minimum efficient frontier risk: "
        f"{format_percent(float(frontier_risks[min_risk_index]))}"
    )
    print(
        f"Return at minimum efficient frontier risk: "
        f"{format_percent(float(frontier_returns[min_risk_index]))}"
    )

    return {
        "frontier_risks": frontier_risks,
        "frontier_returns": frontier_returns,
        "frontier_weights": frontier["frontier_weights"],
        "all_frontier_risks": frontier["all_frontier_risks"],
        "all_frontier_returns": frontier["all_frontier_returns"],
        "all_frontier_weights": frontier["all_frontier_weights"],
    }