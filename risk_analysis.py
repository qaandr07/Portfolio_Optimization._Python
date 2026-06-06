import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

try:
    import quantstats as qs
except ImportError:
    qs = None

from project_config import TRADING_DAYS_PER_YEAR


def clean_return_series(returns):
    clean_returns = (
        pd.Series(returns)
        .replace([np.inf, -np.inf], np.nan)
        .dropna()
    )

    return clean_returns.astype(float)


def max_drawdown(cumulative_series):
    running_max = cumulative_series.cummax()
    drawdown = cumulative_series / running_max - 1

    return float(drawdown.min())


def safe_quantstats_metric(metric_function, returns, default_value=0.0, **kwargs):
    if qs is None:
        return default_value

    try:
        value = metric_function(returns, **kwargs)

        if isinstance(value, pd.Series):
            value = value.iloc[0]

        if value is None:
            return default_value

        value = float(value)

        if not np.isfinite(value):
            return default_value

        return value
    except Exception:
        return default_value


def calculate_manual_strategy_metrics(
    returns,
    risk_free_rate=0.0,
    trading_days=TRADING_DAYS_PER_YEAR,
):
    clean_returns = clean_return_series(returns)

    if clean_returns.empty:
        return {
            "Annual Return": 0.0,
            "Volatility": 0.0,
            "Sharpe Ratio": 0.0,
            "Sortino Ratio": 0.0,
            "Calmar Ratio": 0.0,
            "Max Drawdown": 0.0,
        }

    cumulative_returns = (1 + clean_returns).cumprod()

    annual_return = float(
        cumulative_returns.iloc[-1] ** (trading_days / len(clean_returns)) - 1
    )
    annual_mean_return = float(clean_returns.mean() * trading_days)
    volatility = float(clean_returns.std() * np.sqrt(trading_days))

    sharpe_ratio = 0.0
    if volatility > 0:
        sharpe_ratio = (annual_mean_return - risk_free_rate) / volatility

    risk_free_daily = risk_free_rate / trading_days
    downside_returns = np.minimum(clean_returns - risk_free_daily, 0.0)
    downside_deviation = float(
        np.sqrt(np.mean(downside_returns ** 2)) * np.sqrt(trading_days)
    )

    sortino_ratio = 0.0
    if downside_deviation > 0:
        sortino_ratio = (
            annual_mean_return - risk_free_rate
        ) / downside_deviation

    strategy_max_drawdown = max_drawdown(cumulative_returns)

    calmar_ratio = 0.0
    if abs(strategy_max_drawdown) > 1e-12:
        calmar_ratio = annual_return / abs(strategy_max_drawdown)

    return {
        "Annual Return": annual_return,
        "Volatility": volatility,
        "Sharpe Ratio": sharpe_ratio,
        "Sortino Ratio": sortino_ratio,
        "Calmar Ratio": calmar_ratio,
        "Max Drawdown": strategy_max_drawdown,
    }


def calculate_quantstats_strategy_metrics(
    returns,
    risk_free_rate=0.0,
    trading_days=TRADING_DAYS_PER_YEAR,
):
    clean_returns = clean_return_series(returns)

    if clean_returns.empty:
        return {
            "Annual Return": 0.0,
            "Volatility": 0.0,
            "Sharpe Ratio": 0.0,
            "Sortino Ratio": 0.0,
            "Calmar Ratio": 0.0,
            "Max Drawdown": 0.0,
        }

    manual_metrics = calculate_manual_strategy_metrics(
        clean_returns,
        risk_free_rate=risk_free_rate,
        trading_days=trading_days,
    )

    if qs is None:
        return manual_metrics

    risk_free_daily = risk_free_rate / trading_days

    annual_return = safe_quantstats_metric(
        qs.stats.cagr,
        clean_returns,
        default_value=manual_metrics["Annual Return"],
    )
    volatility = safe_quantstats_metric(
        qs.stats.volatility,
        clean_returns,
        default_value=manual_metrics["Volatility"],
        periods=trading_days,
    )
    sharpe_ratio = safe_quantstats_metric(
        qs.stats.sharpe,
        clean_returns,
        default_value=manual_metrics["Sharpe Ratio"],
        rf=risk_free_daily,
        periods=trading_days,
        annualize=True,
    )
    sortino_ratio = safe_quantstats_metric(
        qs.stats.sortino,
        clean_returns,
        default_value=manual_metrics["Sortino Ratio"],
        rf=risk_free_daily,
        periods=trading_days,
        annualize=True,
    )
    max_drawdown_value = safe_quantstats_metric(
        qs.stats.max_drawdown,
        clean_returns,
        default_value=manual_metrics["Max Drawdown"],
    )
    calmar_ratio = safe_quantstats_metric(
        qs.stats.calmar,
        clean_returns,
        default_value=manual_metrics["Calmar Ratio"],
    )

    return {
        "Annual Return": annual_return,
        "Volatility": volatility,
        "Sharpe Ratio": sharpe_ratio,
        "Sortino Ratio": sortino_ratio,
        "Calmar Ratio": calmar_ratio,
        "Max Drawdown": max_drawdown_value,
    }


def calculate_strategy_metrics(
    returns,
    risk_free_rate=0.0,
    trading_days=TRADING_DAYS_PER_YEAR,
):
    return calculate_quantstats_strategy_metrics(
        returns,
        risk_free_rate=risk_free_rate,
        trading_days=trading_days,
    )


def build_strategy_returns_with_extra(
    backtest_results,
    extra_strategy_returns=None,
):
    strategy_daily_returns = backtest_results["strategy_daily_returns"].copy()

    if extra_strategy_returns:
        for strategy_name, daily_returns in extra_strategy_returns.items():
            strategy_daily_returns[strategy_name] = pd.Series(
                daily_returns,
                index=strategy_daily_returns.index,
            )

    strategy_daily_returns = (
        strategy_daily_returns
        .replace([np.inf, -np.inf], np.nan)
        .dropna(how="all")
    )

    return strategy_daily_returns


def build_drawdown_table(strategy_cumulative_returns):
    drawdown_table = (
        strategy_cumulative_returns
        / strategy_cumulative_returns.cummax()
        - 1
    )

    return drawdown_table


def build_metrics_table(
    strategy_daily_returns,
    risk_free_rate=0.0,
    trading_days=TRADING_DAYS_PER_YEAR,
):
    metrics_table = pd.DataFrame(
        {
            strategy_name: calculate_strategy_metrics(
                strategy_daily_returns[strategy_name],
                risk_free_rate=risk_free_rate,
                trading_days=trading_days,
            )
            for strategy_name in strategy_daily_returns.columns
        }
    ).T

    return metrics_table.round(3)


def analyze_drawdowns(
    backtest_results,
    risk_free_rate=0.0,
    trading_days=TRADING_DAYS_PER_YEAR,
    extra_strategy_returns=None,
    show_plot=True,
    figsize=(12, 8),
):
    strategy_daily_returns = build_strategy_returns_with_extra(
        backtest_results,
        extra_strategy_returns=extra_strategy_returns,
    )
    strategy_cumulative_returns = (1 + strategy_daily_returns).cumprod()
    drawdown_plot = build_drawdown_table(strategy_cumulative_returns)

    metrics_table = build_metrics_table(
        strategy_daily_returns,
        risk_free_rate=risk_free_rate,
        trading_days=trading_days,
    )

    if show_plot:
        plt.figure(figsize=figsize)

        for column in drawdown_plot.columns:
            plt.plot(drawdown_plot.index, drawdown_plot[column], label=column)

        plt.title("Portfolio Drawdowns")
        plt.xlabel("Date")
        plt.ylabel("Drawdown")
        plt.grid(True)
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    print("#part 10")
    print("Risk metrics by strategy:")

    if qs is None:
        print("quantstats is not installed, manual fallback metrics are used.")
    else:
        print("Metrics are calculated with quantstats where possible.")

    print(metrics_table)

    return {
        "strategy_daily_returns": strategy_daily_returns,
        "strategy_cumulative_returns": strategy_cumulative_returns,
        "metrics_table": metrics_table,
        "drawdown_plot": drawdown_plot,
    }