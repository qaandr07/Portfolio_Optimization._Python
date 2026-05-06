from correlation_analysis import run_correlation_analysis
from data_loader import build_daily_return_enum, download_open_prices, resolve_assets
from efficient_frontier import build_efficient_frontier
from portfolio_simulation import simulate_random_portfolios
from price_visualization import plot_asset_prices
from project_config import ACTIVE_ASSETS

DailyReturnArray = None
CorrelationMatrix = None


def main(active_assets=None, **download_kwargs):
    global DailyReturnArray
    global CorrelationMatrix

    active_assets = resolve_assets(*(active_assets or ACTIVE_ASSETS))

    raw_data, open_prices, daily_returns = download_open_prices(
        *active_assets,
        **download_kwargs,
    )

    DailyReturnArray = build_daily_return_enum(daily_returns, *active_assets)

    plot_asset_prices(open_prices, *active_assets)

    print("#part 1")
    print("Loaded open prices and converted them to daily returns.")

    correlation_table, CorrelationMatrix = run_correlation_analysis(
        daily_returns,
        *active_assets,
    )

    simulation = simulate_random_portfolios(daily_returns, *active_assets)

    frontier = build_efficient_frontier(simulation)

    return {
        "raw_data": raw_data,
        "open_prices": open_prices,
        "daily_returns": daily_returns,
        "correlation_table": correlation_table,
        "simulation": simulation,
        "frontier": frontier,
        "DailyReturnArray": DailyReturnArray,
        "CorrelationMatrix": CorrelationMatrix,
    }


if __name__ == "__main__":
    RESULTS = main()