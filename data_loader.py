from enum import Enum

import numpy as np
import pandas as pd
import yfinance as yf

from project_config import (
    ACTIVE_ASSETS,
    DEFAULT_END,
    DEFAULT_INTERVAL,
    DEFAULT_START,
    Ticker,
)


def resolve_assets(*assets):
    if len(assets) == 1 and isinstance(assets[0], (list, tuple, set)):
        assets = tuple(assets[0])

    if not assets:
        assets = tuple(ACTIVE_ASSETS)

    resolved_assets = []

    for asset in assets:
        if isinstance(asset, Ticker):
            resolved_assets.append(asset)
            continue

        if isinstance(asset, str):
            if asset in Ticker.__members__:
                resolved_assets.append(Ticker[asset])
                continue

            matching_tickers = [ticker for ticker in Ticker if ticker.value == asset]
            if matching_tickers:
                resolved_assets.append(matching_tickers[0])
                continue

        raise ValueError(f"Unknown asset: {asset}")

    return resolved_assets


def get_asset_names(*assets):
    return [asset.name for asset in resolve_assets(*assets)]


def get_asset_tickers(*assets):
    return [asset.value for asset in resolve_assets(*assets)]


def select_frame(frame, *assets):
    if assets:
        return frame[get_asset_names(*assets)].copy()
    return frame.copy()


def download_open_prices(
    *assets,
    start=DEFAULT_START,
    end=DEFAULT_END,
    interval=DEFAULT_INTERVAL,
    price_field="Open",
    auto_adjust=False,
    progress=False,
    **download_kwargs,
):
    resolved_assets = resolve_assets(*assets)
    asset_names = [asset.name for asset in resolved_assets]
    asset_tickers = [asset.value for asset in resolved_assets]

    raw_data = yf.download(
        asset_tickers,
        start=start,
        end=end,
        interval=interval,
        auto_adjust=auto_adjust,
        progress=progress,
        **download_kwargs,
    )

    price_data = raw_data[price_field].copy()
    if isinstance(price_data, pd.Series):
        price_data = price_data.to_frame(name=asset_tickers[0])

    price_data = price_data[asset_tickers]
    price_data.columns = asset_names
    price_data = price_data.replace([np.inf, -np.inf], np.nan)

    empty_columns = [
        column
        for column in price_data.columns
        if price_data[column].dropna().empty
    ]
    if empty_columns:
        raise ValueError(
            f"No price history found for assets: {', '.join(empty_columns)}"
        )

    daily_returns = (
        price_data
        .pct_change(fill_method=None)
        .replace([np.inf, -np.inf], np.nan)
        .dropna(how="all")
    )
    if daily_returns.empty:
        raise ValueError(
            "Not enough data to calculate daily returns for the selected assets."
        )

    return raw_data, price_data, daily_returns


def build_daily_return_enum(daily_returns, *assets, digits=3):
    selected_returns = select_frame(daily_returns, *assets).dropna(how="all")
    enum_members = {
        column: selected_returns[column].dropna().round(digits).tolist()
        for column in selected_returns.columns
    }
    return Enum("DailyReturnArray", enum_members)
