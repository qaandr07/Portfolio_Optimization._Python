import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import PercentFormatter
from scipy.optimize import minimize

try:
    from pypfopt import EfficientFrontier
except ImportError:
    EfficientFrontier = None

from common_utils import format_percent, format_weights
from project_config import TRADING_DAYS_PER_YEAR


def project_to_simplex(weights):
    clipped_weights = np.asarray(weights, dtype=float)

    if np.all(clipped_weights >= 0) and np.isclose(clipped_weights.sum(), 1.0):
        return clipped_weights

    sorted_weights = np.sort(clipped_weights)[::-1]
    cumulative_weights = np.cumsum(sorted_weights)
    rho_candidates = (
        sorted_weights
        - (cumulative_weights - 1) / (np.arange(len(sorted_weights)) + 1)
    )
    rho = np.where(rho_candidates > 0)[0][-1]
    theta = (cumulative_weights[rho] - 1) / (rho + 1)

    return np.maximum(clipped_weights - theta, 0.0)


def normalize_weights(weights):
    weights = np.asarray(weights, dtype=float)
    weights = np.nan_to_num(weights, nan=0.0, posinf=0.0, neginf=0.0)
    weights = np.maximum(weights, 0.0)

    total_weight = weights.sum()
    if total_weight <= 0:
        return np.repeat(1 / len(weights), len(weights))

    return weights / total_weight


def pypfopt_weights_to_array(cleaned_weights, asset_names):
    return np.array(
        [float(cleaned_weights.get(asset_name, 0.0)) for asset_name in asset_names],
        dtype=float,
    )


def evaluate_portfolio(
    weights,
    annual_mean_returns,
    annual_cov_matrix,
    aligned_returns,
    risk_free_rate=0.0,
):
    weights = normalize_weights(weights)

    annual_return = float(weights @ annual_mean_returns.to_numpy())
    annual_variance = float(weights.T @ annual_cov_matrix.to_numpy() @ weights)
    annual_risk = float(np.sqrt(max(annual_variance, 0.0)))

    portfolio_daily_returns = aligned_returns.to_numpy() @ weights
    risk_free_daily = risk_free_rate / TRADING_DAYS_PER_YEAR
    downside_returns = np.minimum(
        portfolio_daily_returns - risk_free_daily,
        0.0,
    )
    annual_downside_deviation = float(
        np.sqrt(np.mean(downside_returns ** 2))
        * np.sqrt(TRADING_DAYS_PER_YEAR)
    )

    sharpe_ratio = 0.0
    if annual_risk > 0:
        sharpe_ratio = float((annual_return - risk_free_rate) / annual_risk)

    sortino_ratio = 0.0
    if annual_downside_deviation > 0:
        sortino_ratio = float(
            (annual_return - risk_free_rate) / annual_downside_deviation
        )

    return {
        "weights": weights,
        "return": annual_return,
        "risk": annual_risk,
        "variance": annual_variance,
        "downside_deviation": annual_downside_deviation,
        "sharpe": sharpe_ratio,
        "sortino": sortino_ratio,
        "daily_returns": portfolio_daily_returns,
    }


def refine_long_only_weights(
    initial_weights,
    objective_function,
    maximize=True,
    random_state=42,
    step_sizes=(0.10, 0.05, 0.02, 0.01, 0.005),
    random_trials_per_step=300,
):
    random_generator = np.random.default_rng(random_state)
    best_weights = np.asarray(initial_weights, dtype=float).copy()
    best_weights = project_to_simplex(best_weights)
    best_score = float(objective_function(best_weights))

    def is_better(candidate_score, current_score):
        if maximize:
            return candidate_score > current_score
        return candidate_score < current_score

    for step_size in step_sizes:
        improved = True

        while improved:
            improved = False

            for source_index in range(len(best_weights)):
                for target_index in range(len(best_weights)):
                    if source_index == target_index:
                        continue

                    if best_weights[source_index] < step_size:
                        continue

                    candidate_weights = best_weights.copy()
                    candidate_weights[source_index] -= step_size
                    candidate_weights[target_index] += step_size
                    candidate_score = float(objective_function(candidate_weights))

                    if is_better(candidate_score, best_score):
                        best_weights = candidate_weights
                        best_score = candidate_score
                        improved = True

        for _ in range(random_trials_per_step):
            perturbed_weights = (
                best_weights
                + random_generator.normal(
                    0.0,
                    step_size / 2,
                    size=len(best_weights),
                )
            )
            candidate_weights = project_to_simplex(perturbed_weights)
            candidate_score = float(objective_function(candidate_weights))

            if is_better(candidate_score, best_score):
                best_weights = candidate_weights
                best_score = candidate_score

    return best_weights, best_score


def get_best_monte_carlo_weights(simulation, metric_name):
    if metric_name == "sharpe":
        index = int(np.argmax(simulation["portfolio_sharpes"]))
    elif metric_name == "variance":
        index = int(np.argmin(simulation["portfolio_risks"]))
    elif metric_name == "sortino":
        index = int(np.argmax(simulation["portfolio_sortinos"]))
    else:
        raise ValueError(f"Unknown metric name: {metric_name}")

    return simulation["portfolio_weights"][index]


def optimize_max_sharpe_with_pypfopt(
    annual_mean_returns,
    annual_cov_matrix,
    asset_names,
    risk_free_rate,
):
    if EfficientFrontier is None:
        raise RuntimeError("PyPortfolioOpt is not installed.")

    ef = EfficientFrontier(
        annual_mean_returns,
        annual_cov_matrix,
        weight_bounds=(0, 1),
    )
    ef.max_sharpe(risk_free_rate=risk_free_rate)
    cleaned_weights = ef.clean_weights()

    return normalize_weights(
        pypfopt_weights_to_array(cleaned_weights, asset_names),
    )


def optimize_min_variance_with_pypfopt(
    annual_mean_returns,
    annual_cov_matrix,
    asset_names,
):
    if EfficientFrontier is None:
        raise RuntimeError("PyPortfolioOpt is not installed.")

    ef = EfficientFrontier(
        annual_mean_returns,
        annual_cov_matrix,
        weight_bounds=(0, 1),
    )
    ef.min_volatility()
    cleaned_weights = ef.clean_weights()

    return normalize_weights(
        pypfopt_weights_to_array(cleaned_weights, asset_names),
    )


def optimize_sortino_with_scipy(
    simulation,
    initial_weights,
):
    annual_mean_returns = simulation["annual_mean_returns"]
    annual_cov_matrix = simulation["annual_cov_matrix"]
    aligned_returns = simulation["aligned_returns"]
    risk_free_rate = simulation["risk_free_rate"]
    num_assets = simulation["num_assets"]

    def objective(weights):
        portfolio = evaluate_portfolio(
            weights,
            annual_mean_returns,
            annual_cov_matrix,
            aligned_returns,
            risk_free_rate=risk_free_rate,
        )
        return -portfolio["sortino"]

    constraints = [
        {
            "type": "eq",
            "fun": lambda weights: np.sum(weights) - 1.0,
        },
    ]
    bounds = [(0.0, 1.0) for _ in range(num_assets)]

    result = minimize(
        objective,
        normalize_weights(initial_weights),
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={
            "maxiter": 1000,
            "ftol": 1e-12,
        },
    )

    if not result.success:
        sortino_objective = lambda weights: evaluate_portfolio(
            weights,
            annual_mean_returns,
            annual_cov_matrix,
            aligned_returns,
            risk_free_rate=risk_free_rate,
        )["sortino"]

        fallback_weights, _ = refine_long_only_weights(
            initial_weights,
            sortino_objective,
            maximize=True,
            random_state=43,
        )
        return normalize_weights(fallback_weights)

    return normalize_weights(result.x)


def build_equal_weight_portfolio(simulation):
    equal_weights = np.repeat(
        1 / simulation["num_assets"],
        simulation["num_assets"],
    )
    return {
        "name": "Equal Weight",
        **evaluate_portfolio(
            equal_weights,
            simulation["annual_mean_returns"],
            simulation["annual_cov_matrix"],
            simulation["aligned_returns"],
            risk_free_rate=simulation["risk_free_rate"],
        ),
    }


def build_tangency_portfolio(simulation):
    annual_mean_returns = simulation["annual_mean_returns"]
    annual_cov_matrix = simulation["annual_cov_matrix"]
    aligned_returns = simulation["aligned_returns"]
    asset_names = simulation["asset_names"]
    risk_free_rate = simulation["risk_free_rate"]

    seed_weights = get_best_monte_carlo_weights(simulation, "sharpe")

    try:
        weights = optimize_max_sharpe_with_pypfopt(
            annual_mean_returns,
            annual_cov_matrix,
            asset_names,
            risk_free_rate,
        )
        optimizer = "PyPortfolioOpt"
    except Exception as error:
        print(f"PyPortfolioOpt max Sharpe failed, fallback is used: {error}")

        sharpe_objective = lambda candidate_weights: evaluate_portfolio(
            candidate_weights,
            annual_mean_returns,
            annual_cov_matrix,
            aligned_returns,
            risk_free_rate=risk_free_rate,
        )["sharpe"]

        weights, _ = refine_long_only_weights(
            seed_weights,
            sharpe_objective,
            maximize=True,
            random_state=41,
        )
        optimizer = "Fallback"

    return {
        "name": "Tangency",
        "optimizer": optimizer,
        **evaluate_portfolio(
            weights,
            annual_mean_returns,
            annual_cov_matrix,
            aligned_returns,
            risk_free_rate=risk_free_rate,
        ),
    }


def build_min_variance_portfolio(simulation):
    annual_mean_returns = simulation["annual_mean_returns"]
    annual_cov_matrix = simulation["annual_cov_matrix"]
    aligned_returns = simulation["aligned_returns"]
    asset_names = simulation["asset_names"]
    risk_free_rate = simulation["risk_free_rate"]

    seed_weights = get_best_monte_carlo_weights(simulation, "variance")

    try:
        weights = optimize_min_variance_with_pypfopt(
            annual_mean_returns,
            annual_cov_matrix,
            asset_names,
        )
        optimizer = "PyPortfolioOpt"
    except Exception as error:
        print(f"PyPortfolioOpt min variance failed, fallback is used: {error}")

        variance_objective = lambda candidate_weights: evaluate_portfolio(
            candidate_weights,
            annual_mean_returns,
            annual_cov_matrix,
            aligned_returns,
            risk_free_rate=risk_free_rate,
        )["variance"]

        weights, _ = refine_long_only_weights(
            seed_weights,
            variance_objective,
            maximize=False,
            random_state=42,
        )
        optimizer = "Fallback"

    return {
        "name": "Min Variance",
        "optimizer": optimizer,
        **evaluate_portfolio(
            weights,
            annual_mean_returns,
            annual_cov_matrix,
            aligned_returns,
            risk_free_rate=risk_free_rate,
        ),
    }


def build_sortino_portfolio(simulation):
    annual_mean_returns = simulation["annual_mean_returns"]
    annual_cov_matrix = simulation["annual_cov_matrix"]
    aligned_returns = simulation["aligned_returns"]
    risk_free_rate = simulation["risk_free_rate"]

    seed_weights = get_best_monte_carlo_weights(simulation, "sortino")
    weights = optimize_sortino_with_scipy(simulation, seed_weights)

    return {
        "name": "Max Sortino",
        "optimizer": "scipy.optimize",
        **evaluate_portfolio(
            weights,
            annual_mean_returns,
            annual_cov_matrix,
            aligned_returns,
            risk_free_rate=risk_free_rate,
        ),
    }


def analyze_key_portfolios(
    simulation,
    frontier,
    show_plot=True,
    figsize=(12, 8),
    **scatter_kwargs,
):
    tangency_portfolio = build_tangency_portfolio(simulation)
    min_variance_portfolio = build_min_variance_portfolio(simulation)
    sortino_portfolio = build_sortino_portfolio(simulation)
    equal_weight_portfolio = build_equal_weight_portfolio(simulation)

    key_portfolios = {
        "Tangency": tangency_portfolio,
        "Min Variance": min_variance_portfolio,
        "Max Sortino": sortino_portfolio,
        "Equal Weight": equal_weight_portfolio,
    }

    if show_plot:
        plot_kwargs = {
            "c": simulation["portfolio_sharpes"],
            "cmap": "viridis",
            "s": 10,
        }
        plot_kwargs.update(scatter_kwargs)

        plt.figure(figsize=figsize)
        scatter = plt.scatter(
            simulation["portfolio_risks"],
            simulation["portfolio_returns"],
            **plot_kwargs,
        )
        plt.plot(
            frontier["frontier_risks"],
            frontier["frontier_returns"],
            color="red",
            linewidth=2.5,
            zorder=3,
            label="Efficient Frontier",
        )
        plt.scatter(
            tangency_portfolio["risk"],
            tangency_portfolio["return"],
            color="gold",
            edgecolors="black",
            s=180,
            label="Tangency",
        )
        plt.scatter(
            min_variance_portfolio["risk"],
            min_variance_portfolio["return"],
            color="blue",
            edgecolors="black",
            s=180,
            label="Min Variance",
        )
        plt.scatter(
            sortino_portfolio["risk"],
            sortino_portfolio["return"],
            color="orange",
            edgecolors="black",
            s=180,
            label="Max Sortino",
        )
        plt.colorbar(scatter, label="Sharpe Ratio")
        plt.title("Tangency, Min Variance and Max Sortino Portfolios")
        plt.xlabel("Annual Risk")
        plt.ylabel("Annual Return")
        plt.gca().xaxis.set_major_formatter(PercentFormatter(1.0))
        plt.gca().yaxis.set_major_formatter(PercentFormatter(1.0))
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    print("#part 5")
    print(
        f"Tangency portfolio ({tangency_portfolio['optimizer']}):",
        format_weights(tangency_portfolio["weights"], simulation["asset_names"]),
    )
    print(
        f"Return={format_percent(tangency_portfolio['return'])}, "
        f"Risk={format_percent(tangency_portfolio['risk'])}, "
        f"Sharpe={round(tangency_portfolio['sharpe'], 3)}"
    )
    print(
        f"Min variance portfolio ({min_variance_portfolio['optimizer']}):",
        format_weights(
            min_variance_portfolio["weights"],
            simulation["asset_names"],
        ),
    )
    print(
        f"Return={format_percent(min_variance_portfolio['return'])}, "
        f"Risk={format_percent(min_variance_portfolio['risk'])}"
    )
    print(
        f"Max Sortino portfolio ({sortino_portfolio['optimizer']}):",
        format_weights(sortino_portfolio["weights"], simulation["asset_names"]),
    )
    print(
        f"Return={format_percent(sortino_portfolio['return'])}, "
        f"Risk={format_percent(sortino_portfolio['risk'])}, "
        f"Sortino={round(sortino_portfolio['sortino'], 3)}"
    )

    return key_portfolios