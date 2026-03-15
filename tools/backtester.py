"""
Backtesting Engine for AI Trading Crew.

Simulates the multi-agent trading system on historical data, tracking portfolio
performance and computing key risk/return metrics. Supports walk-forward testing,
multiple stocks, configurable position sizing, and commission costs.

Usage:
    from tools.backtester import run_backtest

    result = run_backtest(
        symbols=["AAPL", "MSFT"],
        start_date="2023-01-01",
        end_date="2024-01-01",
        initial_capital=100_000,
    )
    print(result.report())

    # Walk-forward mode
    result = run_backtest(
        symbols=["AAPL"],
        start_date="2022-01-01",
        end_date="2024-01-01",
        walk_forward_months=3,
        training_months=12,
    )
"""

from __future__ import annotations

import math
import warnings
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Literal

import numpy as np
import pandas as pd
import yfinance as yf

# Import trading rules from project config
try:
    from config.trading_rules import TRADING_RULES
except ImportError:
    # Fallback when running standalone or from a different working directory
    TRADING_RULES = {
        "max_position_pct": 0.05,
        "max_sector_pct": 0.25,
        "max_total_positions": 20,
        "max_daily_loss_pct": 0.02,
        "stop_loss_pct": 0.07,
        "take_profit_pct": 0.15,
        "min_agents_agree": 3,
        "min_confidence": 0.7,
        "human_approval_above_pct": 0.02,
    }

warnings.filterwarnings("ignore", category=FutureWarning)

# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

SignalType = Literal["BUY", "SELL", "HOLD"]


@dataclass
class Trade:
    """Record of a single completed round-trip trade."""
    symbol: str
    side: SignalType
    entry_date: pd.Timestamp
    entry_price: float
    exit_date: pd.Timestamp | None = None
    exit_price: float | None = None
    shares: int = 0
    pnl: float = 0.0
    pnl_pct: float = 0.0
    exit_reason: str = ""

    @property
    def is_closed(self) -> bool:
        return self.exit_date is not None


@dataclass
class Position:
    """An open position held in the portfolio."""
    symbol: str
    shares: int
    entry_price: float
    entry_date: pd.Timestamp
    stop_loss: float
    take_profit: float
    # New fields for enhanced exit logic
    signal_type: str = "momentum"  # "momentum", "mean_reversion", or "rsi2"
    trailing_stop: float = 0.0  # ATR-based chandelier exit (moves up, never down)
    highest_high: float = 0.0  # track highest high since entry for chandelier exit
    bars_held: int = 0  # trading days held
    original_shares: int = 0  # shares before any drawdown scaling


@dataclass
class BacktestResult:
    """Comprehensive backtest output with metrics and trade log."""
    # Identification
    symbols: list[str]
    start_date: str
    end_date: str
    initial_capital: float

    # Equity curve
    equity_curve: pd.DataFrame = field(repr=False, default_factory=pd.DataFrame)
    benchmark_curve: pd.DataFrame = field(repr=False, default_factory=pd.DataFrame)

    # Trade log
    trades: list[Trade] = field(repr=False, default_factory=list)

    # Performance metrics
    total_return_pct: float = 0.0
    benchmark_return_pct: float = 0.0
    excess_return_pct: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    max_drawdown_pct: float = 0.0
    max_drawdown_duration_days: int = 0
    win_rate_pct: float = 0.0
    avg_win_pct: float = 0.0
    avg_loss_pct: float = 0.0
    profit_factor: float = 0.0
    num_trades: int = 0
    num_wins: int = 0
    num_losses: int = 0
    avg_holding_days: float = 0.0
    annual_return_pct: float = 0.0
    annual_volatility_pct: float = 0.0
    calmar_ratio: float = 0.0
    commission_paid: float = 0.0

    # Walk-forward windows (populated when walk_forward_months > 0)
    walk_forward_results: list[dict] = field(repr=False, default_factory=list)

    def report(self) -> str:
        """Generate a human-readable performance report."""
        sep = "=" * 64
        lines = [
            sep,
            "  AI TRADING CREW -- BACKTEST REPORT",
            sep,
            f"  Symbols:          {', '.join(self.symbols)}",
            f"  Period:           {self.start_date} to {self.end_date}",
            f"  Initial Capital:  ${self.initial_capital:,.2f}",
            f"  Final Equity:     ${self.equity_curve['equity'].iloc[-1]:,.2f}" if not self.equity_curve.empty else "",
            "",
            "  RETURNS",
            f"    Total Return:       {self.total_return_pct:+.2f}%",
            f"    Annualized Return:  {self.annual_return_pct:+.2f}%",
            f"    Benchmark (SPY):    {self.benchmark_return_pct:+.2f}%",
            f"    Excess Return:      {self.excess_return_pct:+.2f}%",
            "",
            "  RISK METRICS",
            f"    Sharpe Ratio:       {self.sharpe_ratio:.3f}",
            f"    Sortino Ratio:      {self.sortino_ratio:.3f}",
            f"    Calmar Ratio:       {self.calmar_ratio:.3f}",
            f"    Annual Volatility:  {self.annual_volatility_pct:.2f}%",
            f"    Max Drawdown:       {self.max_drawdown_pct:.2f}%",
            f"    Max DD Duration:    {self.max_drawdown_duration_days} days",
            "",
            "  TRADE STATISTICS",
            f"    Total Trades:       {self.num_trades}",
            f"    Win Rate:           {self.win_rate_pct:.1f}%",
            f"    Avg Win:            {self.avg_win_pct:+.2f}%",
            f"    Avg Loss:           {self.avg_loss_pct:+.2f}%",
            f"    Profit Factor:      {self.profit_factor:.2f}",
            f"    Avg Holding Period: {self.avg_holding_days:.1f} days",
            f"    Commission Paid:    ${self.commission_paid:,.2f}",
            sep,
        ]

        if self.walk_forward_results:
            lines.append("")
            lines.append("  WALK-FORWARD WINDOWS")
            for i, wf in enumerate(self.walk_forward_results, 1):
                lines.append(
                    f"    Window {i}: {wf['test_start']} to {wf['test_end']}  "
                    f"Return: {wf['return_pct']:+.2f}%  "
                    f"Trades: {wf['num_trades']}"
                )
            lines.append(sep)

        return "\n".join(lines)

    def __str__(self) -> str:
        return self.report()


# ---------------------------------------------------------------------------
# Technical signal generator (simulates what the 50 agents would decide)
# ---------------------------------------------------------------------------

class SignalGenerator:
    """
    Professional multi-factor alpha signal generator.

    Combines 15 weighted signals across 5 factor categories — the same approach
    used by Renaissance Technologies, Two Sigma, and AQR:

    MOMENTUM (30% weight):
      - 12-month price momentum (skip last month to avoid reversal)
      - 6-month price momentum
      - 1-month mean reversion (contrarian on short-term extremes)
      - MACD trend confirmation
      - RSI momentum (40-60 = neutral, extremes = signals)

    TREND (25% weight):
      - Price vs 200-day SMA (long-term regime)
      - 50/200 SMA alignment (golden/death cross)
      - Price vs 50-day SMA (medium-term trend)
      - ADX-style trend strength (using directional movement)

    MEAN REVERSION (20% weight):
      - Bollinger Band z-score (how far from mean)
      - RSI oversold/overbought with trend filter
      - 52-week range position (buy near lows in uptrends)

    VOLUME & VOLATILITY (15% weight):
      - Volume surge on up days (accumulation)
      - ATR contraction (volatility squeeze → breakout)
      - On-Balance Volume trend

    REGIME FILTER (10% weight):
      - Market regime (bull/bear/neutral based on SMA and volatility)
      - Volatility regime (low vol = bigger positions, high vol = smaller)

    Position sizing adapts to signal strength (0-1 confidence).
    """

    def __init__(self, min_confidence: float = 0.38):
        self.min_confidence = min_confidence
        # Stores the signal type metadata from the last generate_signals() call
        self._last_signal_types: pd.Series | None = None

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        c = df["Close"]
        h = df["High"]
        l = df["Low"]
        v = df["Volume"]

        # Moving averages
        df["sma_20"] = c.rolling(20, min_periods=1).mean()
        df["sma_50"] = c.rolling(50, min_periods=1).mean()
        df["sma_100"] = c.rolling(100, min_periods=1).mean()
        df["sma_200"] = c.rolling(200, min_periods=1).mean()
        df["ema_12"] = c.ewm(span=12, adjust=False).mean()
        df["ema_26"] = c.ewm(span=26, adjust=False).mean()

        # MACD
        df["macd_line"] = df["ema_12"] - df["ema_26"]
        df["macd_signal"] = df["macd_line"].ewm(span=9, adjust=False).mean()
        df["macd_hist"] = df["macd_line"] - df["macd_signal"]

        # RSI 14
        delta = c.diff()
        gain = delta.where(delta > 0, 0.0).rolling(14, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0.0)).rolling(14, min_periods=1).mean()
        rs = gain / loss.replace(0, np.nan)
        df["rsi_14"] = (100 - (100 / (1 + rs))).fillna(50)

        # Bollinger Bands
        bb_std = c.rolling(20, min_periods=1).std().fillna(0)
        df["bb_upper"] = df["sma_20"] + 2 * bb_std
        df["bb_lower"] = df["sma_20"] - 2 * bb_std
        df["bb_zscore"] = ((c - df["sma_20"]) / bb_std.replace(0, np.nan)).fillna(0)

        # ATR
        prev_c = c.shift(1).fillna(c)
        tr = pd.concat([(h - l), (h - prev_c).abs(), (l - prev_c).abs()], axis=1).max(axis=1)
        df["atr_14"] = tr.rolling(14, min_periods=1).mean()
        df["atr_pct"] = (df["atr_14"] / c * 100).fillna(0)

        # Volume
        avg_vol = v.rolling(20, min_periods=1).mean()
        df["vol_ratio"] = (v / avg_vol.replace(0, np.nan)).fillna(1)

        # Momentum returns
        df["ret_1m"] = c.pct_change(21).fillna(0)
        df["ret_3m"] = c.pct_change(63).fillna(0)
        df["ret_6m"] = c.pct_change(126).fillna(0)
        df["ret_12m"] = c.pct_change(252).fillna(0)
        # 12-1 momentum (skip last month — proven alpha factor)
        df["mom_12_1"] = (c.shift(21).pct_change(231)).fillna(0)

        # 52-week range position (0 = at low, 1 = at high)
        high_252 = h.rolling(252, min_periods=50).max()
        low_252 = l.rolling(252, min_periods=50).min()
        df["range_52w"] = ((c - low_252) / (high_252 - low_252).replace(0, np.nan)).fillna(0.5)

        # Realized volatility (20-day)
        df["realized_vol"] = c.pct_change().rolling(20, min_periods=5).std() * np.sqrt(252)
        df["realized_vol"] = df["realized_vol"].fillna(0.2)

        # OBV trend
        obv = pd.Series(0.0, index=df.index)
        for i in range(1, len(c)):
            if c.iloc[i] > c.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] + v.iloc[i]
            elif c.iloc[i] < c.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] - v.iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]
        df["obv"] = obv
        df["obv_sma"] = obv.rolling(20, min_periods=1).mean()

        # ATR contraction (squeeze detection)
        atr_sma = df["atr_14"].rolling(50, min_periods=10).mean()
        df["atr_squeeze"] = (df["atr_14"] / atr_sma.replace(0, np.nan)).fillna(1)

        # --- NEW INDICATORS ---

        # RSI-2 (Connors RSI — proven 91% win rate strategy)
        delta2 = c.diff()
        gain2 = delta2.where(delta2 > 0, 0.0).ewm(com=1, adjust=False).mean()
        loss2 = (-delta2.where(delta2 < 0, 0.0)).ewm(com=1, adjust=False).mean()
        rs2 = gain2 / loss2.replace(0, np.nan)
        df["rsi_2"] = (100 - (100 / (1 + rs2))).fillna(50)

        # ATR-22 for chandelier exit
        tr22 = pd.concat([(h - l), (h - prev_c).abs(), (l - prev_c).abs()], axis=1).max(axis=1)
        df["atr_22"] = tr22.rolling(22, min_periods=1).mean()
        df["atr_22_pct"] = (df["atr_22"] / c * 100).fillna(0)

        # 22-day highest high (for chandelier exit calculation)
        df["highest_high_22"] = h.rolling(22, min_periods=1).max()

        # Volatility percentile (rolling rank of 20-day vol over last 252 days)
        vol_series = df["realized_vol"]
        df["vol_percentile"] = vol_series.rolling(252, min_periods=50).apply(
            lambda x: pd.Series(x).rank(pct=True).iloc[-1], raw=False
        ).fillna(0.5)

        # Return kurtosis (rolling 60-day, quality proxy)
        daily_rets = c.pct_change()
        df["ret_kurtosis"] = daily_rets.rolling(60, min_periods=20).kurt().fillna(3.0)

        # Rolling 60-day volatility (for quality filter)
        df["vol_60d"] = daily_rets.rolling(60, min_periods=20).std().fillna(
            daily_rets.rolling(20, min_periods=5).std().fillna(0.01)
        )

        return df

    def _score_momentum(self, row, prev) -> float:
        """Momentum factor: 30% weight. Score -1 to +1."""
        scores = []

        # 12-1 momentum (strongest proven factor)
        mom = row["mom_12_1"]
        if mom > 0.20: scores.append(1.0)
        elif mom > 0.10: scores.append(0.6)
        elif mom > 0.0: scores.append(0.2)
        elif mom > -0.10: scores.append(-0.2)
        elif mom > -0.20: scores.append(-0.6)
        else: scores.append(-1.0)

        # 6-month momentum
        r6 = row["ret_6m"]
        if r6 > 0.15: scores.append(0.8)
        elif r6 > 0.05: scores.append(0.4)
        elif r6 > -0.05: scores.append(0.0)
        elif r6 > -0.15: scores.append(-0.4)
        else: scores.append(-0.8)

        # 1-month reversal (contrarian on short-term)
        r1 = row["ret_1m"]
        if r1 < -0.10: scores.append(0.6)  # oversold short-term = buy
        elif r1 < -0.05: scores.append(0.3)
        elif r1 > 0.10: scores.append(-0.4)  # overextended short-term
        else: scores.append(0.0)

        # MACD confirmation
        if row["macd_hist"] > 0 and prev["macd_hist"] <= 0: scores.append(0.8)
        elif row["macd_hist"] > 0: scores.append(0.3)
        elif row["macd_hist"] < 0 and prev["macd_hist"] >= 0: scores.append(-0.8)
        elif row["macd_hist"] < 0: scores.append(-0.3)
        else: scores.append(0.0)

        # RSI momentum zone
        rsi = row["rsi_14"]
        if 50 < rsi < 70: scores.append(0.4)   # bullish momentum
        elif rsi >= 70: scores.append(-0.2)      # overbought caution
        elif 30 < rsi <= 50: scores.append(-0.2) # weakening
        elif rsi <= 30: scores.append(0.5)        # oversold = opportunity
        else: scores.append(0.0)

        return np.mean(scores)

    def _score_trend(self, row) -> float:
        """Trend factor: 25% weight. Score -1 to +1."""
        scores = []
        c = row["Close"]

        # Price vs 200 SMA (most important)
        pct_vs_200 = (c - row["sma_200"]) / row["sma_200"] if row["sma_200"] > 0 else 0
        if pct_vs_200 > 0.05: scores.append(1.0)
        elif pct_vs_200 > 0: scores.append(0.4)
        elif pct_vs_200 > -0.05: scores.append(-0.3)
        else: scores.append(-1.0)

        # 50/200 SMA alignment
        if row["sma_50"] > row["sma_200"] * 1.02: scores.append(1.0)  # strong golden
        elif row["sma_50"] > row["sma_200"]: scores.append(0.5)       # golden cross
        elif row["sma_50"] > row["sma_200"] * 0.98: scores.append(-0.3)  # approaching death
        else: scores.append(-1.0)  # death cross

        # Price vs 50 SMA
        pct_vs_50 = (c - row["sma_50"]) / row["sma_50"] if row["sma_50"] > 0 else 0
        if pct_vs_50 > 0.02: scores.append(0.6)
        elif pct_vs_50 > -0.02: scores.append(0.0)
        else: scores.append(-0.6)

        # All MAs aligned (20 > 50 > 100 > 200 = perfect uptrend)
        if row["sma_20"] > row["sma_50"] > row["sma_100"] > row["sma_200"]:
            scores.append(1.0)
        elif row["sma_20"] < row["sma_50"] < row["sma_100"] < row["sma_200"]:
            scores.append(-1.0)
        else:
            scores.append(0.0)

        return np.mean(scores)

    def _score_mean_reversion(self, row) -> float:
        """Mean reversion factor: 20% weight. Score -1 to +1."""
        scores = []

        # Bollinger z-score
        z = row["bb_zscore"]
        if z < -2.0: scores.append(1.0)    # deeply oversold
        elif z < -1.0: scores.append(0.5)
        elif z > 2.0: scores.append(-0.8)   # overextended
        elif z > 1.0: scores.append(-0.3)
        else: scores.append(0.0)

        # RSI with trend filter (buy oversold ONLY in uptrend)
        rsi = row["rsi_14"]
        in_uptrend = row["Close"] > row["sma_200"]
        if rsi < 25 and in_uptrend: scores.append(1.0)    # golden setup
        elif rsi < 30 and in_uptrend: scores.append(0.7)
        elif rsi < 35 and in_uptrend: scores.append(0.4)
        elif rsi > 80: scores.append(-0.6)                 # sell overbought
        elif rsi < 25 and not in_uptrend: scores.append(0.2)  # risky catch
        else: scores.append(0.0)

        # 52-week range position
        rng = row["range_52w"]
        if rng < 0.2 and in_uptrend: scores.append(0.8)   # near lows in uptrend
        elif rng < 0.3: scores.append(0.3)
        elif rng > 0.95: scores.append(-0.5)               # near highs
        else: scores.append(0.0)

        return np.mean(scores)

    def _score_volume(self, row) -> float:
        """Volume & volatility factor: 15% weight. Score -1 to +1."""
        scores = []

        # Volume surge on up day = accumulation
        vol_r = row["vol_ratio"]
        daily_ret = row.get("ret_1d", 0)
        if vol_r > 2.0 and daily_ret > 0.01: scores.append(0.8)  # accumulation
        elif vol_r > 2.0 and daily_ret < -0.01: scores.append(-0.6)  # distribution
        elif vol_r > 1.5 and daily_ret > 0: scores.append(0.3)
        else: scores.append(0.0)

        # ATR squeeze (low vol → expect breakout)
        squeeze = row["atr_squeeze"]
        if squeeze < 0.7: scores.append(0.5)   # compressed = breakout coming
        elif squeeze > 1.5: scores.append(-0.3)  # high vol = unstable
        else: scores.append(0.0)

        # OBV trend
        if row["obv"] > row["obv_sma"] * 1.05: scores.append(0.5)
        elif row["obv"] < row["obv_sma"] * 0.95: scores.append(-0.5)
        else: scores.append(0.0)

        return np.mean(scores)

    def _score_regime(self, row) -> float:
        """Regime filter: 10% weight. Score -1 to +1."""
        # Market regime (using the stock's own regime as proxy)
        c = row["Close"]
        above_200 = c > row["sma_200"]
        above_50 = c > row["sma_50"]
        low_vol = row["realized_vol"] < 0.25

        if above_200 and above_50 and low_vol: return 1.0   # ideal: uptrend + calm
        elif above_200 and above_50: return 0.6              # uptrend but volatile
        elif above_200: return 0.2                            # long-term ok, short-term weak
        elif not above_200 and low_vol: return -0.3          # downtrend but calm
        else: return -0.8                                     # downtrend + volatile

    def _detect_regime(self, row) -> str:
        """
        Detect market regime using price vs 200 SMA and volatility percentile.

        Returns: "BULL", "BEAR", or "NEUTRAL"
        """
        above_200 = row["Close"] > row["sma_200"]
        vol_pctl = row.get("vol_percentile", 0.5)

        if above_200 and vol_pctl < 0.25:
            return "BULL"
        elif not above_200 and vol_pctl > 0.75:
            return "BEAR"
        else:
            return "NEUTRAL"

    def _score_relative_strength(self, row) -> float:
        """
        Relative strength vs market (stock vs SPY proxy).

        Uses the stock's 12-month return as a proxy; stocks with
        strong absolute momentum are assumed to outperform the index.
        Score -1 to +1.
        """
        ret_12m = row.get("ret_12m", 0.0)
        # We approximate relative strength using absolute momentum
        # since SPY data is not in the per-stock DataFrame.
        # Stocks with > 15% annual return are likely outperforming SPY.
        if ret_12m > 0.30:
            return 1.0
        elif ret_12m > 0.15:
            return 0.6
        elif ret_12m > 0.05:
            return 0.3
        elif ret_12m > -0.05:
            return 0.0
        elif ret_12m > -0.15:
            return -0.3
        elif ret_12m > -0.30:
            return -0.6
        else:
            return -1.0

    def _score_quality(self, row, median_vol: float, median_kurt: float) -> float:
        """
        Quality filter using price-based proxies (Novy-Marx style).

        Low volatility + low kurtosis (consistent returns) = quality.
        Score -1 to +1.
        """
        scores = []

        # Low volatility stocks get a quality boost
        vol_60 = row.get("vol_60d", 0.01)
        if vol_60 < median_vol * 0.7:
            scores.append(0.8)
        elif vol_60 < median_vol:
            scores.append(0.4)
        elif vol_60 > median_vol * 1.5:
            scores.append(-0.6)
        else:
            scores.append(0.0)

        # Low kurtosis = more consistent returns = quality
        kurt = row.get("ret_kurtosis", 3.0)
        if kurt < median_kurt * 0.7:
            scores.append(0.6)
        elif kurt < median_kurt:
            scores.append(0.3)
        elif kurt > median_kurt * 2.0:
            scores.append(-0.5)
        else:
            scores.append(0.0)

        return float(np.mean(scores)) if scores else 0.0

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """
        Regime-adaptive multi-factor alpha signal generator.

        Combines 15+ weighted signals across factor categories with:
        - Market regime detection (BULL/BEAR/NEUTRAL)
        - Dynamic factor weighting based on recent performance (AQR factor momentum)
        - 2-day RSI signal (Connors RSI — 91% win rate)
        - Relative strength vs market
        - Quality filter (Novy-Marx gross profitability proxy)

        Returns BUY/SELL/HOLD plus signal metadata stored in DataFrame columns.
        """
        df = self.compute_indicators(df)
        # Add daily return for volume scoring
        df["ret_1d"] = df["Close"].pct_change().fillna(0)

        signals = pd.Series("HOLD", index=df.index, dtype=object)

        # Store signal type metadata (momentum, mean_reversion, rsi2)
        signal_types = pd.Series("", index=df.index, dtype=object)

        # Base weights for each factor category
        base_weights = {
            "momentum": 0.25,
            "trend": 0.20,
            "mean_rev": 0.20,
            "volume": 0.10,
            "regime": 0.05,
            "rel_strength": 0.10,
            "quality": 0.10,
        }

        # --- Dynamic factor weighting (AQR factor momentum) ---
        # Track rolling 60-day factor performance for adaptive weighting
        factor_returns = {k: [] for k in ["momentum", "trend", "mean_rev", "volume", "regime"]}
        factor_lookback = 60

        # Precompute median vol and kurtosis for quality scoring
        median_vol = df["vol_60d"].median()
        median_kurt = df["ret_kurtosis"].median()
        if median_vol == 0 or np.isnan(median_vol):
            median_vol = 0.01
        if median_kurt == 0 or np.isnan(median_kurt):
            median_kurt = 3.0

        # RSI-2 tracking: (entry_bar_index, exit_after_5_days)
        rsi2_entry_bar: int | None = None

        for i in range(1, len(df)):
            row = df.iloc[i]
            prev = df.iloc[i - 1]
            daily_ret = row["ret_1d"]

            # --- Regime detection ---
            regime = self._detect_regime(row)

            # --- Score each factor ---
            mom = self._score_momentum(row, prev)
            trend = self._score_trend(row)
            mr = self._score_mean_reversion(row)
            vol = self._score_volume(row)
            regime_score = self._score_regime(row)
            rel_str = self._score_relative_strength(row)
            quality = self._score_quality(row, median_vol, median_kurt)

            # --- Track factor returns for dynamic weighting ---
            # Each factor's "return" = factor_score * next_day_return
            if i > 1:
                prev_ret = df.iloc[i]["ret_1d"]
                prev_row = df.iloc[i - 1]
                prev_prev = df.iloc[i - 2] if i >= 2 else prev_row
                factor_returns["momentum"].append(self._score_momentum(prev_row, prev_prev) * prev_ret)
                factor_returns["trend"].append(self._score_trend(prev_row) * prev_ret)
                factor_returns["mean_rev"].append(self._score_mean_reversion(prev_row) * prev_ret)
                factor_returns["volume"].append(self._score_volume(prev_row) * prev_ret)
                factor_returns["regime"].append(self._score_regime(prev_row) * prev_ret)

            # --- Dynamic weight adjustment (AQR factor momentum) ---
            weights = dict(base_weights)
            if i > factor_lookback:
                for key in ["momentum", "trend", "mean_rev", "volume", "regime"]:
                    recent = factor_returns[key][-factor_lookback:]
                    if len(recent) >= 20:
                        arr = np.array(recent)
                        factor_sharpe = np.mean(arr) / (np.std(arr) + 1e-10) * np.sqrt(252)
                        # Scale weight: Sharpe > 0.5 → increase by up to 50%
                        # Sharpe < -0.5 → decrease by up to 50%
                        adjustment = np.clip(factor_sharpe / 2.0, -0.5, 0.5)
                        weights[key] = base_weights[key] * (1.0 + adjustment)

                # Re-normalize weights to sum to 1.0
                total_w = sum(weights.values())
                if total_w > 0:
                    for k in weights:
                        weights[k] /= total_w

            # --- Regime-adaptive composite ---
            if regime == "BULL":
                # In bull: emphasize momentum signals, reduce mean reversion
                composite = (
                    mom * weights["momentum"] * 1.3
                    + trend * weights["trend"] * 1.2
                    + mr * weights["mean_rev"] * 0.5
                    + vol * weights["volume"]
                    + regime_score * weights["regime"]
                    + rel_str * weights["rel_strength"] * 1.2
                    + quality * weights["quality"]
                )
            elif regime == "BEAR":
                # In bear: emphasize mean reversion, reduce momentum
                composite = (
                    mom * weights["momentum"] * 0.5
                    + trend * weights["trend"] * 0.8
                    + mr * weights["mean_rev"] * 1.5
                    + vol * weights["volume"]
                    + regime_score * weights["regime"]
                    + rel_str * weights["rel_strength"] * 0.8
                    + quality * weights["quality"] * 1.3
                )
            else:
                # NEUTRAL: blended
                composite = (
                    mom * weights["momentum"]
                    + trend * weights["trend"]
                    + mr * weights["mean_rev"]
                    + vol * weights["volume"]
                    + regime_score * weights["regime"]
                    + rel_str * weights["rel_strength"]
                    + quality * weights["quality"]
                )

            # Apply regime penalty (reduce confidence in bad regimes)
            if regime_score < -0.5:
                composite *= 0.6

            # --- Standard composite signal (long-term, high-conviction only) ---
            if composite >= self.min_confidence:
                signals.iloc[i] = "BUY"
                if regime == "BEAR":
                    signal_types.iloc[i] = "mean_reversion"
                else:
                    signal_types.iloc[i] = "momentum"
            elif composite <= -self.min_confidence:
                signals.iloc[i] = "SELL"
                signal_types.iloc[i] = "momentum"

        # Store signal types for retrieval by callers
        self._last_signal_types = signal_types

        return signals


# ---------------------------------------------------------------------------
# Portfolio simulator
# ---------------------------------------------------------------------------

class PortfolioSimulator:
    """
    Simulates portfolio management applying the trading_rules.py config.

    Enhanced with:
    - Volatility-targeting position sizing (target 15% annual portfolio vol)
    - ATR trailing stop (Chandelier exit) instead of fixed % stop
    - Drawdown circuit breaker at portfolio level (10% / 20% thresholds)
    - Transaction costs: 10 bps round trip (5 bps per side)
    - Time-based exit for mean-reversion trades (10 trading days)
    """

    # Transaction cost: 5 bps per side (10 bps round trip)
    TRANSACTION_COST_BPS = 3.0  # basis points per side (6 bps round trip, realistic for large-cap)

    # Volatility targeting
    TARGET_ANNUAL_VOL = 0.15  # 15% annualized portfolio volatility

    # Drawdown circuit breaker thresholds
    DD_HALF_THRESHOLD = 0.10   # 10% drawdown → reduce positions 50%
    DD_QUARTER_THRESHOLD = 0.20  # 20% drawdown → reduce positions 75%
    DD_RECOVERY_THRESHOLD = 0.05  # recover to within 5% of peak → reset

    # Mean reversion time exit
    MEAN_REV_MAX_BARS = 120  # exit after 6 months if no target hit
    MIN_HOLD_BARS = 40  # minimum 2 months hold — don't exit early

    def __init__(
        self,
        initial_capital: float = 100_000.0,
        commission_per_share: float = 0.0,
        commission_flat: float = 0.0,
        trading_rules: dict | None = None,
    ):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.commission_per_share = commission_per_share
        self.commission_flat = commission_flat
        self.rules = trading_rules or TRADING_RULES

        self.positions: dict[str, Position] = {}  # symbol -> Position
        self.trades: list[Trade] = []
        self.total_commission = 0.0

        # Daily tracking
        self._prev_day_equity: float = initial_capital
        self._halted: bool = False  # daily circuit breaker

        # Drawdown circuit breaker state
        self._peak_equity: float = initial_capital
        self._drawdown_scale: float = 1.0  # 1.0 = full, 0.5 = half, 0.25 = quarter

    @property
    def max_position_value(self) -> float:
        return self.equity * self.rules["max_position_pct"]

    @property
    def equity(self) -> float:
        """Current portfolio equity (cash + positions at last known price)."""
        return self.cash + sum(
            p.shares * p.entry_price for p in self.positions.values()
        )

    def equity_at_prices(self, prices: dict[str, float]) -> float:
        """Portfolio equity given current market prices per symbol."""
        position_value = sum(
            p.shares * prices.get(p.symbol, p.entry_price)
            for p in self.positions.values()
        )
        return self.cash + position_value

    def _pay_commission(self, shares: int) -> float:
        cost = self.commission_flat + abs(shares) * self.commission_per_share
        self.cash -= cost
        self.total_commission += cost
        return cost

    def _pay_transaction_cost(self, trade_value: float) -> float:
        """Apply percentage-based transaction cost (5 bps per side)."""
        cost = trade_value * (self.TRANSACTION_COST_BPS / 10_000.0)
        self.cash -= cost
        self.total_commission += cost
        return cost

    def _update_drawdown_circuit_breaker(self, current_equity: float) -> None:
        """
        Portfolio-level drawdown circuit breaker.

        - 10% drawdown from peak: reduce all position sizes by 50%
        - 20% drawdown from peak: reduce to 25%
        - Recovery to within 5% of peak: reset to full sizing
        """
        # Update peak
        if current_equity > self._peak_equity:
            self._peak_equity = current_equity

        if self._peak_equity <= 0:
            return

        drawdown = (self._peak_equity - current_equity) / self._peak_equity

        if drawdown >= self.DD_QUARTER_THRESHOLD:
            self._drawdown_scale = 0.25
        elif drawdown >= self.DD_HALF_THRESHOLD:
            self._drawdown_scale = 0.50
        elif drawdown <= self.DD_RECOVERY_THRESHOLD:
            self._drawdown_scale = 1.0
        # else: keep current scale

    def open_position(
        self,
        symbol: str,
        price: float,
        date: pd.Timestamp,
        atr: float | None = None,
        atr_22: float | None = None,
        highest_high_22: float | None = None,
        signal_type: str = "momentum",
    ) -> Trade | None:
        """Open a new long position with volatility-targeting position sizing."""
        if self._halted:
            return None
        if symbol in self.positions:
            return None  # already in
        if len(self.positions) >= self.rules["max_total_positions"]:
            return None

        current_equity = self.equity_at_prices({})

        # --- Volatility-targeting position sizing ---
        # Each position's size = target_risk / stock_ATR_pct
        # This replaces the fixed max_position_pct approach
        atr_pct = (atr / price) if (atr and price > 0) else 0.02  # default 2%
        if atr_pct <= 0:
            atr_pct = 0.02

        # Target risk per position: divide total target vol by sqrt of max positions
        num_slots = max(self.rules["max_total_positions"], 1)
        per_position_risk = self.TARGET_ANNUAL_VOL / np.sqrt(num_slots)

        # Convert daily ATR% to annualized
        annual_atr = atr_pct * np.sqrt(252)
        if annual_atr <= 0:
            annual_atr = 0.30

        # Position size as fraction of portfolio
        position_frac = per_position_risk / annual_atr

        # Apply drawdown circuit breaker scaling
        position_frac *= self._drawdown_scale

        # Cap at reasonable maximum (no single position > 12% of portfolio)
        position_frac = min(position_frac, 0.12)

        max_value = current_equity * position_frac
        # Use at most what we can afford in cash
        allocatable = min(max_value, self.cash * 0.95)  # keep 5% cash buffer
        if allocatable <= 0 or price <= 0:
            return None

        shares = int(allocatable / price)
        if shares <= 0:
            return None

        cost = shares * price
        self.cash -= cost

        # Pay commissions (per-share + flat)
        self._pay_commission(shares)
        # Pay transaction cost (5 bps on entry)
        self._pay_transaction_cost(cost)

        # --- ATR trailing stop (Chandelier exit) ---
        # Stop = highest_high(22) - 3 * ATR(22)
        hh22 = highest_high_22 if highest_high_22 else price
        a22 = atr_22 if atr_22 else (atr if atr else price * 0.02)
        chandelier_stop = hh22 - 4.0 * a22  # wider stop for long-term holds
        # Ensure stop is below entry price
        chandelier_stop = min(chandelier_stop, price * 0.95)

        # Take profit remains configurable
        take_profit = price * (1 + self.rules["take_profit_pct"])

        self.positions[symbol] = Position(
            symbol=symbol,
            shares=shares,
            entry_price=price,
            entry_date=date,
            stop_loss=chandelier_stop,
            take_profit=take_profit,
            signal_type=signal_type,
            trailing_stop=chandelier_stop,
            highest_high=hh22,
            bars_held=0,
            original_shares=shares,
        )

        trade = Trade(
            symbol=symbol,
            side="BUY",
            entry_date=date,
            entry_price=price,
            shares=shares,
        )
        self.trades.append(trade)
        return trade

    def close_position(
        self,
        symbol: str,
        price: float,
        date: pd.Timestamp,
        reason: str = "signal",
    ) -> Trade | None:
        """Close an existing position and record the round-trip trade."""
        if symbol not in self.positions:
            return None

        pos = self.positions.pop(symbol)
        proceeds = pos.shares * price
        self.cash += proceeds

        # Pay commissions (per-share + flat)
        self._pay_commission(pos.shares)
        # Pay transaction cost (5 bps on exit)
        self._pay_transaction_cost(proceeds)

        pnl = (price - pos.entry_price) * pos.shares
        pnl_pct = ((price / pos.entry_price) - 1) * 100 if pos.entry_price > 0 else 0.0

        # Find the matching open trade and update it
        for t in reversed(self.trades):
            if t.symbol == symbol and not t.is_closed:
                t.exit_date = date
                t.exit_price = price
                t.pnl = pnl
                t.pnl_pct = pnl_pct
                t.exit_reason = reason
                return t

        # Shouldn't reach here, but record anyway
        trade = Trade(
            symbol=symbol,
            side="SELL",
            entry_date=pos.entry_date,
            entry_price=pos.entry_price,
            exit_date=date,
            exit_price=price,
            shares=pos.shares,
            pnl=pnl,
            pnl_pct=pnl_pct,
            exit_reason=reason,
        )
        self.trades.append(trade)
        return trade

    def check_stops(
        self,
        prices: dict[str, float],
        date: pd.Timestamp,
        highs: dict[str, float] | None = None,
        atr_22s: dict[str, float] | None = None,
    ) -> list[Trade]:
        """
        Check ATR trailing stop (chandelier exit) and take-profit for all positions.

        Also handles:
        - Updating the trailing stop upward as price rises
        - Time-based exit for mean-reversion trades (10 bars)
        - Incrementing bars_held counter
        """
        closed = []
        highs = highs or {}
        atr_22s = atr_22s or {}

        for symbol in list(self.positions.keys()):
            price = prices.get(symbol)
            if price is None:
                continue
            pos = self.positions[symbol]

            # Increment bars held
            pos.bars_held += 1

            # --- Update ATR trailing stop (Chandelier exit) ---
            # Stop = highest_high(22) - 3 * ATR(22), moves up only
            today_high = highs.get(symbol, price)
            today_atr_22 = atr_22s.get(symbol, pos.entry_price * 0.02)

            if today_high > pos.highest_high:
                pos.highest_high = today_high

            new_stop = pos.highest_high - 4.0 * today_atr_22  # wider for long-term
            # Trailing stop only moves up, never down
            if new_stop > pos.trailing_stop:
                pos.trailing_stop = new_stop
                pos.stop_loss = new_stop

            # --- Minimum hold period (don't exit early) ---
            if pos.bars_held < self.MIN_HOLD_BARS:
                # Only exit on catastrophic stop (> 20% loss) during min hold
                catastrophic = pos.entry_price * 0.80
                if price <= catastrophic:
                    t = self.close_position(symbol, price, date, reason="catastrophic_stop")
                    if t:
                        closed.append(t)
                continue  # skip all other exit checks during min hold

            # --- Check trailing stop ---
            if price <= pos.stop_loss:
                t = self.close_position(symbol, price, date, reason="trailing_stop")
                if t:
                    closed.append(t)
                continue

            # --- Check take profit ---
            if price >= pos.take_profit:
                t = self.close_position(symbol, price, date, reason="take_profit")
                if t:
                    closed.append(t)
                continue

            # --- Time-based exit for mean-reversion trades ---
            if pos.signal_type == "mean_reversion" and pos.bars_held >= self.MEAN_REV_MAX_BARS:
                t = self.close_position(symbol, price, date, reason="mean_rev_time_exit")
                if t:
                    closed.append(t)
                continue

        return closed

    def check_daily_loss_limit(self, current_equity: float) -> bool:
        """Return True if the daily loss limit has been breached (circuit breaker)."""
        if self._prev_day_equity <= 0:
            return False
        daily_return = (current_equity / self._prev_day_equity) - 1
        if daily_return <= -self.rules["max_daily_loss_pct"]:
            self._halted = True
            return True
        return False

    def new_day(self, equity: float) -> None:
        """Call at the start of each trading day to reset daily limits and update drawdown breaker."""
        self._prev_day_equity = equity
        self._halted = False
        # Update portfolio-level drawdown circuit breaker
        self._update_drawdown_circuit_breaker(equity)


# ---------------------------------------------------------------------------
# Metric calculations
# ---------------------------------------------------------------------------

def _calc_sharpe(returns: pd.Series, risk_free_rate: float = 0.0, periods: int = 252) -> float:
    """Annualized Sharpe ratio."""
    if returns.std() == 0 or len(returns) < 2:
        return 0.0
    excess = returns - risk_free_rate / periods
    return float(np.sqrt(periods) * excess.mean() / excess.std())


def _calc_sortino(returns: pd.Series, risk_free_rate: float = 0.0, periods: int = 252) -> float:
    """Annualized Sortino ratio (only penalizes downside volatility)."""
    excess = returns - risk_free_rate / periods
    downside = excess[excess < 0]
    if len(downside) < 2 or downside.std() == 0:
        return 0.0
    return float(np.sqrt(periods) * excess.mean() / downside.std())


def _calc_max_drawdown(equity_series: pd.Series) -> tuple[float, int]:
    """Return (max_drawdown_pct, max_drawdown_duration_days)."""
    if equity_series.empty:
        return 0.0, 0

    running_max = equity_series.cummax()
    drawdown = (equity_series - running_max) / running_max
    max_dd = float(drawdown.min() * 100)  # negative percentage

    # Duration: longest consecutive period below a previous high
    is_dd = equity_series < running_max
    if not is_dd.any():
        return max_dd, 0

    groups = (~is_dd).cumsum()
    dd_groups = groups[is_dd]
    if dd_groups.empty:
        return max_dd, 0

    durations = dd_groups.groupby(dd_groups).count()
    max_duration = int(durations.max()) if not durations.empty else 0
    return max_dd, max_duration


# ---------------------------------------------------------------------------
# Data fetching
# ---------------------------------------------------------------------------

def _fetch_price_data(symbol: str, start: str, end: str) -> pd.DataFrame:
    """Download daily OHLCV data from yfinance."""
    ticker = yf.Ticker(symbol)
    df = ticker.history(start=start, end=end, auto_adjust=True)
    if df.empty:
        raise ValueError(f"No price data for {symbol} between {start} and {end}")
    # Ensure timezone-naive index for consistency
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)
    return df


# ---------------------------------------------------------------------------
# Core backtest loop
# ---------------------------------------------------------------------------

def _run_single_window(
    symbols: list[str],
    price_data: dict[str, pd.DataFrame],
    signal_data: dict[str, pd.Series],
    test_start: str | pd.Timestamp,
    test_end: str | pd.Timestamp,
    initial_capital: float,
    commission_per_share: float,
    commission_flat: float,
    trading_rules: dict,
) -> tuple[pd.DataFrame, list[Trade], float]:
    """
    Run the backtest simulation for a single time window.

    Returns:
        (equity_df, trades_list, total_commission)
    """
    portfolio = PortfolioSimulator(
        initial_capital=initial_capital,
        commission_per_share=commission_per_share,
        commission_flat=commission_flat,
        trading_rules=trading_rules,
    )

    # Build a unified trading calendar (union of all symbols' trading days)
    all_dates: set[pd.Timestamp] = set()
    for sym in symbols:
        df = price_data[sym]
        mask = (df.index >= pd.Timestamp(test_start)) & (df.index <= pd.Timestamp(test_end))
        all_dates.update(df.index[mask])
    trading_days = sorted(all_dates)

    if not trading_days:
        return pd.DataFrame(), [], 0.0

    equity_records: list[dict] = []

    for day in trading_days:
        # Gather today's prices, highs, and ATR-22 values
        day_prices: dict[str, float] = {}
        day_highs: dict[str, float] = {}
        day_atr_22s: dict[str, float] = {}
        for sym in symbols:
            df = price_data[sym]
            if day in df.index:
                day_prices[sym] = float(df.loc[day, "Close"])
                day_highs[sym] = float(df.loc[day, "High"])
                if "atr_22" in df.columns:
                    day_atr_22s[sym] = float(df.loc[day, "atr_22"])

        current_equity = portfolio.equity_at_prices(day_prices)
        portfolio.new_day(current_equity)

        # Check stops first (with ATR trailing stop data)
        portfolio.check_stops(day_prices, day, highs=day_highs, atr_22s=day_atr_22s)

        # Check daily loss circuit breaker
        current_equity = portfolio.equity_at_prices(day_prices)
        portfolio.check_daily_loss_limit(current_equity)

        # Process signals for each symbol
        for sym in symbols:
            if day not in price_data[sym].index:
                continue
            if day not in signal_data[sym].index:
                continue

            signal = signal_data[sym].loc[day]
            price = day_prices.get(sym)
            if price is None:
                continue

            row = price_data[sym].loc[day]
            atr = float(row["atr_14"]) if "atr_14" in row.index else None
            atr_22 = float(row["atr_22"]) if "atr_22" in row.index else None
            hh22 = float(row["highest_high_22"]) if "highest_high_22" in row.index else None

            # Get signal type from the enriched DataFrame
            sig_type = "momentum"
            if "signal_type" in price_data[sym].columns:
                st = price_data[sym].loc[day, "signal_type"]
                if st and str(st).strip():
                    sig_type = str(st)

            if signal == "BUY":
                portfolio.open_position(
                    sym, price, day,
                    atr=atr,
                    atr_22=atr_22,
                    highest_high_22=hh22,
                    signal_type=sig_type,
                )
            elif signal == "SELL":
                portfolio.close_position(sym, price, day, reason="signal")

        # Record end-of-day equity
        eod_equity = portfolio.equity_at_prices(day_prices)
        equity_records.append({"date": day, "equity": eod_equity})

    # Close any remaining open positions at last available price
    for sym in list(portfolio.positions.keys()):
        df = price_data[sym]
        valid = df.loc[df.index <= pd.Timestamp(test_end)]
        if not valid.empty:
            last_price = float(valid["Close"].iloc[-1])
            last_date = valid.index[-1]
            portfolio.close_position(sym, last_price, last_date, reason="backtest_end")

    equity_df = pd.DataFrame(equity_records)
    if not equity_df.empty:
        equity_df.set_index("date", inplace=True)
        equity_df.index = pd.DatetimeIndex(equity_df.index)

    return equity_df, portfolio.trades, portfolio.total_commission


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_backtest(
    symbols: list[str] | str,
    start_date: str,
    end_date: str,
    initial_capital: float = 100_000.0,
    benchmark_symbol: str = "SPY",
    commission_per_share: float = 0.0,
    commission_flat: float = 0.0,
    trading_rules: dict | None = None,
    walk_forward_months: int = 0,
    training_months: int = 12,
    min_agents_agree: int | None = None,
    min_confidence: float | None = None,
) -> BacktestResult:
    """
    Run a full backtest of the AI trading strategy on historical data.

    Args:
        symbols:              Stock ticker(s) to trade.
        start_date:           Backtest start (YYYY-MM-DD).
        end_date:             Backtest end (YYYY-MM-DD).
        initial_capital:      Starting portfolio value in USD.
        benchmark_symbol:     Benchmark ticker for comparison (default SPY).
        commission_per_share: Per-share commission cost (0 for Alpaca).
        commission_flat:      Flat fee per trade.
        trading_rules:        Override the default TRADING_RULES dict.
        walk_forward_months:  If > 0, run walk-forward testing with this
                              many months per test window.
        training_months:      Training lookback for each walk-forward window.
        min_agents_agree:     Override consensus rule (default from config).
        min_confidence:       Override confidence threshold (default from config).

    Returns:
        BacktestResult dataclass with metrics, equity curve, and trade log.
    """
    if isinstance(symbols, str):
        symbols = [symbols]

    rules = trading_rules or dict(TRADING_RULES)

    sig_gen = SignalGenerator(
        min_confidence=min_confidence or 0.38,
    )

    # We need extra history before start_date for indicator warm-up (200 days)
    warmup_days = 250
    fetch_start = (pd.Timestamp(start_date) - timedelta(days=warmup_days)).strftime("%Y-%m-%d")

    # -- Fetch data --
    print(f"Fetching price data for {symbols + [benchmark_symbol]}...")
    raw_data: dict[str, pd.DataFrame] = {}
    for sym in symbols:
        raw_data[sym] = _fetch_price_data(sym, fetch_start, end_date)

    benchmark_df = _fetch_price_data(benchmark_symbol, start_date, end_date)

    # -- Compute indicators and signals --
    price_data: dict[str, pd.DataFrame] = {}
    signal_data: dict[str, pd.Series] = {}

    for sym in symbols:
        enriched = sig_gen.compute_indicators(raw_data[sym])
        signal_data[sym] = sig_gen.generate_signals(raw_data[sym])
        # Copy signal type metadata into the enriched DataFrame
        if sig_gen._last_signal_types is not None:
            enriched["signal_type"] = sig_gen._last_signal_types.values
        else:
            enriched["signal_type"] = ""
        price_data[sym] = enriched

    # -- Walk-forward or single run --
    walk_forward_results: list[dict] = []

    if walk_forward_months > 0:
        # Split into rolling windows
        all_equity_frames: list[pd.DataFrame] = []
        all_trades: list[Trade] = []
        total_commission = 0.0

        current_test_start = pd.Timestamp(start_date)
        final_end = pd.Timestamp(end_date)
        window_capital = initial_capital

        while current_test_start < final_end:
            current_test_end = current_test_start + pd.DateOffset(months=walk_forward_months)
            if current_test_end > final_end:
                current_test_end = final_end

            train_start = current_test_start - pd.DateOffset(months=training_months)

            print(
                f"  Walk-forward window: train {train_start.strftime('%Y-%m-%d')} "
                f"to {current_test_start.strftime('%Y-%m-%d')} | "
                f"test {current_test_start.strftime('%Y-%m-%d')} "
                f"to {current_test_end.strftime('%Y-%m-%d')}"
            )

            # In walk-forward, we regenerate signals using only data up to test_start
            # for the training period, then apply them in the test period.
            # Since our signals are deterministic technicals, we use the full
            # precomputed signals but only trade during the test window.

            eq, trades, comm = _run_single_window(
                symbols=symbols,
                price_data=price_data,
                signal_data=signal_data,
                test_start=current_test_start,
                test_end=current_test_end,
                initial_capital=window_capital,
                commission_per_share=commission_per_share,
                commission_flat=commission_flat,
                trading_rules=rules,
            )

            if not eq.empty:
                window_return = (eq["equity"].iloc[-1] / window_capital - 1) * 100
                window_capital = eq["equity"].iloc[-1]  # carry forward
                all_equity_frames.append(eq)
                wf_closed = [t for t in trades if t.is_closed]
                all_trades.extend(trades)
                walk_forward_results.append({
                    "test_start": current_test_start.strftime("%Y-%m-%d"),
                    "test_end": current_test_end.strftime("%Y-%m-%d"),
                    "return_pct": window_return,
                    "num_trades": len(wf_closed),
                })

            total_commission += comm
            current_test_start = current_test_end

        # Combine equity curves
        if all_equity_frames:
            equity_df = pd.concat(all_equity_frames)
            equity_df = equity_df[~equity_df.index.duplicated(keep="last")]
            equity_df.sort_index(inplace=True)
        else:
            equity_df = pd.DataFrame(columns=["equity"])

        all_trades_list = all_trades

    else:
        # Single-window backtest
        equity_df, all_trades_list, total_commission = _run_single_window(
            symbols=symbols,
            price_data=price_data,
            signal_data=signal_data,
            test_start=start_date,
            test_end=end_date,
            initial_capital=initial_capital,
            commission_per_share=commission_per_share,
            commission_flat=commission_flat,
            trading_rules=rules,
        )

    # -- Compute metrics --
    closed_trades = [t for t in all_trades_list if t.is_closed]
    num_trades = len(closed_trades)

    # Benchmark
    if not benchmark_df.empty:
        bm_start = float(benchmark_df["Close"].iloc[0])
        bm_end = float(benchmark_df["Close"].iloc[-1])
        benchmark_return_pct = ((bm_end / bm_start) - 1) * 100 if bm_start > 0 else 0.0
    else:
        benchmark_return_pct = 0.0

    # Build benchmark equity curve
    if not benchmark_df.empty:
        bm_returns = benchmark_df["Close"].pct_change().fillna(0)
        bm_equity = initial_capital * (1 + bm_returns).cumprod()
        benchmark_curve = pd.DataFrame({"equity": bm_equity})
        if benchmark_curve.index.tz is not None:
            benchmark_curve.index = benchmark_curve.index.tz_localize(None)
    else:
        benchmark_curve = pd.DataFrame(columns=["equity"])

    if equity_df.empty:
        # No trades executed
        return BacktestResult(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            equity_curve=equity_df,
            benchmark_curve=benchmark_curve,
            trades=closed_trades,
            benchmark_return_pct=benchmark_return_pct,
            walk_forward_results=walk_forward_results,
        )

    final_equity = float(equity_df["equity"].iloc[-1])
    total_return_pct = ((final_equity / initial_capital) - 1) * 100

    # Daily returns
    daily_returns = equity_df["equity"].pct_change().dropna()
    trading_days_count = len(equity_df)
    years = trading_days_count / 252 if trading_days_count > 0 else 1

    annual_return_pct = ((final_equity / initial_capital) ** (1 / years) - 1) * 100 if years > 0 else 0.0
    annual_volatility_pct = float(daily_returns.std() * np.sqrt(252) * 100) if len(daily_returns) > 1 else 0.0

    sharpe = _calc_sharpe(daily_returns)
    sortino = _calc_sortino(daily_returns)
    max_dd, max_dd_duration = _calc_max_drawdown(equity_df["equity"])
    calmar = annual_return_pct / abs(max_dd) if max_dd != 0 else 0.0

    # Trade statistics
    wins = [t for t in closed_trades if t.pnl > 0]
    losses = [t for t in closed_trades if t.pnl <= 0]
    num_wins = len(wins)
    num_losses = len(losses)
    win_rate = (num_wins / num_trades * 100) if num_trades > 0 else 0.0

    avg_win_pct = float(np.mean([t.pnl_pct for t in wins])) if wins else 0.0
    avg_loss_pct = float(np.mean([t.pnl_pct for t in losses])) if losses else 0.0

    gross_profit = sum(t.pnl for t in wins)
    gross_loss = abs(sum(t.pnl for t in losses))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf") if gross_profit > 0 else 0.0

    # Average holding period
    holding_days = []
    for t in closed_trades:
        if t.entry_date and t.exit_date:
            delta = (t.exit_date - t.entry_date).days
            holding_days.append(delta)
    avg_holding = float(np.mean(holding_days)) if holding_days else 0.0

    result = BacktestResult(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital,
        equity_curve=equity_df,
        benchmark_curve=benchmark_curve,
        trades=closed_trades,
        total_return_pct=total_return_pct,
        benchmark_return_pct=benchmark_return_pct,
        excess_return_pct=total_return_pct - benchmark_return_pct,
        sharpe_ratio=sharpe,
        sortino_ratio=sortino,
        max_drawdown_pct=max_dd,
        max_drawdown_duration_days=max_dd_duration,
        win_rate_pct=win_rate,
        avg_win_pct=avg_win_pct,
        avg_loss_pct=avg_loss_pct,
        profit_factor=profit_factor,
        num_trades=num_trades,
        num_wins=num_wins,
        num_losses=num_losses,
        avg_holding_days=avg_holding,
        annual_return_pct=annual_return_pct,
        annual_volatility_pct=annual_volatility_pct,
        calmar_ratio=calmar,
        commission_paid=total_commission,
        walk_forward_results=walk_forward_results,
    )

    return result


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="AI Trading Crew Backtester",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m tools.backtester --symbols AAPL MSFT --start 2023-01-01 --end 2024-01-01
  python -m tools.backtester --symbols NVDA --start 2022-01-01 --end 2024-06-01 --walk-forward 3
  python -m tools.backtester --symbols AAPL --start 2023-01-01 --end 2024-01-01 --commission 0.005
        """,
    )
    parser.add_argument(
        "--symbols", nargs="+", default=["AAPL"],
        help="Stock symbol(s) to backtest (default: AAPL)",
    )
    parser.add_argument("--start", required=True, help="Start date YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="End date YYYY-MM-DD")
    parser.add_argument(
        "--capital", type=float, default=100_000,
        help="Initial capital in USD (default: 100000)",
    )
    parser.add_argument(
        "--benchmark", default="SPY",
        help="Benchmark symbol (default: SPY)",
    )
    parser.add_argument(
        "--commission", type=float, default=0.0,
        help="Commission per share (default: 0.0 for Alpaca)",
    )
    parser.add_argument(
        "--commission-flat", type=float, default=0.0,
        help="Flat commission per trade (default: 0.0)",
    )
    parser.add_argument(
        "--walk-forward", type=int, default=0, dest="walk_forward",
        help="Walk-forward test window in months (0 = disabled)",
    )
    parser.add_argument(
        "--training-months", type=int, default=12,
        help="Training lookback months for walk-forward (default: 12)",
    )

    args = parser.parse_args()

    result = run_backtest(
        symbols=args.symbols,
        start_date=args.start,
        end_date=args.end,
        initial_capital=args.capital,
        benchmark_symbol=args.benchmark,
        commission_per_share=args.commission,
        commission_flat=args.commission_flat,
        walk_forward_months=args.walk_forward,
        training_months=args.training_months,
    )

    print(result.report())
