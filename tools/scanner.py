"""Stock scanner that automatically finds the best trading opportunities.

Screens a configurable universe (default: S&P 500 top components) for
momentum, volume, fundamental, breakout, and earnings-catalyst signals.
Each opportunity is scored 0-100 and ranked.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

import numpy as np
import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# S&P 500 top ~100 by market cap (configurable universe)
# ---------------------------------------------------------------------------
SP500_TOP100 = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B",
    "JPM", "JNJ", "V", "UNH", "HD", "PG", "MA", "DIS", "PYPL", "NFLX",
    "ADBE", "CRM", "INTC", "AMD", "QCOM", "TXN", "COST", "WMT", "MRK",
    "PFE", "ABBV", "LLY", "TMO", "ABT", "DHR", "AVGO", "CSCO", "ACN",
    "PEP", "KO", "MCD", "NKE", "LIN", "NEE", "UNP", "LOW", "MDT",
    "HON", "AMGN", "IBM", "GE", "CAT", "BA", "RTX", "GS", "BLK",
    "ISRG", "SPGI", "AXP", "SYK", "GILD", "MDLZ", "CVX", "XOM",
    "COP", "EOG", "SLB", "MMM", "DE", "CI", "ELV", "CB", "SO",
    "DUK", "MO", "PM", "BMY", "VRTX", "REGN", "ZTS", "SCHW",
    "MS", "C", "USB", "PNC", "TFC", "ADP", "CME", "ICE", "MCO",
    "APD", "SHW", "ECL", "NSC", "ITW", "EMR", "FDX", "UPS",
    "ORCL", "NOW", "SNOW", "PANW", "CRWD", "ABNB", "UBER", "SQ",
    "COIN", "PLTR", "RIVN", "MRVL",
]


# ---------------------------------------------------------------------------
# Internal helpers — technical indicator calculations
# ---------------------------------------------------------------------------

def _compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Return RSI as a Series aligned with *series*."""
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(period).mean()
    rs = gain / loss
    return 100.0 - (100.0 / (1.0 + rs))


def _compute_macd(series: pd.Series,
                  fast: int = 12,
                  slow: int = 26,
                  signal: int = 9) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Return (macd_line, signal_line, histogram)."""
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def _compute_atr(high: pd.Series, low: pd.Series, close: pd.Series,
                 period: int = 14) -> pd.Series:
    """Average True Range."""
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(period).mean()


def _find_support_resistance(close: pd.Series,
                             lookback: int = 20) -> tuple[float, float]:
    """Simple support / resistance via rolling min/max over *lookback* bars."""
    recent = close.iloc[-lookback:]
    support = recent.min()
    resistance = recent.max()
    return float(support), float(resistance)


# ---------------------------------------------------------------------------
# Per-stock signal extraction
# ---------------------------------------------------------------------------

def _analyze_stock(symbol: str,
                   hist: pd.DataFrame,
                   info: dict) -> Optional[dict]:
    """Run all signal checks on a single stock.

    Returns a dict of raw signals or ``None`` when data is insufficient.
    """
    if hist is None or hist.empty or len(hist) < 50:
        return None

    close = hist["Close"]
    volume = hist["Volume"]
    high = hist["High"]
    low = hist["Low"]

    current_price = float(close.iloc[-1])
    prev_price = float(close.iloc[-2]) if len(close) >= 2 else current_price

    # --- Moving averages ---
    sma_20 = close.rolling(20).mean()
    sma_50 = close.rolling(50).mean()
    sma_200 = close.rolling(200).mean() if len(close) >= 200 else pd.Series(dtype=float)

    sma_50_val = float(sma_50.iloc[-1]) if not sma_50.empty and pd.notna(sma_50.iloc[-1]) else None
    sma_200_val = float(sma_200.iloc[-1]) if not sma_200.empty and pd.notna(sma_200.iloc[-1]) else None

    # --- RSI ---
    rsi_series = _compute_rsi(close, 14)
    rsi_val = float(rsi_series.iloc[-1]) if pd.notna(rsi_series.iloc[-1]) else 50.0

    # --- MACD ---
    macd_line, signal_line, macd_hist = _compute_macd(close)
    macd_val = float(macd_line.iloc[-1]) if pd.notna(macd_line.iloc[-1]) else 0.0
    macd_signal_val = float(signal_line.iloc[-1]) if pd.notna(signal_line.iloc[-1]) else 0.0
    macd_hist_val = float(macd_hist.iloc[-1]) if pd.notna(macd_hist.iloc[-1]) else 0.0
    macd_hist_prev = float(macd_hist.iloc[-2]) if len(macd_hist) >= 2 and pd.notna(macd_hist.iloc[-2]) else 0.0

    # Crossover detection (histogram sign change)
    macd_bullish_cross = macd_hist_prev < 0 and macd_hist_val >= 0
    macd_bearish_cross = macd_hist_prev > 0 and macd_hist_val <= 0

    # --- Golden / death cross ---
    golden_cross = False
    death_cross = False
    if sma_50_val is not None and sma_200_val is not None and len(sma_50) >= 2 and len(sma_200) >= 2:
        prev_50 = float(sma_50.iloc[-2]) if pd.notna(sma_50.iloc[-2]) else None
        prev_200 = float(sma_200.iloc[-2]) if pd.notna(sma_200.iloc[-2]) else None
        if prev_50 is not None and prev_200 is not None:
            golden_cross = prev_50 <= prev_200 and sma_50_val > sma_200_val
            death_cross = prev_50 >= prev_200 and sma_50_val < sma_200_val

    # --- Volume ---
    avg_vol_20 = float(volume.rolling(20).mean().iloc[-1]) if pd.notna(volume.rolling(20).mean().iloc[-1]) else 1.0
    current_vol = float(volume.iloc[-1])
    volume_ratio = current_vol / avg_vol_20 if avg_vol_20 > 0 else 1.0

    # --- Breakout / breakdown ---
    support, resistance = _find_support_resistance(close, lookback=20)
    breakout_up = current_price > resistance and prev_price <= resistance
    breakdown = current_price < support and prev_price >= support

    # --- ATR for volatility context ---
    atr = _compute_atr(high, low, close, 14)
    atr_val = float(atr.iloc[-1]) if pd.notna(atr.iloc[-1]) else 0.0
    atr_pct = (atr_val / current_price * 100) if current_price > 0 else 0.0

    # --- Price change ---
    pct_change_1d = ((current_price - prev_price) / prev_price * 100) if prev_price else 0.0
    pct_change_5d = 0.0
    if len(close) >= 6:
        p5 = float(close.iloc[-6])
        pct_change_5d = ((current_price - p5) / p5 * 100) if p5 else 0.0

    # --- Fundamentals from info dict ---
    pe_ratio = info.get("trailingPE")
    forward_pe = info.get("forwardPE")
    market_cap = info.get("marketCap")
    revenue_growth = info.get("revenueGrowth")  # yfinance returns as decimal
    earnings_date_raw = info.get("earningsTimestamp") or info.get("earningsDate")
    profit_margins = info.get("profitMargins")
    price_to_book = info.get("priceToBook")

    # Parse earnings date
    earnings_days_away: Optional[int] = None
    if earnings_date_raw is not None:
        try:
            # yfinance may return a list of timestamps or a single value
            if isinstance(earnings_date_raw, (list, tuple)) and len(earnings_date_raw) > 0:
                ts = earnings_date_raw[0]
            else:
                ts = earnings_date_raw
            if isinstance(ts, (int, float)):
                earn_dt = datetime.utcfromtimestamp(ts)
            else:
                earn_dt = pd.Timestamp(ts).to_pydatetime()
            earnings_days_away = (earn_dt - datetime.utcnow()).days
        except Exception:
            earnings_days_away = None

    # --- RSI divergence (simple: price making lower low but RSI making higher low) ---
    rsi_bullish_div = False
    rsi_bearish_div = False
    if len(close) >= 30 and len(rsi_series) >= 30:
        try:
            price_window = close.iloc[-30:]
            rsi_window = rsi_series.iloc[-30:]
            mid = 15
            price_low1 = float(price_window.iloc[:mid].min())
            price_low2 = float(price_window.iloc[mid:].min())
            rsi_at_low1 = float(rsi_window.iloc[price_window.iloc[:mid].values.argmin()])
            rsi_at_low2 = float(rsi_window.iloc[mid + price_window.iloc[mid:].values.argmin()])
            if price_low2 < price_low1 and rsi_at_low2 > rsi_at_low1:
                rsi_bullish_div = True
            price_high1 = float(price_window.iloc[:mid].max())
            price_high2 = float(price_window.iloc[mid:].max())
            rsi_at_high1 = float(rsi_window.iloc[price_window.iloc[:mid].values.argmax()])
            rsi_at_high2 = float(rsi_window.iloc[mid + price_window.iloc[mid:].values.argmax()])
            if price_high2 > price_high1 and rsi_at_high2 < rsi_at_high1:
                rsi_bearish_div = True
        except Exception:
            pass

    return {
        "symbol": symbol,
        "price": current_price,
        "pct_change_1d": round(pct_change_1d, 2),
        "pct_change_5d": round(pct_change_5d, 2),
        # Momentum
        "rsi": round(rsi_val, 2),
        "macd": round(macd_val, 4),
        "macd_signal": round(macd_signal_val, 4),
        "macd_histogram": round(macd_hist_val, 4),
        "macd_bullish_cross": macd_bullish_cross,
        "macd_bearish_cross": macd_bearish_cross,
        "golden_cross": golden_cross,
        "death_cross": death_cross,
        # Moving averages
        "sma_50": round(sma_50_val, 2) if sma_50_val else None,
        "sma_200": round(sma_200_val, 2) if sma_200_val else None,
        "above_sma_50": current_price > sma_50_val if sma_50_val else None,
        "above_sma_200": current_price > sma_200_val if sma_200_val else None,
        # Volume
        "volume": int(current_vol),
        "avg_volume_20d": int(avg_vol_20),
        "volume_ratio": round(volume_ratio, 2),
        "volume_spike": volume_ratio >= 2.0,
        # Breakout
        "support": round(support, 2),
        "resistance": round(resistance, 2),
        "breakout_up": breakout_up,
        "breakdown": breakdown,
        # Volatility
        "atr": round(atr_val, 2),
        "atr_pct": round(atr_pct, 2),
        # Fundamentals
        "pe_ratio": round(float(pe_ratio), 2) if pe_ratio and isinstance(pe_ratio, (int, float)) else None,
        "forward_pe": round(float(forward_pe), 2) if forward_pe and isinstance(forward_pe, (int, float)) else None,
        "market_cap": market_cap,
        "revenue_growth": round(float(revenue_growth), 4) if revenue_growth and isinstance(revenue_growth, (int, float)) else None,
        "profit_margins": round(float(profit_margins), 4) if profit_margins and isinstance(profit_margins, (int, float)) else None,
        "price_to_book": round(float(price_to_book), 2) if price_to_book and isinstance(price_to_book, (int, float)) else None,
        # Earnings
        "earnings_days_away": earnings_days_away,
        # Divergences
        "rsi_bullish_divergence": rsi_bullish_div,
        "rsi_bearish_divergence": rsi_bearish_div,
    }


# ---------------------------------------------------------------------------
# Scoring engine
# ---------------------------------------------------------------------------

def _score_opportunity(signals: dict, profile: Optional[str] = None) -> float:
    """Score an opportunity 0-100.

    When *profile* is given the weights are adjusted to emphasise
    the signals relevant to that scan profile.
    """
    score = 50.0  # neutral starting point

    # -- Momentum (max +/-20) --
    rsi = signals.get("rsi", 50)
    if rsi < 30:
        score += 10 + (30 - rsi) * 0.5       # deeper oversold = higher bonus
    elif rsi > 70:
        score += 10 + (rsi - 70) * 0.5        # overbought can be momentum strength
    if signals.get("macd_bullish_cross"):
        score += 8
    if signals.get("golden_cross"):
        score += 7
    if signals.get("above_sma_50"):
        score += 3
    if signals.get("above_sma_200"):
        score += 3

    # -- Volume (max +15) --
    vol_ratio = signals.get("volume_ratio", 1.0)
    if vol_ratio >= 2.0:
        score += min(15, 5 + (vol_ratio - 2.0) * 3)

    # -- Breakout (max +15) --
    if signals.get("breakout_up"):
        score += 15
    if signals.get("breakdown"):
        score -= 10  # bearish

    # -- Fundamentals (max +10) --
    pe = signals.get("pe_ratio")
    if pe is not None and 0 < pe <= 15:
        score += 5
    elif pe is not None and 15 < pe <= 25:
        score += 2
    rev_growth = signals.get("revenue_growth")
    if rev_growth is not None and rev_growth > 0.10:
        score += 5
    elif rev_growth is not None and rev_growth > 0.0:
        score += 2

    # -- Earnings catalyst (max +8) --
    ed = signals.get("earnings_days_away")
    if ed is not None and 0 < ed <= 14:
        score += 8
    elif ed is not None and 14 < ed <= 30:
        score += 4

    # -- Divergences (max +10) --
    if signals.get("rsi_bullish_divergence"):
        score += 10
    if signals.get("rsi_bearish_divergence"):
        score -= 5

    # -- Profile-specific adjustments --
    if profile == "momentum_breakout":
        if signals.get("breakout_up"):
            score += 10
        if vol_ratio >= 2.0:
            score += 5
        if signals.get("macd_bullish_cross"):
            score += 5
        # Penalize if not above key MA
        if not signals.get("above_sma_50"):
            score -= 10

    elif profile == "value_oversold":
        if rsi < 30:
            score += 10
        if pe is not None and 0 < pe <= 15:
            score += 10
        if signals.get("price_to_book") is not None and signals["price_to_book"] < 2.0:
            score += 5
        if rev_growth is not None and rev_growth < 0:
            score -= 10

    elif profile == "earnings_catalyst":
        if ed is not None and 0 < ed <= 14:
            score += 12
        if rev_growth is not None and rev_growth > 0.10:
            score += 8
        margins = signals.get("profit_margins")
        if margins is not None and margins > 0.15:
            score += 5

    elif profile == "trend_reversal":
        if signals.get("rsi_bullish_divergence"):
            score += 12
        if signals.get("rsi_bearish_divergence"):
            score += 8  # still an opportunity to short
        if signals.get("macd_bullish_cross") and rsi < 40:
            score += 10
        if signals.get("death_cross"):
            score += 5  # potential bottom after death cross

    # Clamp to 0-100
    return round(max(0.0, min(100.0, score)), 1)


# ---------------------------------------------------------------------------
# Scan filter predicates (for pre-filtering before scoring)
# ---------------------------------------------------------------------------

def _passes_filter(signals: dict,
                   *,
                   min_market_cap: Optional[float] = None,
                   pe_range: Optional[tuple[float, float]] = None,
                   min_revenue_growth: Optional[float] = None,
                   rsi_oversold: bool = False,
                   rsi_overbought: bool = False,
                   require_volume_spike: bool = False,
                   require_breakout: bool = False,
                   earnings_within_days: Optional[int] = None) -> bool:
    """Return True if *signals* pass the given filter criteria."""

    mc = signals.get("market_cap")
    if min_market_cap is not None and (mc is None or mc < min_market_cap):
        return False

    pe = signals.get("pe_ratio")
    if pe_range is not None:
        if pe is None or not (pe_range[0] <= pe <= pe_range[1]):
            return False

    rg = signals.get("revenue_growth")
    if min_revenue_growth is not None and (rg is None or rg < min_revenue_growth):
        return False

    rsi = signals.get("rsi", 50)
    if rsi_oversold and rsi >= 30:
        return False
    if rsi_overbought and rsi <= 70:
        return False

    if require_volume_spike and not signals.get("volume_spike"):
        return False

    if require_breakout and not signals.get("breakout_up"):
        return False

    ed = signals.get("earnings_days_away")
    if earnings_within_days is not None:
        if ed is None or ed < 0 or ed > earnings_within_days:
            return False

    return True


# ---------------------------------------------------------------------------
# Pre-built scan profiles
# ---------------------------------------------------------------------------

SCAN_PROFILES: dict[str, dict] = {
    "momentum_breakout": {
        "description": "Stocks breaking out above resistance on high volume",
        "filter_kwargs": {
            "require_volume_spike": True,
            "require_breakout": True,
            "min_market_cap": 5e9,
        },
    },
    "value_oversold": {
        "description": "Undervalued stocks with RSI < 30 (oversold)",
        "filter_kwargs": {
            "rsi_oversold": True,
            "pe_range": (0, 20),
            "min_market_cap": 2e9,
        },
    },
    "earnings_catalyst": {
        "description": "Strong fundamentals with earnings within 14 days",
        "filter_kwargs": {
            "earnings_within_days": 14,
            "min_revenue_growth": 0.05,
            "min_market_cap": 10e9,
        },
    },
    "trend_reversal": {
        "description": "Potential trend reversals via RSI divergences or MACD cross near lows",
        "filter_kwargs": {
            "min_market_cap": 2e9,
        },
    },
}


# ---------------------------------------------------------------------------
# Data fetching helpers (batch-friendly)
# ---------------------------------------------------------------------------

def _fetch_histories(symbols: list[str],
                     period: str = "1y",
                     interval: str = "1d") -> dict[str, pd.DataFrame]:
    """Download price histories for all *symbols* at once using yfinance batch."""
    try:
        data = yf.download(symbols, period=period, interval=interval,
                           group_by="ticker", threads=True, progress=False)
    except Exception as exc:
        logger.warning("Batch download failed (%s); falling back to serial", exc)
        data = None

    histories: dict[str, pd.DataFrame] = {}
    if data is not None and not data.empty:
        for sym in symbols:
            try:
                if len(symbols) == 1:
                    df = data.copy()
                else:
                    df = data[sym].dropna(how="all")
                if not df.empty:
                    # Flatten MultiIndex columns if present
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.droplevel(1)
                    histories[sym] = df
            except (KeyError, Exception):
                continue

    # Fill gaps with serial fallback
    for sym in symbols:
        if sym not in histories:
            try:
                df = yf.Ticker(sym).history(period=period, interval=interval)
                if not df.empty:
                    histories[sym] = df
            except Exception:
                continue

    return histories


def _fetch_infos(symbols: list[str]) -> dict[str, dict]:
    """Fetch ``yf.Ticker.info`` for each symbol (serial, with error handling)."""
    infos: dict[str, dict] = {}
    for sym in symbols:
        try:
            infos[sym] = yf.Ticker(sym).info
        except Exception:
            infos[sym] = {}
    return infos


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def scan(universe: Optional[list[str]] = None,
         profile: Optional[str] = None,
         top_n: int = 10,
         *,
         min_market_cap: Optional[float] = None,
         pe_range: Optional[tuple[float, float]] = None,
         min_revenue_growth: Optional[float] = None,
         rsi_oversold: bool = False,
         rsi_overbought: bool = False,
         require_volume_spike: bool = False,
         require_breakout: bool = False,
         earnings_within_days: Optional[int] = None) -> list[dict]:
    """Run a full scan and return the top *top_n* opportunities.

    Parameters
    ----------
    universe : list[str] | None
        Tickers to scan. Defaults to ``SP500_TOP100``.
    profile : str | None
        One of the pre-built scan profile names. When provided, its
        default filter kwargs are merged (explicit kwargs take priority).
    top_n : int
        Number of results to return, sorted descending by score.
    min_market_cap, pe_range, min_revenue_growth, rsi_oversold,
    rsi_overbought, require_volume_spike, require_breakout,
    earnings_within_days
        Optional filter criteria applied before scoring.

    Returns
    -------
    list[dict]
        Each dict contains the full signal payload plus a ``score`` key.
    """
    if universe is None:
        universe = list(SP500_TOP100)

    # Merge profile defaults with explicit overrides
    filter_kw: dict = {}
    if profile is not None:
        prof = SCAN_PROFILES.get(profile)
        if prof is None:
            raise ValueError(
                f"Unknown profile '{profile}'. "
                f"Available: {list(SCAN_PROFILES.keys())}"
            )
        filter_kw.update(prof["filter_kwargs"])

    # Explicit kwargs override profile defaults
    explicit = {
        "min_market_cap": min_market_cap,
        "pe_range": pe_range,
        "min_revenue_growth": min_revenue_growth,
        "rsi_oversold": rsi_oversold,
        "rsi_overbought": rsi_overbought,
        "require_volume_spike": require_volume_spike,
        "require_breakout": require_breakout,
        "earnings_within_days": earnings_within_days,
    }
    for k, v in explicit.items():
        if v is not None and v is not False:
            filter_kw[k] = v

    logger.info("Scanning %d symbols (profile=%s) ...", len(universe), profile)

    # Fetch data
    histories = _fetch_histories(universe)
    infos = _fetch_infos(list(histories.keys()))

    # Analyze & filter & score
    results: list[dict] = []
    for sym in universe:
        hist = histories.get(sym)
        info = infos.get(sym, {})
        signals = _analyze_stock(sym, hist, info)
        if signals is None:
            continue

        # Apply filters — for trend_reversal profile also require a divergence
        if profile == "trend_reversal":
            has_divergence = (
                signals.get("rsi_bullish_divergence")
                or signals.get("rsi_bearish_divergence")
                or (signals.get("macd_bullish_cross") and signals.get("rsi", 50) < 40)
            )
            if not has_divergence:
                continue

        if not _passes_filter(signals, **filter_kw):
            continue

        signals["score"] = _score_opportunity(signals, profile=profile)
        results.append(signals)

    # Sort by score descending, then by volume ratio as tiebreaker
    results.sort(key=lambda x: (x["score"], x.get("volume_ratio", 0)), reverse=True)

    return results[:top_n]


def quick_scan(symbols: list[str]) -> list[dict]:
    """Lightweight scan of a small watchlist — no filters, just scored signals.

    Useful for rescanning an existing watchlist or a handful of tickers
    without the overhead of profile filtering.
    """
    return scan(universe=symbols, top_n=len(symbols))


def list_profiles() -> dict[str, str]:
    """Return available scan profile names and their descriptions."""
    return {name: prof["description"] for name, prof in SCAN_PROFILES.items()}


# ---------------------------------------------------------------------------
# CLI convenience
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json
    import argparse

    parser = argparse.ArgumentParser(description="Stock opportunity scanner")
    parser.add_argument("--profile", "-p", type=str, default=None,
                        choices=list(SCAN_PROFILES.keys()),
                        help="Pre-built scan profile")
    parser.add_argument("--top", "-n", type=int, default=10,
                        help="Number of results to return")
    parser.add_argument("--symbols", "-s", type=str, nargs="*", default=None,
                        help="Custom list of symbols (overrides default universe)")
    parser.add_argument("--min-mcap", type=float, default=None,
                        help="Minimum market cap filter")
    parser.add_argument("--pe-min", type=float, default=None)
    parser.add_argument("--pe-max", type=float, default=None)
    parser.add_argument("--min-rev-growth", type=float, default=None,
                        help="Minimum revenue growth (decimal, e.g. 0.1 = 10%%)")
    parser.add_argument("--volume-spike", action="store_true",
                        help="Require volume >= 2x 20-day average")
    parser.add_argument("--breakout", action="store_true",
                        help="Require price breakout above resistance")
    parser.add_argument("--oversold", action="store_true",
                        help="Require RSI < 30")
    parser.add_argument("--earnings-days", type=int, default=None,
                        help="Require earnings within N days")

    args = parser.parse_args()

    pe_range = None
    if args.pe_min is not None or args.pe_max is not None:
        pe_range = (args.pe_min or 0, args.pe_max or 999)

    results = scan(
        universe=args.symbols,
        profile=args.profile,
        top_n=args.top,
        min_market_cap=args.min_mcap,
        pe_range=pe_range,
        min_revenue_growth=args.min_rev_growth,
        rsi_oversold=args.oversold,
        require_volume_spike=args.volume_spike,
        require_breakout=args.breakout,
        earnings_within_days=args.earnings_days,
    )

    if not results:
        print("No opportunities found matching criteria.")
    else:
        print(f"\n{'='*80}")
        print(f" Top {len(results)} Opportunities"
              + (f"  [profile: {args.profile}]" if args.profile else ""))
        print(f"{'='*80}\n")
        for i, r in enumerate(results, 1):
            print(f"  {i:>2}. {r['symbol']:<6}  Score: {r['score']:5.1f}  "
                  f"Price: ${r['price']:.2f}  RSI: {r['rsi']:.1f}  "
                  f"Vol Ratio: {r['volume_ratio']:.1f}x  "
                  f"1d: {r['pct_change_1d']:+.2f}%")
        print()
        print(json.dumps(results, indent=2, default=str))
