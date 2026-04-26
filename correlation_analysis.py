import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from data_loader import select_frame


def pearson_correlation(x, y):
    x_mean = sum(x) / len(x)
    y_mean = sum(y) / len(y)

    numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, y))
    x_part = sum((xi - x_mean) ** 2 for xi in x)
    y_part = sum((yi - y_mean) ** 2 for yi in y)

    denominator = (x_part * y_part) ** 0.5
    return numerator / denominator


def build_correlation_matrix_class(correlation_table):
    matrix = correlation_table.round(3).to_dict()

    class CorrelationMatrixAccessor:
        MATRIX = matrix

        def __class_getitem__(cls, item):
            return cls.MATRIX[item]

    return CorrelationMatrixAccessor


def run_correlation_analysis(
    daily_returns,
    *assets,
    show_plot=True,
    figsize=(8, 6),
    title="Correlation Matrix",
    **heatmap_kwargs,
):
    selected_returns = select_frame(daily_returns, *assets).dropna()
    asset_names = selected_returns.columns.tolist()

    correlation_table = pd.DataFrame(index=asset_names, columns=asset_names, dtype=float)

    for asset1 in asset_names:
        for asset2 in asset_names:
            correlation_table.loc[asset1, asset2] = round(
                pearson_correlation(
                    selected_returns[asset1].tolist(),
                    selected_returns[asset2].tolist(),
                ),
                3,
            )

    correlation_matrix_class = build_correlation_matrix_class(correlation_table)

    print("#part 2")
    print("Correlation matrix:")
    print(correlation_table)

    if show_plot:
        plot_kwargs = {
            "annot": True,
            "cmap": "coolwarm",
            "vmin": -1,
            "vmax": 1,
            "linewidths": 0.5,
        }
        plot_kwargs.update(heatmap_kwargs)

        plt.figure(figsize=figsize)
        sns.heatmap(correlation_table, **plot_kwargs)
        plt.title(title)
        plt.tight_layout()
        plt.show()

    return correlation_table, correlation_matrix_class
