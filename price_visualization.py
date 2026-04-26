import matplotlib.pyplot as plt

from data_loader import select_frame


def plot_asset_prices(
    open_prices,
    *assets,
    max_plots_per_figure=4,
    figure_width=16,
    plot_height=3.8,
    title="Assets Prices",
):
    selected_prices = select_frame(open_prices, *assets)
    asset_names = selected_prices.columns.tolist()

    for start_index in range(0, len(asset_names), max_plots_per_figure):
        page_assets = asset_names[start_index:start_index + max_plots_per_figure]
        page_prices = selected_prices[page_assets]

        fig, axes = plt.subplots(
            len(page_assets),
            1,
            figsize=(figure_width, max(6, plot_height * len(page_assets))),
            sharex=True,
        )

        fig.suptitle(title, fontsize=16)

        if len(page_assets) == 1:
            axes = [axes]

        for axis, asset_name in zip(axes, page_assets):
            axis.plot(
                page_prices.index,
                page_prices[asset_name],
            )

            axis.text(
                0.01,
                0.88,
                asset_name,
                transform=axis.transAxes,
                fontsize=11,
                verticalalignment="top",
                horizontalalignment="left",
                bbox={
                    "facecolor": "white",
                    "alpha": 0.75,
                    "edgecolor": "none",
                    "pad": 3,
                },
            )

            axis.grid(True)

        axes[-1].set_xlabel("Date")

        for label in axes[-1].get_xticklabels():
            label.set_rotation(45)
            label.set_horizontalalignment("right")

        fig.subplots_adjust(
            left=0.07,
            right=0.97,
            top=0.92,
            bottom=0.13,
            hspace=0.12,
        )

        plt.show()