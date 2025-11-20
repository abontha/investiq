"""
Utility helpers that fetch Yahoo Finance candles without yfinance's heavy stack.
"""

from __future__ import annotations

from datetime import datetime, timezone
from functools import lru_cache
from typing import List

import pandas as pd
import requests

# Reuse a single session with a browser-like user agent so Yahoo does not
# reject us with HTTP 429.
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/118.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json,text/javascript,*/*;q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
}
BASE_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"


@lru_cache(maxsize=1)
def get_yfinance_session() -> requests.Session:
    """Return a cached session with the desired headers."""
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    return session


def _align_length(values: List | None, length: int) -> List:
    if values is None:
        return [None] * length
    if len(values) == length:
        return values
    if len(values) > length:
        return values[:length]
    return values + [None] * (length - len(values))


def _to_unix_timestamp(value: datetime) -> int:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    else:
        value = value.astimezone(timezone.utc)
    return int(value.timestamp())


def download_price_history(symbol: str, start: datetime, end: datetime) -> pd.DataFrame:
    """Download historical OHLCV candles for a single ticker."""
    if end <= start:
        raise ValueError("`end` must be greater than `start` when fetching history.")

    session = get_yfinance_session()
    params = {
        "period1": _to_unix_timestamp(start),
        "period2": _to_unix_timestamp(end),
        "interval": "1d",
        "includePrePost": "false",
        "events": "div,splits",
        "lang": "en-US",
        "region": "US",
    }
    try:
        response = session.get(
            BASE_CHART_URL.format(symbol=symbol),
            params=params,
            timeout=30,
        )
        if response.status_code == 429:
            raise RuntimeError(
                "Yahoo Finance rate limit hit. Please wait a moment and try again."
            )
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise RuntimeError("Unable to reach Yahoo Finance.") from exc
    chart = payload.get("chart", {})
    if error := chart.get("error"):
        description = error.get("description") or "Unknown Yahoo Finance error."
        raise RuntimeError(description)
    results = chart.get("result") or []
    if not results:
        return pd.DataFrame()

    result = results[0]
    timestamps = result.get("timestamp") or []
    indicators = result.get("indicators") or {}
    quote = (indicators.get("quote") or [{}])[0]
    adj_close_values = (indicators.get("adjclose") or [{}])[0].get("adjclose")
    if not timestamps:
        return pd.DataFrame()

    opens = _align_length(quote.get("open"), len(timestamps))
    highs = _align_length(quote.get("high"), len(timestamps))
    lows = _align_length(quote.get("low"), len(timestamps))
    closes = _align_length(quote.get("close"), len(timestamps))
    volumes = _align_length(quote.get("volume"), len(timestamps))
    adj_closes = _align_length(
        adj_close_values if adj_close_values is not None else closes,
        len(timestamps),
    )

    frame = pd.DataFrame(
        {
            "Date": pd.to_datetime(timestamps, unit="s"),
            "Open": opens,
            "High": highs,
            "Low": lows,
            "Close": closes,
            "Adj Close": adj_closes,
            "Volume": volumes,
        }
    )
    return frame
