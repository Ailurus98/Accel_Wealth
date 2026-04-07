import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time


def fetch_price_history(ticker: str, period: str = "1y") -> pd.DataFrame:
    """Fetch OHLCV data for a ticker. Returns empty DataFrame on failure."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            data = yf.download(ticker, period=period, progress=False, auto_adjust=True)
            if data is None or data.empty:
                return pd.DataFrame()
            # Flatten MultiIndex columns if present
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            return data
        except Exception as e:
            error_msg = str(e)
            if "Rate limited" in error_msg or "Too Many Requests" in error_msg:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 5  # Exponential backoff: 5s, 10s, 20s
                    print(f"[!] Rate limited for {ticker}. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"[!] Rate limit error fetching {ticker} after {max_retries} attempts: {e}")
            else:
                print(f"[!] Error fetching {ticker}: {e}")
            return pd.DataFrame()


def compute_moving_average(series: pd.Series, window: int) -> pd.Series:
    """
    Safely compute a simple moving average.
    If there aren't enough data points for the requested window,
    use the available length instead of raising an error.
    """
    available = len(series.dropna())
    effective_window = min(window, available)

    if effective_window < 2:
        # Not enough data even for a 2-period average — return NaN series
        return pd.Series(np.nan, index=series.index)

    return series.rolling(window=effective_window, min_periods=1).mean()


def compute_ema(series: pd.Series, span: int) -> pd.Series:
    """Safely compute exponential moving average."""
    available = len(series.dropna())
    effective_span = min(span, available)
    if effective_span < 2:
        return pd.Series(np.nan, index=series.index)
    return series.ewm(span=effective_span, adjust=False).mean()


def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Compute RSI with safe minimum-period handling."""
    available = len(series.dropna())
    effective = min(period, max(2, available - 1))

    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=effective, min_periods=1).mean()
    avg_loss = loss.rolling(window=effective, min_periods=1).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi


def get_technical_indicators(df: pd.DataFrame) -> dict:
    """
    Return a dict of technical indicator Series.
    All moving averages degrade gracefully when history is short.
    """
    if df.empty or "Close" not in df.columns:
        return {}

    close = df["Close"].squeeze()
    n = len(close)

    indicators = {}

    # Moving averages — only compute if we have meaningful data
    for window, label in [(20, "MA20"), (50, "MA50"), (200, "MA200")]:
        if n >= 5:          # need at least 5 bars to be useful
            indicators[label] = compute_moving_average(close, window)
        else:
            indicators[label] = pd.Series(np.nan, index=df.index)

    # EMA
    for span, label in [(12, "EMA12"), (26, "EMA26")]:
        indicators[label] = compute_ema(close, span)

    # RSI
    indicators["RSI"] = compute_rsi(close)

    # Bollinger Bands
    window = min(20, n)
    if window >= 5:
        rolling = close.rolling(window=window, min_periods=1)
        mid = rolling.mean()
        std = rolling.std(ddof=0).fillna(0)
        indicators["BB_upper"] = mid + 2 * std
        indicators["BB_lower"] = mid - 2 * std
        indicators["BB_mid"] = mid

    return indicators


def get_info(ticker: str) -> dict:
    """Return yfinance .info dict, falling back to {} on error."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            t = yf.Ticker(ticker)
            info = t.info or {}
            return info
        except Exception as e:
            error_msg = str(e)
            if "Rate limited" in error_msg or "Too Many Requests" in error_msg:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 5  # Exponential backoff: 5s, 10s, 20s
                    print(f"[!] Rate limited for {ticker} info. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"[!] Rate limit error fetching {ticker} info after {max_retries} attempts")
            else:
                print(f"[!] Error fetching {ticker} info: {e}")
            return {}


def format_inr(value) -> str:
    """Format a number into Indian numbering (Crore / Lakh)."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "N/A"

    if v >= 1e7:
        return f"₹{v / 1e7:.2f} Cr"
    elif v >= 1e5:
        return f"₹{v / 1e5:.2f} L"
    else:
        return f"₹{v:,.0f}"
