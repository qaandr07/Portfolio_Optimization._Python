import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import PercentFormatter

from common_utils import format_percent, format_weights


def analyze_indifference_curve(
    simulation,
    frontier,
    risk_aversion=3.0,
    show_plot=True,
    figsize=(12, 8),
):
    frontier_returns = frontier["frontier_returns"]
    frontier_risks = frontier["frontier_risks"]
    frontier_weights = frontier["frontier_weights"]

    frontier_utilities = (
        frontier_returns
        - 0.5 * risk_aversion * (frontier_risks ** 2)
    )
    optimal_index = int(np.argmax(frontier_utilities))

    optimal_weights = frontier_weights[optimal_index]
    optimal_return = float(frontier_returns[optimal_index])
    optimal_risk = float(frontier_risks[optimal_index])
    optimal_utility = float(frontier_utilities[optimal_index])

    utility_step = max(abs(optimal_utility) * 0.15, 0.01)
    utility_levels = [
        optimal_utility - utility_step,
        optimal_utility,
        optimal_utility + utility_step,
    ]

    indifference_risks = np.linspace(
        0,
        max(simulation["portfolio_risks"]) * 1.05,
        200,
    )

    if show_plot:
        plt.figure(figsize=figsize)
        plt.scatter(
            simulation["portfolio_risks"],
            simulation["portfolio_returns"],
            c="lightgray",
            s=10,
            label="Random Portfolios",
        )
        plt.plot(
            frontier["frontier_risks"],
            frontier["frontier_returns"],
            color="red",
            linewidth=2.5,
            zorder=3,
            label="Efficient Frontier",
        )

        for curve_index, utility_level in enumerate(utility_levels, start=1):
            indifference_returns = (
                utility_level
                + 0.5 * risk_aversion * (indifference_risks ** 2)
            )
            plt.plot(
                indifference_risks,
                indifference_returns,
                linewidth=1.5,
                linestyle="--",
                label=f"Indifference Curve {curve_index}",
            )

        plt.scatter(
            optimal_risk,
            optimal_return,
            color="black",
            s=180,
            label="Optimal Investor Choice",
        )
        plt.title("Investor Indifference Curves")
        plt.xlabel("Annual Risk")
        plt.ylabel("Annual Return")
        plt.gca().xaxis.set_major_formatter(PercentFormatter(1.0))
        plt.gca().yaxis.set_major_formatter(PercentFormatter(1.0))
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    print("#part 8")
    print(f"Risk aversion A = {risk_aversion}")
    print(
        "Optimal investor weights:",
        format_weights(optimal_weights, simulation["asset_names"]),
    )
    print(
        f"Utility={round(optimal_utility, 3)}, "
        f"Return={format_percent(optimal_return)}, "
        f"Risk={format_percent(optimal_risk)}"
    )

    return {
        "risk_aversion": risk_aversion,
        "optimal_weights": optimal_weights,
        "optimal_return": optimal_return,
        "optimal_risk": optimal_risk,
        "optimal_utility": optimal_utility,
        "utility_levels": utility_levels,
        "frontier_utilities": frontier_utilities,
    }
