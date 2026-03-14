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
    Generates buy/sell/hold signals using a composite of the technical
    indicators the AI agents analyze. This is a deterministic proxy for
    the multi-agent consensus so backtests are reproducible.

    The composite considers:
      - Trend (SMA 50/200 golden/death cross, price vs SMA 50)
      - Momentum (RSI 14, MACD crossover)
      - Volume confirmation (volume spike on signal)
      - Mean reversion (Bollinger Band extremes)

    Each sub-signal votes BUY (+1), SELL (-1), or HOLD (0). The final
    signal requires >= min_agents_agree votes in one direction and
    overall confidence >= min_confidence.
    """

    def __init__(
        self,
        min_agents_agree: int = 3,
        min_confidence: float = 0.7,
    ):
        self.min_agents_agree = min_agents_agree
        self.min_confidence = min_confidence

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add all technical indicator columns to a price DataFrame."""
        df = df.copy()
        close = df["Close"]
        volume = df["Volume"]

        # -- Trend --
        df["sma_50"] = close.rolling(50, min_periods=1).mean()
        df["sma_200"] = close.rolling(200, min_periods=1).mean()

        # -- MACD --
        ema_12 = close.ewm(span=12, adjust=False).mean()
        ema_26 = close.ewm(span=26, adjust=False).mean()
        df["macd_line"] = ema_12 - ema_26
        df["macd_signal"] = df["macd_line"].ewm(span=9, adjust=False).mean()
        df["macd_hist"] = df["macd_line"] - df["macd_signal"]

        # -- RSI 14 --
        delta = close.diff()
        gain = delta.where(delta > 0, 0.0).rolling(14, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0.0)).rolling(14, min_periods=1).mean()
        rs = gain / loss.replace(0, np.nan)
        df["rsi_14"] = 100 - (100 / (1 + rs))
        df["rsi_14"] = df["rsi_14"].fillna(50)

        # -- Bollinger Bands (20, 2) --
        sma_20 = close.rolling(20, min_periods=1).mean()
        std_20 = close.rolling(20, min_periods=1).std().fillna(0)
        df["bb_upper"] = sma_20 + 2 * std_20
        df["bb_lower"] = sma_20 - 2 * std_20

        # -- Volume spike --
        avg_vol_20 = volume.rolling(20, min_periods=1).mean()
        df["vol_spike"] = volume / avg_vol_20.replace(0, np.nan)
        df["vol_spike"] = df["vol_spike"].fillna(1.0)

        # -- ATR 14 (for stop/take-profit calibration) --
        high = df["High"]
        low = df["Low"]
        prev_close = close.shift(1).fillna(close)
        tr = pd.concat([
            (high - low),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ], axis=1).max(axis=1)
        df["atr_14"] = tr.rolling(14, min_periods=1).mean()

        return df

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """
        Return a Series of SignalType for each trading day.

        The composite scoring works as follows (7 sub-signals, mimicking
        the 8 agent teams minus the execution team which does not vote):

        1. Trend Follower (Marcus):  golden cross / death cross
        2. Momentum (Sophia):        RSI oversold/overbought
        3. MACD (Quant team):        MACD histogram crossover
        4. Mean Reversion (Ivan):    Bollinger Band extremes
        5. Volume (Raj):             volume confirmation
        6. Price vs SMA50:           above/below trend
        7. Macro trend (SMA200):     long-term direction

        A signal fires when enough sub-signals agree and confidence is met.
        """
        df = self.compute_indicators(df)
        signals = pd.Series("HOLD", index=df.index, dtype=object)

        for i in range(1, len(df)):
            row = df.iloc[i]
            prev = df.iloc[i - 1]

            votes = []

            # 1. Golden / Death cross
            if row["sma_50"] > row["sma_200"]:
                votes.append(1)
            elif row["sma_50"] < row["sma_200"]:
                votes.append(-1)
            else:
                votes.append(0)

            # 2. RSI
            if row["rsi_14"] < 30:
                votes.append(1)   # oversold -> buy
            elif row["rsi_14"] > 70:
                votes.append(-1)  # overbought -> sell
            else:
                votes.append(0)

            # 3. MACD histogram crossover
            if row["macd_hist"] > 0 and prev["macd_hist"] <= 0:
                votes.append(1)
            elif row["macd_hist"] < 0 and prev["macd_hist"] >= 0:
                votes.append(-1)
            else:
                votes.append(0)

            # 4. Bollinger Band extremes (mean reversion)
            close_price = row["Close"]
            if close_price <= row["bb_lower"]:
                votes.append(1)   # oversold bounce
            elif close_price >= row["bb_upper"]:
                votes.append(-1)  # overextended
            else:
                votes.append(0)

            # 5. Volume confirmation (amplifies existing signals only)
            vol_confirmed = row["vol_spike"] > 1.5
            if vol_confirmed:
                # Add a vote in the direction of recent price change
                daily_return = (close_price / prev["Close"]) - 1 if prev["Close"] > 0 else 0
                if daily_return > 0.005:
                    votes.append(1)
                elif daily_return < -0.005:
                    votes.append(-1)
                else:
                    votes.append(0)
            else:
                votes.append(0)

            # 6. Price vs SMA 50 (short-term trend)
            if close_price > row["sma_50"] * 1.01:
                votes.append(1)
            elif close_price < row["sma_50"] * 0.99:
                votes.append(-1)
            else:
                votes.append(0)

            # 7. Price vs SMA 200 (long-term trend)
            if close_price > row["sma_200"]:
                votes.append(1)
            elif close_price < row["sma_200"]:
                votes.append(-1)
            else:
                votes.append(0)

            # -- Tally votes --
            buy_votes = sum(1 for v in votes if v > 0)
            sell_votes = sum(1 for v in votes if v < 0)
            total_signals = len(votes)

            if buy_votes >= self.min_agents_agree:
                confidence = buy_votes / total_signals
                if confidence >= self.min_confidence:
                    signals.iloc[i] = "BUY"
            elif sell_votes >= self.min_agents_agree:
                confidence = sell_votes / total_signals
                if confidence >= self.min_confidence:
                    signals.iloc[i] = "SELL"
            # else remains HOLD

        return signals


# ---------------------------------------------------------------------------
# Portfolio simulator
# ---------------------------------------------------------------------------

class PortfolioSimulator:
    """
    Simulates portfolio management applying the trading_rules.py config.
    Handles position sizing, stop-losses, take-profits, and daily loss limits.
    """

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
        self._halted: bool = False  # circuit breaker

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

    def open_position(
        self,
        symbol: str,
        price: float,
        date: pd.Timestamp,
        atr: float | None = None,
    ) -> Trade | None:
        """Open a new long position respecting risk rules."""
        if self._halted:
            return None
        if symbol in self.positions:
            return None  # already in
        if len(self.positions) >= self.rules["max_total_positions"]:
            return None

        # Position sizing: max_position_pct of current equity
        max_value = self.equity_at_prices({}) * self.rules["max_position_pct"]
        # Use at most what we can afford in cash
        allocatable = min(max_value, self.cash * 0.95)  # keep 5% cash buffer
        if allocatable <= 0 or price <= 0:
            return None

        shares = int(allocatable / price)
        if shares <= 0:
            return None

        cost = shares * price
        self.cash -= cost
        self._pay_commission(shares)

        stop_loss = price * (1 - self.rules["stop_loss_pct"])
        take_profit = price * (1 + self.rules["take_profit_pct"])

        self.positions[symbol] = Position(
            symbol=symbol,
            shares=shares,
            entry_price=price,
            entry_date=date,
            stop_loss=stop_loss,
            take_profit=take_profit,
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
        self._pay_commission(pos.shares)

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

    def check_stops(self, prices: dict[str, float], date: pd.Timestamp) -> list[Trade]:
        """Check stop-loss and take-profit levels for all positions."""
        closed = []
        for symbol in list(self.positions.keys()):
            price = prices.get(symbol)
            if price is None:
                continue
            pos = self.positions[symbol]
            if price <= pos.stop_loss:
                t = self.close_position(symbol, price, date, reason="stop_loss")
                if t:
                    closed.append(t)
            elif price >= pos.take_profit:
                t = self.close_position(symbol, price, date, reason="take_profit")
                if t:
                    closed.append(t)
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
        """Call at the start of each trading day to reset daily limits."""
        self._prev_day_equity = equity
        self._halted = False


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
        # Gather today's prices
        day_prices: dict[str, float] = {}
        for sym in symbols:
            df = price_data[sym]
            if day in df.index:
                day_prices[sym] = float(df.loc[day, "Close"])

        current_equity = portfolio.equity_at_prices(day_prices)
        portfolio.new_day(current_equity)

        # Check stops first
        portfolio.check_stops(day_prices, day)

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

            if signal == "BUY":
                portfolio.open_position(sym, price, day, atr=atr)
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
        min_agents_agree=min_agents_agree or rules.get("min_agents_agree", 3),
        min_confidence=min_confidence or rules.get("min_confidence", 0.7),
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
        price_data[sym] = enriched
        signal_data[sym] = sig_gen.generate_signals(enriched)

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
