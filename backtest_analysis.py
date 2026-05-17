import matplotlib.pyplot as plt
import pandas as pd


def backtest_strategies(
    simulation,
    key_portfolios,
    show_plot=True,
    figsize=(12, 8),
    **line_kwargs,
):
    strategies = {
        "Tangency": key_portfolios["Tangency"]["weights"],
        "Min Variance": key_portfolios["Min Variance"]["weights"],
        "Max Sortino": key_portfolios["Max Sortino"]["weights"],
        "Equal Weight": key_portfolios["Equal Weight"]["weights"],
    }

    strategy_daily_returns = pd.DataFrame(
        index=simulation["aligned_returns"].index
    )

    for strategy_name, strategy_weights in strategies.items():
        strategy_daily_returns[strategy_name] = (
            simulation["aligned_returns"] @ strategy_weights
        )

    strategy_cumulative_returns = (1 + strategy_daily_returns).cumprod()

    if show_plot:
        plt.figure(figsize=figsize)
        for column in strategy_cumulative_returns.columns:
            plt.plot(
                strategy_cumulative_returns.index,
                strategy_cumulative_returns[column],
                label=column,
                **line_kwargs,
            )

        plt.title("Backtest of Portfolio Strategies")
        plt.xlabel("Date")
        plt.ylabel("Growth of 1")
        plt.grid(True)
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    final_values = strategy_cumulative_returns.iloc[-1].round(3)

    print("#part 6")
    print("Final value of 1 unit by strategy:")
    print(final_values)

    return {
        "strategy_weights": strategies,
        "strategy_daily_returns": strategy_daily_returns,
        "strategy_cumulative_returns": strategy_cumulative_returns,
        "final_values": final_values,
    }
