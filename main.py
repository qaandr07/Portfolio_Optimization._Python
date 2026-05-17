from backtest_analysis import backtest_strategies
from correlation_analysis import run_correlation_analysis
from data_loader import build_daily_return_enum, download_open_prices, resolve_assets
from efficient_frontier import build_efficient_frontier
from kelly_analysis import analyze_kelly
from leverage_analysis import analyze_leverage
from portfolio_simulation import simulate_random_portfolios
from portfolio_strategies import analyze_key_portfolios
from price_visualization import plot_asset_prices
from project_config import (
    ACTIVE_ASSETS,
    DEFAULT_KELLY_MAX_LEVERAGE,
    DEFAULT_LEVERAGE_RATIO,
    DEFAULT_RISK_AVERSION,
    DEFAULT_RISK_FREE_RATE,
)
from risk_analysis import analyze_drawdowns
from utility_analysis import analyze_indifference_curve

DailyReturnArray = None
CorrelationMatrix = None


def main(
    active_assets=None,
    risk_free_rate=DEFAULT_RISK_FREE_RATE,
    leverage_ratio=DEFAULT_LEVERAGE_RATIO,
    risk_aversion=DEFAULT_RISK_AVERSION,
    kelly_max_leverage=DEFAULT_KELLY_MAX_LEVERAGE,
    show_plots=True,
    **download_kwargs,
):
    global DailyReturnArray
    global CorrelationMatrix

    active_assets = resolve_assets(*(active_assets or ACTIVE_ASSETS))

    raw_data, open_prices, daily_returns = download_open_prices(
        *active_assets,
        **download_kwargs,
    )

    DailyReturnArray = build_daily_return_enum(daily_returns, *active_assets)

    if show_plots:
        plot_asset_prices(open_prices, *active_assets)

    print("#part 1")
    print("Loaded open prices and calculated daily returns.")

    correlation_table, CorrelationMatrix = run_correlation_analysis(
        daily_returns,
        *active_assets,
        show_plot=show_plots,
    )

    simulation = simulate_random_portfolios(
        daily_returns,
        *active_assets,
        risk_free_rate=risk_free_rate,
        show_plot=show_plots,
    )

    frontier = build_efficient_frontier(
        simulation,
        show_plot=show_plots,
    )

    key_portfolios = analyze_key_portfolios(
        simulation,
        frontier,
        show_plot=show_plots,
    )

    backtest = backtest_strategies(
        simulation,
        key_portfolios,
        show_plot=show_plots,
    )

    leverage = analyze_leverage(
        simulation,
        key_portfolios,
        leverage_ratio=leverage_ratio,
        risk_free_rate=risk_free_rate,
        show_plot=show_plots,
    )

    utility = analyze_indifference_curve(
        simulation,
        frontier,
        risk_aversion=risk_aversion,
        show_plot=show_plots,
    )

    kelly = analyze_kelly(
        simulation,
        key_portfolios,
        risk_free_rate=risk_free_rate,
        fixed_leverage_ratio=leverage_ratio,
        max_leverage=kelly_max_leverage,
        show_plot=show_plots,
    )

    drawdowns = analyze_drawdowns(
        backtest,
        risk_free_rate=risk_free_rate,
        extra_strategy_returns={
            f"{leverage_ratio}x Tangency": leverage["daily_returns"],
            "Kelly Tangency": kelly["daily_returns"],
        },
        show_plot=show_plots,
    )

    return {
        "raw_data": raw_data,
        "open_prices": open_prices,
        "daily_returns": daily_returns,
        "correlation_table": correlation_table,
        "simulation": simulation,
        "frontier": frontier,
        "key_portfolios": key_portfolios,
        "backtest": backtest,
        "leverage": leverage,
        "utility": utility,
        "kelly": kelly,
        "drawdowns": drawdowns,
        "DailyReturnArray": DailyReturnArray,
        "CorrelationMatrix": CorrelationMatrix,
    }


if __name__ == "__main__":
    RESULTS = main()