"""Market regime detection system.

Classifies the current market environment into one of six regimes
and provides strategy adjustment recommendations. Uses broad market
indicators — trend, volatility, breadth, credit, sentiment — to
build a composite regime score.
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REGIME_HISTORY_PATH = Path(__file__).resolve().parent.parent / "data" / "regime_history.json"

# Tickers used for signal generation
TICKERS = {
    "market": "SPY",
    "vix": "^VIX",
    "hyg": "HYG",       # High-yield corporate bonds
    "lqd": "LQD",       # Investment-grade corporate bonds
    "tlt": "TLT",       # Long-term treasuries
    "2y": "^IRX",       # 2-year proxy (13-week T-bill rate index)
    "10y": "^TNX",      # 10-year treasury yield index
}

# Sector ETFs: offensive (risk-on) vs defensive (risk-off)
OFFENSIVE_SECTORS = {"XLK": "Technology", "XLY": "Consumer Discretionary",
                     "XLI": "Industrials", "XLF": "Financials"}
DEFENSIVE_SECTORS = {"XLV": "Healthcare", "XLU": "Utilities",
                     "XLP": "Consumer Staples", "XLE": "Energy"}

LOOKBACK_PERIOD = "1y"
LOOKBACK_INTERVAL = "1d"


# ---------------------------------------------------------------------------
# Regime enum and strategy map
# ---------------------------------------------------------------------------

class MarketRegime(str, Enum):
    STRONG_BULL = "STRONG_BULL"
    BULL = "BULL"
    NEUTRAL = "NEUTRAL"
    BEAR = "BEAR"
    STRONG_BEAR = "STRONG_BEAR"
    VOLATILE = "VOLATILE"


STRATEGY_RECOMMENDATIONS: dict[MarketRegime, dict] = {
    MarketRegime.STRONG_BULL: {
        "position_size_multiplier": 1.25,
        "strategy": "momentum",
        "description": (
            "Aggressive positioning. Full or over-weight position sizes. "
            "Favour momentum and breakout strategies. Ride winners."
        ),
        "sector_bias": "offensive",
        "hedging": "minimal",
        "stop_loss_width": "tight",
    },
    MarketRegime.BULL: {
        "position_size_multiplier": 1.0,
        "strategy": "trend_following",
        "description": (
            "Normal position sizes. Follow established trends. "
            "Let profits run but protect with trailing stops."
        ),
        "sector_bias": "offensive",
        "hedging": "light",
        "stop_loss_width": "normal",
    },
    MarketRegime.NEUTRAL: {
        "position_size_multiplier": 0.65,
        "strategy": "mean_reversion",
        "description": (
            "Reduce position sizes. Prefer mean-reversion and range-bound "
            "strategies. Be very selective — quality over quantity."
        ),
        "sector_bias": "balanced",
        "hedging": "moderate",
        "stop_loss_width": "normal",
    },
    MarketRegime.BEAR: {
        "position_size_multiplier": 0.35,
        "strategy": "defensive",
        "description": (
            "Minimal long exposure. Rotate into defensive sectors and "
            "high-quality names. Hedge actively with puts or inverse ETFs."
        ),
        "sector_bias": "defensive",
        "hedging": "heavy",
        "stop_loss_width": "tight",
    },
    MarketRegime.STRONG_BEAR: {
        "position_size_multiplier": 0.10,
        "strategy": "capital_preservation",
        "description": (
            "Preserve capital. Move to cash and T-bills. "
            "Only consider short opportunities with strict risk limits."
        ),
        "sector_bias": "cash_and_treasuries",
        "hedging": "maximum",
        "stop_loss_width": "very_tight",
    },
    MarketRegime.VOLATILE: {
        "position_size_multiplier": 0.50,
        "strategy": "reduced_volatility",
        "description": (
            "High volatility without clear direction. Reduce size, widen "
            "stops to avoid whipsaws, shorten holding periods. "
            "Sell premium (options) if available."
        ),
        "sector_bias": "balanced",
        "hedging": "moderate",
        "stop_loss_width": "wide",
    },
}


# ---------------------------------------------------------------------------
# Data classes for signal outputs
# ---------------------------------------------------------------------------

@dataclass
class SignalResult:
    """One directional signal contributing to regime classification."""
    name: str
    value: float              # raw numeric value
    score: float              # normalised to [-1, +1]: -1=very bearish, +1=very bullish
    interpretation: str       # human-readable summary


@dataclass
class RegimeResult:
    """Full regime detection output."""
    regime: MarketRegime
    composite_score: float              # [-1, +1]
    confidence: float                   # [0, 1]
    signals: list[SignalResult]
    strategy: dict
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        d = asdict(self)
        d["regime"] = self.regime.value
        return d


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fetch_history(symbol: str, period: str = LOOKBACK_PERIOD,
                   interval: str = LOOKBACK_INTERVAL) -> pd.DataFrame:
    """Download OHLCV history via yfinance, returning an empty frame on error."""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        if df.empty:
            logger.warning("No data returned for %s", symbol)
        return df
    except Exception as exc:
        logger.error("Failed to fetch %s: %s", symbol, exc)
        return pd.DataFrame()


def _safe_iloc(series: pd.Series, idx: int, default: float = np.nan) -> float:
    """Index into a series without blowing up on short data."""
    try:
        return float(series.iloc[idx])
    except (IndexError, KeyError):
        return default


# ---------------------------------------------------------------------------
# Individual signal generators
# ---------------------------------------------------------------------------

def _spy_trend_signal() -> SignalResult:
    """S&P 500 trend: price vs 50/200 SMA, golden/death cross."""
    df = _fetch_history("SPY")
    if df.empty or len(df) < 200:
        return SignalResult("spy_trend", 0.0, 0.0, "Insufficient SPY data")

    close = df["Close"]
    current = float(close.iloc[-1])
    sma50 = float(close.rolling(50).mean().iloc[-1])
    sma200 = float(close.rolling(200).mean().iloc[-1])

    # How far above/below the 200-SMA (percent)
    distance_200 = (current - sma200) / sma200

    # Golden cross / death cross detection (50-SMA vs 200-SMA)
    sma50_prev = float(close.rolling(50).mean().iloc[-2])
    sma200_prev = float(close.rolling(200).mean().iloc[-2])
    golden_cross = sma50 > sma200 and sma50_prev <= sma200_prev
    death_cross = sma50 < sma200 and sma50_prev >= sma200_prev

    # Score: combine relative position and cross events
    score = np.clip(distance_200 * 5, -1, 1)  # +-20% maps to +-1
    if current > sma50 > sma200:
        score = max(score, 0.4)
    elif current < sma50 < sma200:
        score = min(score, -0.4)

    if golden_cross:
        score = min(score + 0.3, 1.0)
    if death_cross:
        score = max(score - 0.3, -1.0)

    parts = []
    parts.append(f"SPY {current:.2f}")
    parts.append(f"50-SMA {sma50:.2f}")
    parts.append(f"200-SMA {sma200:.2f}")
    if golden_cross:
        parts.append("GOLDEN CROSS")
    if death_cross:
        parts.append("DEATH CROSS")
    above_below_50 = "above" if current > sma50 else "below"
    above_below_200 = "above" if current > sma200 else "below"
    parts.append(f"Price {above_below_50} 50-SMA, {above_below_200} 200-SMA")

    return SignalResult("spy_trend", distance_200, round(score, 3), " | ".join(parts))


def _vix_signal() -> SignalResult:
    """VIX level and trend — fear gauge."""
    df = _fetch_history("^VIX")
    if df.empty or len(df) < 20:
        return SignalResult("vix", 0.0, 0.0, "Insufficient VIX data")

    close = df["Close"]
    current_vix = float(close.iloc[-1])
    sma20 = float(close.rolling(20).mean().iloc[-1])

    # VIX thresholds (common market conventions)
    # <15 = complacent, 15-20 = normal, 20-30 = elevated, 30-40 = high fear, >40 = panic
    if current_vix < 15:
        score = 0.8   # low fear = bullish
    elif current_vix < 20:
        score = 0.4
    elif current_vix < 25:
        score = 0.0
    elif current_vix < 30:
        score = -0.4
    elif current_vix < 40:
        score = -0.7
    else:
        score = -1.0

    # Adjust for trend: rising VIX is more bearish
    vix_trend = (current_vix - sma20) / sma20
    score -= np.clip(vix_trend * 2, -0.3, 0.3)
    score = float(np.clip(score, -1, 1))

    interp = f"VIX {current_vix:.2f} (20-SMA {sma20:.2f})"
    if current_vix > 30:
        interp += " — HIGH FEAR"
    elif current_vix < 15:
        interp += " — LOW FEAR / COMPLACENCY"

    return SignalResult("vix", current_vix, round(score, 3), interp)


def _breadth_signal() -> SignalResult:
    """Advance/decline breadth proxy using S&P 500 sector participation.

    True breadth data (NYSE A/D line) is not available in yfinance.  We
    approximate breadth by checking what fraction of the 11 sector ETFs
    are trading above their own 50-day SMA — a widely-used participation
    measure.
    """
    all_sectors = list(OFFENSIVE_SECTORS.keys()) + list(DEFENSIVE_SECTORS.keys())
    above_count = 0
    total = 0

    for etf in all_sectors:
        df = _fetch_history(etf, period="6mo")
        if df.empty or len(df) < 50:
            continue
        close = df["Close"]
        current = float(close.iloc[-1])
        sma50 = float(close.rolling(50).mean().iloc[-1])
        total += 1
        if current > sma50:
            above_count += 1

    if total == 0:
        return SignalResult("breadth", 0.0, 0.0, "No sector data")

    pct_above = above_count / total
    # Map: 0% -> -1, 50% -> 0, 100% -> +1
    score = float(np.clip((pct_above - 0.5) * 2, -1, 1))
    interp = f"{above_count}/{total} sectors above 50-SMA ({pct_above:.0%} participation)"
    return SignalResult("breadth", pct_above, round(score, 3), interp)


def _sector_rotation_signal() -> SignalResult:
    """Relative performance of offensive vs defensive sectors (20-day return)."""
    def _sector_return(etf: str) -> Optional[float]:
        df = _fetch_history(etf, period="3mo")
        if df.empty or len(df) < 20:
            return None
        close = df["Close"]
        return float((close.iloc[-1] / close.iloc[-20]) - 1)

    off_returns = [r for etf in OFFENSIVE_SECTORS if (r := _sector_return(etf)) is not None]
    def_returns = [r for etf in DEFENSIVE_SECTORS if (r := _sector_return(etf)) is not None]

    if not off_returns or not def_returns:
        return SignalResult("sector_rotation", 0.0, 0.0, "Insufficient sector data")

    avg_off = np.mean(off_returns)
    avg_def = np.mean(def_returns)
    spread = avg_off - avg_def  # positive = risk-on outperforming

    score = float(np.clip(spread * 10, -1, 1))  # +-10% spread maps to +-1
    interp = (f"Offensive avg 20d return {avg_off:+.2%} vs "
              f"Defensive {avg_def:+.2%} (spread {spread:+.2%})")
    if spread > 0.02:
        interp += " — RISK-ON"
    elif spread < -0.02:
        interp += " — RISK-OFF rotation"

    return SignalResult("sector_rotation", spread, round(score, 3), interp)


def _yield_curve_signal() -> SignalResult:
    """2y/10y yield spread — recession indicator.

    Uses ^TNX (10-year yield) and ^IRX (13-week T-bill yield) as a proxy
    for the 2y-10y spread because yfinance does not carry a clean 2-year
    yield series.  An inverted curve (negative spread) historically
    precedes recessions.
    """
    df_10y = _fetch_history("^TNX", period="6mo")
    df_2y = _fetch_history("^IRX", period="6mo")

    if df_10y.empty or df_2y.empty or len(df_10y) < 5 or len(df_2y) < 5:
        return SignalResult("yield_curve", 0.0, 0.0, "Insufficient yield data")

    # ^TNX and ^IRX report yields as values (e.g., 4.3 means 4.3%)
    y10 = float(df_10y["Close"].iloc[-1])
    y2 = float(df_2y["Close"].iloc[-1])
    spread = y10 - y2  # positive = normal curve, negative = inverted

    # Score: -1 (deeply inverted) to +1 (steep positive)
    # A spread of +2% or more is very bullish; -1% or worse is very bearish
    score = float(np.clip(spread / 2.0, -1, 1))
    state = "INVERTED" if spread < 0 else "NORMAL"
    interp = f"10Y {y10:.2f}% - 2Y proxy {y2:.2f}% = {spread:+.2f}% ({state})"
    return SignalResult("yield_curve", spread, round(score, 3), interp)


def _credit_spread_signal() -> SignalResult:
    """Credit spread: HYG vs LQD relative performance — stress indicator.

    When HYG (high-yield junk bonds) underperforms LQD (investment-grade),
    it signals credit stress and risk aversion.
    """
    df_hyg = _fetch_history("HYG", period="6mo")
    df_lqd = _fetch_history("LQD", period="6mo")

    if df_hyg.empty or df_lqd.empty or len(df_hyg) < 20 or len(df_lqd) < 20:
        return SignalResult("credit_spread", 0.0, 0.0, "Insufficient credit data")

    # 20-day relative performance
    hyg_ret = float(df_hyg["Close"].iloc[-1] / df_hyg["Close"].iloc[-20] - 1)
    lqd_ret = float(df_lqd["Close"].iloc[-1] / df_lqd["Close"].iloc[-20] - 1)
    spread = hyg_ret - lqd_ret  # positive = risk appetite healthy

    score = float(np.clip(spread * 20, -1, 1))  # +-5% maps to +-1
    interp = (f"HYG 20d ret {hyg_ret:+.2%} vs LQD {lqd_ret:+.2%} "
              f"(spread {spread:+.2%})")
    if spread < -0.01:
        interp += " — CREDIT STRESS"
    return SignalResult("credit_spread", spread, round(score, 3), interp)


def _put_call_signal() -> SignalResult:
    """Put/call ratio proxy via VIX term structure.

    True CBOE put/call ratio is not in yfinance.  We approximate
    sentiment extremes using the VIX level relative to its own
    historical percentile over the past year.
    """
    df = _fetch_history("^VIX", period="1y")
    if df.empty or len(df) < 60:
        return SignalResult("put_call_proxy", 0.0, 0.0, "Insufficient VIX data for sentiment")

    close = df["Close"]
    current = float(close.iloc[-1])
    percentile = float((close < current).mean())  # fraction of days with lower VIX

    # High percentile = VIX is elevated = bearish sentiment (contrarian bullish at extremes)
    # We score it directionally: extreme fear = bearish (not contrarian here,
    # since regime detection cares about the current state, not the mean-reversion trade).
    if percentile > 0.90:
        score = -0.9  # extreme fear
    elif percentile > 0.75:
        score = -0.5
    elif percentile > 0.50:
        score = -0.1
    elif percentile > 0.25:
        score = 0.3
    elif percentile > 0.10:
        score = 0.6
    else:
        score = 0.8   # extreme complacency

    interp = f"VIX at {percentile:.0%} percentile (1Y). Current {current:.2f}"
    if percentile > 0.80:
        interp += " — EXTREME FEAR"
    elif percentile < 0.15:
        interp += " — EXTREME COMPLACENCY"

    return SignalResult("put_call_proxy", percentile, round(score, 3), interp)


def _highs_lows_signal() -> SignalResult:
    """New 52-week highs vs lows proxy.

    yfinance doesn't provide NYSE new-highs/new-lows directly.
    We approximate by checking a broad basket of sector ETFs: how many
    are within 5% of their 52-week high vs within 5% of their 52-week low.
    """
    all_etfs = list(OFFENSIVE_SECTORS.keys()) + list(DEFENSIVE_SECTORS.keys())
    near_high = 0
    near_low = 0
    total = 0

    for etf in all_etfs:
        df = _fetch_history(etf, period="1y")
        if df.empty or len(df) < 50:
            continue
        close = df["Close"]
        current = float(close.iloc[-1])
        high_52 = float(close.max())
        low_52 = float(close.min())
        total += 1
        if high_52 > 0 and (high_52 - current) / high_52 <= 0.05:
            near_high += 1
        if low_52 > 0 and (current - low_52) / low_52 <= 0.05:
            near_low += 1

    if total == 0:
        return SignalResult("highs_lows", 0.0, 0.0, "No data for highs/lows")

    net = near_high - near_low
    ratio = net / total  # -1 to +1 range
    score = float(np.clip(ratio, -1, 1))
    interp = (f"{near_high} ETFs near 52w high, {near_low} near 52w low "
              f"(net {net:+d} out of {total})")
    return SignalResult("highs_lows", ratio, round(score, 3), interp)


# ---------------------------------------------------------------------------
# Volatility measurement (used in regime classification, not as a
# directional signal)
# ---------------------------------------------------------------------------

def _volatility_level() -> float:
    """Return current realised volatility percentile (0-1) of SPY over the
    past year, using 20-day rolling standard deviation of daily returns."""
    df = _fetch_history("SPY", period="1y")
    if df.empty or len(df) < 40:
        return 0.5  # default neutral

    returns = df["Close"].pct_change().dropna()
    rolling_vol = returns.rolling(20).std().dropna()
    if rolling_vol.empty:
        return 0.5

    current_vol = float(rolling_vol.iloc[-1])
    percentile = float((rolling_vol < current_vol).mean())
    return percentile


# ---------------------------------------------------------------------------
# Composite regime classifier
# ---------------------------------------------------------------------------

# Signal weights (sum to 1)
SIGNAL_WEIGHTS = {
    "spy_trend": 0.25,
    "vix": 0.15,
    "breadth": 0.15,
    "sector_rotation": 0.10,
    "yield_curve": 0.10,
    "credit_spread": 0.10,
    "put_call_proxy": 0.08,
    "highs_lows": 0.07,
}


def _classify_regime(composite: float, vol_percentile: float) -> MarketRegime:
    """Map composite score and volatility into a regime.

    Parameters
    ----------
    composite : float
        Weighted average of all signal scores, range [-1, +1].
    vol_percentile : float
        Current realised-volatility percentile over the past year [0, 1].
    """
    high_vol = vol_percentile > 0.75

    # High volatility with no clear direction -> VOLATILE regime
    if high_vol and -0.20 <= composite <= 0.20:
        return MarketRegime.VOLATILE

    if composite >= 0.55:
        return MarketRegime.STRONG_BULL
    elif composite >= 0.20:
        return MarketRegime.BULL
    elif composite >= -0.20:
        return MarketRegime.NEUTRAL
    elif composite >= -0.55:
        return MarketRegime.BEAR
    else:
        return MarketRegime.STRONG_BEAR


def _compute_confidence(signals: list[SignalResult]) -> float:
    """Confidence = agreement among signals (1 = all agree, 0 = split).

    We use the standard deviation of signal scores — lower spread means
    higher agreement and therefore higher confidence.
    """
    scores = [s.score for s in signals if s.score != 0.0]
    if len(scores) < 2:
        return 0.5
    std = float(np.std(scores))
    # max possible std for [-1,1] range is 1.0
    confidence = max(0.0, 1.0 - std)
    return round(confidence, 3)


# ---------------------------------------------------------------------------
# Regime history persistence
# ---------------------------------------------------------------------------

def _load_regime_history() -> list[dict]:
    """Load regime history from disk."""
    if REGIME_HISTORY_PATH.exists():
        try:
            with open(REGIME_HISTORY_PATH, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as exc:
            logger.warning("Could not load regime history: %s", exc)
    return []


def _save_regime_history(history: list[dict]) -> None:
    """Persist regime history to disk, keeping the last 500 entries."""
    REGIME_HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    history = history[-500:]
    with open(REGIME_HISTORY_PATH, "w") as f:
        json.dump(history, f, indent=2)


def _record_regime(result: RegimeResult) -> None:
    """Append current regime to history if it differs from the last entry
    (or if enough time has passed since the last recording)."""
    history = _load_regime_history()

    entry = {
        "timestamp": result.timestamp,
        "regime": result.regime.value,
        "composite_score": result.composite_score,
        "confidence": result.confidence,
    }

    # Only record if regime changed or last entry is >12h old
    if history:
        last = history[-1]
        last_ts = datetime.fromisoformat(last["timestamp"])
        now = datetime.fromisoformat(result.timestamp)
        same_regime = last.get("regime") == result.regime.value
        recent = (now - last_ts) < timedelta(hours=12)
        if same_regime and recent:
            return

    history.append(entry)
    _save_regime_history(history)


def get_regime_history(last_n: int = 30) -> list[dict]:
    """Return the most recent *last_n* regime-change records."""
    history = _load_regime_history()
    return history[-last_n:]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def detect_regime(verbose: bool = False) -> RegimeResult:
    """Run all signal generators, compute composite score, classify regime.

    Parameters
    ----------
    verbose : bool
        If True, log detailed signal information to stdout.

    Returns
    -------
    RegimeResult with regime classification, score, confidence,
    individual signals, and strategy recommendations.
    """
    logger.info("Running market regime detection ...")

    # Collect signals
    signal_funcs = [
        _spy_trend_signal,
        _vix_signal,
        _breadth_signal,
        _sector_rotation_signal,
        _yield_curve_signal,
        _credit_spread_signal,
        _put_call_signal,
        _highs_lows_signal,
    ]

    signals: list[SignalResult] = []
    for fn in signal_funcs:
        try:
            sig = fn()
            signals.append(sig)
            if verbose:
                logger.info("  [%s] score=%.3f  %s", sig.name, sig.score, sig.interpretation)
        except Exception as exc:
            logger.error("Signal %s failed: %s", fn.__name__, exc)
            signals.append(SignalResult(fn.__name__, 0.0, 0.0, f"ERROR: {exc}"))

    # Weighted composite score
    composite = 0.0
    total_weight = 0.0
    for sig in signals:
        w = SIGNAL_WEIGHTS.get(sig.name, 0.0)
        composite += sig.score * w
        total_weight += w

    if total_weight > 0:
        composite /= total_weight  # normalise in case some signals are missing

    composite = round(float(np.clip(composite, -1, 1)), 4)

    # Volatility overlay
    vol_pct = _volatility_level()

    # Classify
    regime = _classify_regime(composite, vol_pct)
    confidence = _compute_confidence(signals)
    strategy = STRATEGY_RECOMMENDATIONS[regime]

    result = RegimeResult(
        regime=regime,
        composite_score=composite,
        confidence=confidence,
        signals=signals,
        strategy=strategy,
    )

    # Record to history
    try:
        _record_regime(result)
    except Exception as exc:
        logger.warning("Could not save regime history: %s", exc)

    logger.info("Regime detected: %s (score=%.3f, confidence=%.2f)",
                regime.value, composite, confidence)

    return result


def get_strategy_for_regime(regime: MarketRegime) -> dict:
    """Look up the strategy recommendation for a given regime."""
    return STRATEGY_RECOMMENDATIONS[regime]


def print_regime_report(result: Optional[RegimeResult] = None) -> str:
    """Generate a human-readable regime report.

    If *result* is not provided, runs detect_regime() first.
    """
    if result is None:
        result = detect_regime(verbose=True)

    lines = [
        "=" * 64,
        "  MARKET REGIME REPORT",
        f"  Timestamp: {result.timestamp}",
        "=" * 64,
        "",
        f"  Regime:           {result.regime.value}",
        f"  Composite Score:  {result.composite_score:+.4f}  (range: -1 to +1)",
        f"  Confidence:       {result.confidence:.1%}",
        "",
        "-" * 64,
        "  SIGNALS",
        "-" * 64,
    ]
    for sig in result.signals:
        lines.append(f"  [{sig.name:<20s}]  score={sig.score:+.3f}  {sig.interpretation}")

    lines += [
        "",
        "-" * 64,
        "  STRATEGY RECOMMENDATION",
        "-" * 64,
        f"  Position size multiplier: {result.strategy['position_size_multiplier']}x",
        f"  Primary strategy:        {result.strategy['strategy']}",
        f"  Sector bias:             {result.strategy['sector_bias']}",
        f"  Hedging level:           {result.strategy['hedging']}",
        f"  Stop-loss width:         {result.strategy['stop_loss_width']}",
        "",
        f"  {result.strategy['description']}",
        "",
        "=" * 64,
    ]

    # Recent regime history
    history = get_regime_history(10)
    if history:
        lines += [
            "  RECENT REGIME HISTORY",
            "-" * 64,
        ]
        for entry in history:
            lines.append(
                f"  {entry['timestamp'][:19]}  {entry['regime']:<14s}  "
                f"score={entry['composite_score']:+.4f}  conf={entry['confidence']:.1%}"
            )
        lines.append("=" * 64)

    report = "\n".join(lines)
    return report


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    report = print_regime_report()
    print(report)
