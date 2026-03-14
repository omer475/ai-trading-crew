"""
Automated trade execution gate and portfolio risk management.

Every trade proposal flows through this module before reaching the broker.
It enforces position sizing, stop-loss management, pre-trade risk checks,
portfolio-level risk metrics, and circuit breakers.
"""

import math
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

import numpy as np
import pandas as pd

from config.trading_rules import TRADING_RULES
from tools.broker import get_account_info, get_positions, place_order, close_position
from tools.market_data import get_price_history, get_stock_price

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants derived from the canonical trading rules
# ---------------------------------------------------------------------------
MAX_POSITION_PCT = TRADING_RULES["max_position_pct"]
MAX_SECTOR_PCT = TRADING_RULES["max_sector_pct"]
MAX_TOTAL_POSITIONS = TRADING_RULES["max_total_positions"]
MAX_DAILY_LOSS_PCT = TRADING_RULES["max_daily_loss_pct"]
STOP_LOSS_PCT = TRADING_RULES["stop_loss_pct"]
TAKE_PROFIT_PCT = TRADING_RULES["take_profit_pct"]
HUMAN_APPROVAL_ABOVE_PCT = TRADING_RULES["human_approval_above_pct"]

# Additional risk parameters (extend trading_rules.py if you want to
# centralise them; kept here to avoid touching shared config).
HALF_KELLY_FRACTION = 0.5
DEFAULT_RISK_PER_TRADE_PCT = 0.01          # 1 % fixed-fractional default
ATR_PERIOD = 14
ATR_RISK_MULTIPLIER = 2.0                  # stop distance = 2 * ATR
TRAILING_STOP_ATR_MULT = 3.0
BREAKEVEN_TRIGGER_PCT = 0.03               # move stop to entry after 3 % gain
TIME_STOP_DAYS = 15                        # exit if flat after 15 calendar days
DRAWDOWN_REDUCE_THRESHOLD = 0.05           # reduce sizing at 5 % drawdown
DRAWDOWN_HALT_THRESHOLD = 0.10             # halt trading at 10 % drawdown
MAX_CORRELATION_ALLOWED = 0.70             # reject if correlation > 0.70
VAR_CONFIDENCE = 0.95                      # 95 % VaR
VAR_LOOKBACK_DAYS = 252


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------
class StopType(Enum):
    INITIAL = "initial"
    TRAILING = "trailing"
    BREAKEVEN = "breakeven"
    TIME = "time"


@dataclass
class StopLoss:
    """Tracks the current stop-loss state for a single position."""
    symbol: str
    entry_price: float
    entry_date: datetime
    stop_price: float
    stop_type: StopType = StopType.INITIAL
    highest_price: float = 0.0              # watermark for trailing stop

    def __post_init__(self):
        if self.highest_price == 0.0:
            self.highest_price = self.entry_price


@dataclass
class RiskCheckResult:
    """Outcome of the pre-trade risk gate."""
    passed: bool
    checks: dict[str, bool] = field(default_factory=dict)
    reasons: list[str] = field(default_factory=list)

    def __str__(self):
        status = "PASSED" if self.passed else "BLOCKED"
        detail = "; ".join(self.reasons) if self.reasons else "all clear"
        return f"RiskCheck {status}: {detail}"


@dataclass
class TradeProposal:
    """A candidate trade that must pass the risk gate."""
    symbol: str
    side: str                               # "buy" or "sell"
    confidence: float                       # 0-1
    win_rate: float = 0.55                  # historical or estimated
    avg_win_loss_ratio: float = 1.5         # reward / risk
    order_type: str = "limit"
    limit_price: Optional[float] = None
    sector: Optional[str] = None


# ---------------------------------------------------------------------------
# 1. Position Sizing
# ---------------------------------------------------------------------------
class PositionSizer:
    """Calculate position sizes using multiple methodologies."""

    @staticmethod
    def kelly_criterion(win_rate: float, avg_win_loss_ratio: float,
                        equity: float, current_price: float,
                        half_kelly: bool = True) -> int:
        """
        Kelly Criterion sizing.

        f* = W - (1-W)/R
        where W = win probability, R = avg_win / avg_loss.

        Returns number of shares (floored to int).
        """
        if win_rate <= 0 or avg_win_loss_ratio <= 0:
            return 0

        kelly_frac = win_rate - (1.0 - win_rate) / avg_win_loss_ratio
        if kelly_frac <= 0:
            return 0

        if half_kelly:
            kelly_frac *= HALF_KELLY_FRACTION

        # Cap at the per-position max from trading rules
        kelly_frac = min(kelly_frac, MAX_POSITION_PCT)

        dollar_amount = equity * kelly_frac
        shares = int(dollar_amount / current_price)
        return max(shares, 0)

    @staticmethod
    def fixed_fractional(equity: float, current_price: float,
                         stop_price: float,
                         risk_pct: float = DEFAULT_RISK_PER_TRADE_PCT) -> int:
        """
        Fixed-fractional sizing: risk a fixed % of equity per trade.

        shares = (equity * risk_pct) / (entry - stop)
        """
        risk_per_share = abs(current_price - stop_price)
        if risk_per_share <= 0:
            return 0

        dollar_risk = equity * risk_pct
        shares = int(dollar_risk / risk_per_share)

        # Enforce max position size
        max_shares = int((equity * MAX_POSITION_PCT) / current_price)
        return min(shares, max_shares)

    @staticmethod
    def volatility_based(equity: float, current_price: float,
                         atr: float,
                         risk_pct: float = DEFAULT_RISK_PER_TRADE_PCT) -> int:
        """
        ATR-adjusted sizing: larger ATR -> smaller position.

        shares = (equity * risk_pct) / (ATR * multiplier)
        """
        risk_distance = atr * ATR_RISK_MULTIPLIER
        if risk_distance <= 0:
            return 0

        dollar_risk = equity * risk_pct
        shares = int(dollar_risk / risk_distance)

        max_shares = int((equity * MAX_POSITION_PCT) / current_price)
        return min(shares, max_shares)

    @staticmethod
    def adjust_for_concentration(shares: int, current_price: float,
                                 equity: float,
                                 existing_sector_exposure: float) -> int:
        """
        Reduce position size if sector concentration would exceed limits.

        ``existing_sector_exposure`` is the current dollar value already
        allocated to this position's sector.
        """
        proposed_value = shares * current_price
        max_sector_value = equity * MAX_SECTOR_PCT
        room = max_sector_value - existing_sector_exposure

        if room <= 0:
            return 0

        if proposed_value > room:
            shares = int(room / current_price)

        return max(shares, 0)

    @classmethod
    def recommend(cls, proposal: TradeProposal, equity: float,
                  current_price: float, atr: float,
                  stop_price: float,
                  existing_sector_exposure: float = 0.0) -> dict:
        """
        Run all sizing methods and return the recommended (conservative)
        size along with a breakdown.
        """
        kelly = cls.kelly_criterion(
            proposal.win_rate, proposal.avg_win_loss_ratio,
            equity, current_price,
        )
        fixed = cls.fixed_fractional(equity, current_price, stop_price)
        vol = cls.volatility_based(equity, current_price, atr)

        # Take the minimum across all three methods (conservative)
        raw = min(kelly, fixed, vol)
        adjusted = cls.adjust_for_concentration(
            raw, current_price, equity, existing_sector_exposure,
        )

        return {
            "kelly_shares": kelly,
            "fixed_fractional_shares": fixed,
            "volatility_shares": vol,
            "raw_recommendation": raw,
            "adjusted_shares": adjusted,
            "position_value": adjusted * current_price,
            "position_pct": (adjusted * current_price) / equity if equity else 0,
        }


# ---------------------------------------------------------------------------
# 2. Stop-Loss Management
# ---------------------------------------------------------------------------
class StopLossManager:
    """Create and update stop-loss levels for open positions."""

    def __init__(self):
        # symbol -> StopLoss
        self._stops: dict[str, StopLoss] = {}

    @property
    def stops(self) -> dict[str, StopLoss]:
        return dict(self._stops)

    # -- creation -----------------------------------------------------------

    def create_atr_stop(self, symbol: str, entry_price: float,
                        atr: float,
                        multiplier: float = ATR_RISK_MULTIPLIER) -> StopLoss:
        """Initial stop = entry - (ATR * multiplier) for longs."""
        stop_price = entry_price - atr * multiplier
        sl = StopLoss(
            symbol=symbol,
            entry_price=entry_price,
            entry_date=datetime.utcnow(),
            stop_price=round(stop_price, 2),
        )
        self._stops[symbol] = sl
        logger.info("ATR stop created for %s at %.2f (entry=%.2f, ATR=%.2f)",
                     symbol, stop_price, entry_price, atr)
        return sl

    def create_fixed_pct_stop(self, symbol: str, entry_price: float,
                              pct: float = STOP_LOSS_PCT) -> StopLoss:
        """Initial stop = entry * (1 - pct)."""
        stop_price = entry_price * (1.0 - pct)
        sl = StopLoss(
            symbol=symbol,
            entry_price=entry_price,
            entry_date=datetime.utcnow(),
            stop_price=round(stop_price, 2),
        )
        self._stops[symbol] = sl
        logger.info("Fixed-pct stop created for %s at %.2f (%.1f%%)",
                     symbol, stop_price, pct * 100)
        return sl

    # -- updates ------------------------------------------------------------

    def update_trailing(self, symbol: str, current_price: float,
                        atr: float,
                        multiplier: float = TRAILING_STOP_ATR_MULT) -> Optional[StopLoss]:
        """
        Trail the stop upward with price. Never moves down.

        trailing_stop = highest_price - ATR * multiplier
        """
        sl = self._stops.get(symbol)
        if sl is None:
            return None

        if current_price > sl.highest_price:
            sl.highest_price = current_price

        new_stop = sl.highest_price - atr * multiplier
        new_stop = round(new_stop, 2)

        if new_stop > sl.stop_price:
            sl.stop_price = new_stop
            sl.stop_type = StopType.TRAILING
            logger.info("Trailing stop for %s raised to %.2f (high=%.2f)",
                         symbol, new_stop, sl.highest_price)

        return sl

    def check_breakeven(self, symbol: str, current_price: float,
                        trigger_pct: float = BREAKEVEN_TRIGGER_PCT) -> Optional[StopLoss]:
        """Move stop to entry price once the position is up *trigger_pct*."""
        sl = self._stops.get(symbol)
        if sl is None:
            return None

        gain_pct = (current_price - sl.entry_price) / sl.entry_price
        if gain_pct >= trigger_pct and sl.stop_price < sl.entry_price:
            sl.stop_price = sl.entry_price
            sl.stop_type = StopType.BREAKEVEN
            logger.info("Breakeven stop activated for %s at %.2f",
                         symbol, sl.entry_price)

        return sl

    def check_time_stop(self, symbol: str,
                        current_price: float,
                        max_days: int = TIME_STOP_DAYS) -> bool:
        """
        Return True if the position should be closed because it has been
        open for *max_days* without any profit.
        """
        sl = self._stops.get(symbol)
        if sl is None:
            return False

        elapsed = (datetime.utcnow() - sl.entry_date).days
        if elapsed >= max_days and current_price <= sl.entry_price:
            logger.warning("Time stop triggered for %s after %d days",
                            symbol, elapsed)
            return True
        return False

    def is_stopped_out(self, symbol: str, current_price: float) -> bool:
        """Return True if current_price has hit or breached the stop."""
        sl = self._stops.get(symbol)
        if sl is None:
            return False
        return current_price <= sl.stop_price

    def remove(self, symbol: str) -> None:
        self._stops.pop(symbol, None)

    def update_all(self, positions: list[dict], atr_cache: dict[str, float]) -> list[str]:
        """
        Run trailing-stop, breakeven, time-stop, and stop-hit checks for
        every tracked position.  Returns list of symbols that should be closed.
        """
        to_close: list[str] = []
        for pos in positions:
            sym = pos["symbol"]
            price = pos["current_price"]
            atr = atr_cache.get(sym, 0.0)

            if atr > 0:
                self.update_trailing(sym, price, atr)
            self.check_breakeven(sym, price)

            if self.is_stopped_out(sym, price):
                logger.warning("STOP HIT for %s at %.2f", sym, price)
                to_close.append(sym)
            elif self.check_time_stop(sym, price):
                to_close.append(sym)

        return to_close


# ---------------------------------------------------------------------------
# 3. Pre-Trade Risk Checks
# ---------------------------------------------------------------------------
class RiskGate:
    """
    Every trade proposal must pass **all** checks here before execution.
    """

    def __init__(self):
        self._trading_halted = False
        self._sizing_reduction: float = 1.0   # 1.0 = full size, 0.5 = half, etc.

    @property
    def trading_halted(self) -> bool:
        return self._trading_halted

    @property
    def sizing_reduction(self) -> float:
        return self._sizing_reduction

    def halt_trading(self, reason: str = "") -> None:
        self._trading_halted = True
        logger.critical("TRADING HALTED: %s", reason)

    def resume_trading(self) -> None:
        self._trading_halted = False
        self._sizing_reduction = 1.0
        logger.info("Trading resumed, sizing reset to 100%%")

    # -- individual checks --------------------------------------------------

    @staticmethod
    def _check_daily_loss(account: dict) -> tuple[bool, str]:
        daily_pnl = account["daily_pnl"]
        equity = account["equity"]
        if equity <= 0:
            return False, "equity is zero or negative"

        daily_loss_pct = daily_pnl / equity  # negative when losing
        if daily_loss_pct <= -MAX_DAILY_LOSS_PCT:
            return False, (
                f"daily loss {daily_loss_pct:.2%} exceeds limit "
                f"{-MAX_DAILY_LOSS_PCT:.2%}"
            )
        return True, ""

    @staticmethod
    def _check_position_size(shares: int, price: float,
                             equity: float) -> tuple[bool, str]:
        value = shares * price
        pct = value / equity if equity else 1.0
        if pct > MAX_POSITION_PCT:
            return False, (
                f"position {pct:.2%} of equity exceeds limit {MAX_POSITION_PCT:.2%}"
            )
        return True, ""

    @staticmethod
    def _check_sector_concentration(sector: Optional[str],
                                    positions: list[dict],
                                    proposed_value: float,
                                    equity: float) -> tuple[bool, str]:
        if sector is None:
            return True, ""

        sector_value = sum(
            p["market_value"] for p in positions
            if _position_sector(p["symbol"]) == sector
        )
        total = sector_value + proposed_value
        pct = total / equity if equity else 1.0
        if pct > MAX_SECTOR_PCT:
            return False, (
                f"sector '{sector}' would be {pct:.2%} of equity "
                f"(limit {MAX_SECTOR_PCT:.2%})"
            )
        return True, ""

    @staticmethod
    def _check_total_exposure(positions: list[dict],
                              proposed_value: float,
                              equity: float) -> tuple[bool, str]:
        current_exposure = sum(abs(p["market_value"]) for p in positions)
        total = current_exposure + proposed_value
        # Allow up to 100 % net exposure (no leverage)
        if total > equity:
            return False, (
                f"total exposure ${total:,.0f} would exceed "
                f"equity ${equity:,.0f}"
            )
        return True, ""

    @staticmethod
    def _check_max_positions(positions: list[dict]) -> tuple[bool, str]:
        if len(positions) >= MAX_TOTAL_POSITIONS:
            return False, (
                f"already at max open positions ({MAX_TOTAL_POSITIONS})"
            )
        return True, ""

    @staticmethod
    def _check_correlation(symbol: str, positions: list[dict],
                           threshold: float = MAX_CORRELATION_ALLOWED) -> tuple[bool, str]:
        """
        Reject the trade if the proposed symbol is too correlated with
        existing holdings.  Uses 90-day daily returns.
        """
        if not positions:
            return True, ""

        existing_symbols = [p["symbol"] for p in positions]
        # Limit to first 10 to keep API calls manageable
        symbols_to_check = existing_symbols[:10]

        try:
            returns = _get_returns_matrix([symbol] + symbols_to_check, days=90)
        except Exception as exc:
            logger.warning("Correlation check failed: %s (allowing trade)", exc)
            return True, ""

        if returns.empty or symbol not in returns.columns:
            return True, ""

        for existing_sym in symbols_to_check:
            if existing_sym not in returns.columns:
                continue
            corr = returns[symbol].corr(returns[existing_sym])
            if not math.isnan(corr) and abs(corr) > threshold:
                return False, (
                    f"{symbol} corr {corr:.2f} with {existing_sym} "
                    f"exceeds {threshold:.2f}"
                )

        return True, ""

    # -- main gate ----------------------------------------------------------

    def evaluate(self, proposal: TradeProposal, shares: int,
                 current_price: float) -> RiskCheckResult:
        """
        Run every pre-trade check. Returns a ``RiskCheckResult`` whose
        ``.passed`` flag is True only when **all** checks pass.
        """
        result = RiskCheckResult(passed=True)

        # Circuit breaker: immediate halt
        if self._trading_halted:
            result.passed = False
            result.reasons.append("trading is halted by circuit breaker")
            return result

        account = get_account_info()
        positions = get_positions()
        equity = account["equity"]
        proposed_value = shares * current_price

        checks = [
            ("daily_loss", self._check_daily_loss(account)),
            ("position_size", self._check_position_size(shares, current_price, equity)),
            ("sector_concentration", self._check_sector_concentration(
                proposal.sector, positions, proposed_value, equity)),
            ("total_exposure", self._check_total_exposure(positions, proposed_value, equity)),
            ("max_positions", self._check_max_positions(positions)),
            ("correlation", self._check_correlation(proposal.symbol, positions)),
        ]

        for name, (passed, reason) in checks:
            result.checks[name] = passed
            if not passed:
                result.passed = False
                result.reasons.append(reason)

        # Apply sizing reduction from drawdown circuit breaker
        if self._sizing_reduction < 1.0:
            result.reasons.append(
                f"sizing reduced to {self._sizing_reduction:.0%} due to drawdown"
            )

        logger.info("Risk gate for %s %d shares of %s: %s",
                     proposal.side, shares, proposal.symbol, result)
        return result


# ---------------------------------------------------------------------------
# 4. Portfolio Risk Dashboard
# ---------------------------------------------------------------------------
class PortfolioRiskDashboard:
    """Compute portfolio-level risk metrics on demand."""

    @staticmethod
    def value_at_risk(positions: list[dict],
                      confidence: float = VAR_CONFIDENCE,
                      lookback: int = VAR_LOOKBACK_DAYS) -> dict:
        """
        Parametric (variance-covariance) VaR for the current portfolio.

        Returns dollar VaR and percentage VaR.
        """
        if not positions:
            return {"var_dollar": 0.0, "var_pct": 0.0, "confidence": confidence}

        symbols = [p["symbol"] for p in positions]
        weights = np.array([p["market_value"] for p in positions], dtype=float)
        total_value = weights.sum()
        if total_value == 0:
            return {"var_dollar": 0.0, "var_pct": 0.0, "confidence": confidence}

        weights = weights / total_value

        try:
            returns = _get_returns_matrix(symbols, days=lookback)
        except Exception as exc:
            logger.warning("VaR calculation failed: %s", exc)
            return {"var_dollar": 0.0, "var_pct": 0.0, "confidence": confidence,
                    "error": str(exc)}

        # Align weights to columns that are actually present
        aligned_weights = []
        aligned_symbols = []
        for sym, w in zip(symbols, weights):
            if sym in returns.columns:
                aligned_weights.append(w)
                aligned_symbols.append(sym)

        if not aligned_symbols:
            return {"var_dollar": 0.0, "var_pct": 0.0, "confidence": confidence}

        w = np.array(aligned_weights)
        w = w / w.sum()  # re-normalise

        cov = returns[aligned_symbols].cov().values * 252  # annualised
        port_var = float(np.sqrt(w @ cov @ w))
        z = _z_score(confidence)
        daily_var_pct = port_var / math.sqrt(252) * z
        daily_var_dollar = daily_var_pct * total_value

        return {
            "var_dollar": round(daily_var_dollar, 2),
            "var_pct": round(daily_var_pct, 4),
            "confidence": confidence,
            "annualised_volatility": round(port_var, 4),
        }

    @staticmethod
    def portfolio_heat(positions: list[dict],
                       stop_losses: dict[str, StopLoss],
                       equity: float) -> dict:
        """
        Portfolio heat = total capital at risk (distance to stops)
        as a percentage of equity.
        """
        total_risk = 0.0
        breakdown: list[dict] = []

        for pos in positions:
            sym = pos["symbol"]
            sl = stop_losses.get(sym)
            if sl is None:
                # Assume default stop loss %
                risk_per_share = pos["current_price"] * STOP_LOSS_PCT
            else:
                risk_per_share = max(pos["current_price"] - sl.stop_price, 0)

            position_risk = risk_per_share * abs(pos["qty"])
            total_risk += position_risk
            breakdown.append({
                "symbol": sym,
                "risk_dollar": round(position_risk, 2),
                "risk_pct_equity": round(position_risk / equity, 4) if equity else 0,
            })

        heat_pct = total_risk / equity if equity else 0.0
        return {
            "total_risk_dollar": round(total_risk, 2),
            "heat_pct": round(heat_pct, 4),
            "positions": breakdown,
        }

    @staticmethod
    def sector_allocation(positions: list[dict],
                          equity: float) -> dict[str, dict]:
        """Sector breakdown of current holdings."""
        sectors: dict[str, float] = {}
        for pos in positions:
            sector = _position_sector(pos["symbol"])
            sectors[sector] = sectors.get(sector, 0.0) + abs(pos["market_value"])

        result = {}
        for sector, value in sorted(sectors.items(), key=lambda x: -x[1]):
            result[sector] = {
                "value": round(value, 2),
                "pct_equity": round(value / equity, 4) if equity else 0,
            }
        return result

    @staticmethod
    def correlation_matrix(positions: list[dict],
                           days: int = 90) -> Optional[pd.DataFrame]:
        """Pairwise correlation matrix of current holdings (daily returns)."""
        symbols = [p["symbol"] for p in positions]
        if len(symbols) < 2:
            return None

        try:
            returns = _get_returns_matrix(symbols, days=days)
            return returns.corr()
        except Exception as exc:
            logger.warning("Correlation matrix failed: %s", exc)
            return None

    @classmethod
    def full_dashboard(cls, stop_losses: dict[str, StopLoss]) -> dict:
        """
        One-call convenience that assembles every risk metric into a single
        dict suitable for logging, display, or agent consumption.
        """
        account = get_account_info()
        positions = get_positions()
        equity = account["equity"]

        var_data = cls.value_at_risk(positions)
        heat_data = cls.portfolio_heat(positions, stop_losses, equity)
        sectors = cls.sector_allocation(positions, equity)

        corr = cls.correlation_matrix(positions)
        corr_dict = corr.to_dict() if corr is not None else {}

        return {
            "account": account,
            "var": var_data,
            "portfolio_heat": heat_data,
            "sector_allocation": sectors,
            "correlation_matrix": corr_dict,
            "open_positions": len(positions),
            "timestamp": datetime.utcnow().isoformat(),
        }


# ---------------------------------------------------------------------------
# 5. Circuit Breakers
# ---------------------------------------------------------------------------
class CircuitBreaker:
    """
    Automatic safeguards that override normal trading when portfolio-level
    thresholds are breached.
    """

    def __init__(self, risk_gate: RiskGate,
                 daily_halt_pct: float = MAX_DAILY_LOSS_PCT,
                 drawdown_reduce_pct: float = DRAWDOWN_REDUCE_THRESHOLD,
                 drawdown_halt_pct: float = DRAWDOWN_HALT_THRESHOLD):
        self.risk_gate = risk_gate
        self.daily_halt_pct = daily_halt_pct
        self.drawdown_reduce_pct = drawdown_reduce_pct
        self.drawdown_halt_pct = drawdown_halt_pct
        self._peak_equity: float = 0.0
        self._alerts: list[dict] = []

    @property
    def alerts(self) -> list[dict]:
        return list(self._alerts)

    def check(self, account: dict) -> dict:
        """
        Run circuit-breaker logic.  Returns a status dict and
        mutates the ``RiskGate`` state (halt / reduce) as needed.
        """
        equity = account["equity"]
        daily_pnl = account["daily_pnl"]
        status: dict = {"action": "none"}

        # Track equity high-water mark
        if equity > self._peak_equity:
            self._peak_equity = equity

        # -- 1. Daily loss halt ------------------------------------------------
        if equity > 0 and (daily_pnl / equity) <= -self.daily_halt_pct:
            self.risk_gate.halt_trading(
                f"daily loss {daily_pnl / equity:.2%} hit -{self.daily_halt_pct:.2%} limit"
            )
            status["action"] = "halt"
            status["reason"] = "daily loss limit"
            self._emit_alert("HALT", status["reason"], equity, daily_pnl)
            return status

        # -- 2. Drawdown checks ------------------------------------------------
        if self._peak_equity > 0:
            drawdown = (self._peak_equity - equity) / self._peak_equity

            if drawdown >= self.drawdown_halt_pct:
                self.risk_gate.halt_trading(
                    f"drawdown {drawdown:.2%} exceeded halt threshold "
                    f"{self.drawdown_halt_pct:.2%}"
                )
                status["action"] = "halt"
                status["reason"] = f"drawdown {drawdown:.2%}"
                self._emit_alert("HALT", status["reason"], equity, daily_pnl)
                return status

            if drawdown >= self.drawdown_reduce_pct:
                reduction = 0.5  # halve position sizes
                self.risk_gate._sizing_reduction = reduction
                status["action"] = "reduce"
                status["reason"] = f"drawdown {drawdown:.2%} — sizing at 50%"
                self._emit_alert("REDUCE", status["reason"], equity, daily_pnl)
                logger.warning("Circuit breaker: %s", status["reason"])
                return status

        return status

    def _emit_alert(self, level: str, reason: str,
                    equity: float, daily_pnl: float) -> None:
        alert = {
            "level": level,
            "reason": reason,
            "equity": equity,
            "daily_pnl": daily_pnl,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._alerts.append(alert)
        logger.critical("CIRCUIT BREAKER ALERT [%s]: %s", level, reason)

    def reset_peak(self, equity: float) -> None:
        """Manually reset the high-water mark (e.g. new quarter)."""
        self._peak_equity = equity


# ---------------------------------------------------------------------------
# 6. Orchestrator — ties everything together
# ---------------------------------------------------------------------------
class RiskManager:
    """
    Top-level facade used by the Head Coach / Execution Team to vet and
    execute trades.

    Usage::

        rm = RiskManager()
        result = rm.execute_trade(proposal)
    """

    def __init__(self):
        self.sizer = PositionSizer()
        self.stop_manager = StopLossManager()
        self.risk_gate = RiskGate()
        self.circuit_breaker = CircuitBreaker(self.risk_gate)
        self.dashboard = PortfolioRiskDashboard()

    # -- public API ---------------------------------------------------------

    def execute_trade(self, proposal: TradeProposal) -> dict:
        """
        Full pipeline: size -> check -> execute -> set stops.

        Returns a dict describing what happened (trade placed, blocked, etc.).
        """
        # 0. Circuit breaker sweep
        account = get_account_info()
        cb_status = self.circuit_breaker.check(account)
        if cb_status["action"] == "halt":
            return {"status": "blocked", "reason": cb_status["reason"]}

        equity = account["equity"]
        positions = get_positions()

        # 1. Fetch market data for sizing
        price_info = get_stock_price(proposal.symbol)
        current_price = proposal.limit_price or price_info["price"]
        if current_price is None or current_price <= 0:
            return {"status": "error", "reason": "could not determine price"}

        sector = proposal.sector or price_info.get("sector")
        proposal.sector = sector

        atr = _compute_atr(proposal.symbol)

        # Initial stop for sizing purposes
        if atr > 0:
            stop_price = current_price - atr * ATR_RISK_MULTIPLIER
        else:
            stop_price = current_price * (1.0 - STOP_LOSS_PCT)

        # Existing sector exposure
        sector_exposure = sum(
            abs(p["market_value"]) for p in positions
            if _position_sector(p["symbol"]) == sector
        )

        # 2. Size the position
        sizing = self.sizer.recommend(
            proposal, equity, current_price, atr, stop_price, sector_exposure,
        )
        shares = sizing["adjusted_shares"]

        # Apply circuit-breaker reduction
        if self.risk_gate.sizing_reduction < 1.0:
            shares = int(shares * self.risk_gate.sizing_reduction)

        if shares <= 0:
            return {"status": "blocked", "reason": "position size is zero after adjustments",
                    "sizing": sizing}

        # 3. Risk gate
        check = self.risk_gate.evaluate(proposal, shares, current_price)
        if not check.passed:
            return {"status": "blocked", "reason": str(check), "sizing": sizing}

        # 4. Human approval gate for large positions
        position_pct = (shares * current_price) / equity if equity else 1.0
        if position_pct > HUMAN_APPROVAL_ABOVE_PCT:
            logger.warning(
                "Trade %s %d %s (%.2f%% of equity) requires human approval",
                proposal.side, shares, proposal.symbol, position_pct * 100,
            )
            return {
                "status": "pending_human_approval",
                "symbol": proposal.symbol,
                "shares": shares,
                "side": proposal.side,
                "position_pct": round(position_pct, 4),
                "sizing": sizing,
                "risk_checks": check.checks,
            }

        # 5. Place the order
        order_result = place_order(
            symbol=proposal.symbol,
            qty=shares,
            side=proposal.side,
            order_type=proposal.order_type,
            limit_price=proposal.limit_price,
            stop_price=None,
        )

        # 6. Register stop loss
        if proposal.side == "buy":
            if atr > 0:
                self.stop_manager.create_atr_stop(proposal.symbol, current_price, atr)
            else:
                self.stop_manager.create_fixed_pct_stop(proposal.symbol, current_price)

        return {
            "status": "executed",
            "order": order_result,
            "shares": shares,
            "sizing": sizing,
            "risk_checks": check.checks,
            "stop_price": self.stop_manager.stops.get(proposal.symbol, StopLoss(
                symbol=proposal.symbol, entry_price=current_price,
                entry_date=datetime.utcnow(), stop_price=stop_price,
            )).stop_price,
        }

    def update_stops(self) -> list[dict]:
        """
        Refresh trailing stops, check breakevens and time stops for all
        tracked positions.  Close any that have been stopped out.

        Returns list of close results.
        """
        positions = get_positions()
        atr_cache = {}
        for pos in positions:
            try:
                atr_cache[pos["symbol"]] = _compute_atr(pos["symbol"])
            except Exception:
                atr_cache[pos["symbol"]] = 0.0

        to_close = self.stop_manager.update_all(positions, atr_cache)

        results = []
        for sym in to_close:
            try:
                close_result = close_position(sym)
                self.stop_manager.remove(sym)
                results.append(close_result)
                logger.info("Closed position %s due to stop", sym)
            except Exception as exc:
                logger.error("Failed to close %s: %s", sym, exc)
                results.append({"symbol": sym, "status": "error", "error": str(exc)})

        return results

    def get_dashboard(self) -> dict:
        """Return the full portfolio risk dashboard."""
        return self.dashboard.full_dashboard(self.stop_manager.stops)

    def run_circuit_breakers(self) -> dict:
        """Manually trigger a circuit-breaker check."""
        account = get_account_info()
        return self.circuit_breaker.check(account)


# ---------------------------------------------------------------------------
# Helpers (module-private)
# ---------------------------------------------------------------------------
_sector_cache: dict[str, str] = {}


def _position_sector(symbol: str) -> str:
    """Look up sector for a symbol, with a simple in-memory cache."""
    if symbol in _sector_cache:
        return _sector_cache[symbol]
    try:
        info = get_stock_price(symbol)
        sector = info.get("sector") or "Unknown"
    except Exception:
        sector = "Unknown"
    _sector_cache[symbol] = sector
    return sector


def _compute_atr(symbol: str, period: int = ATR_PERIOD) -> float:
    """Compute the latest Average True Range for *symbol*."""
    try:
        df = get_price_history(symbol, period="3mo", interval="1d")
        if df.empty or len(df) < period + 1:
            return 0.0

        high = df["High"]
        low = df["Low"]
        close = df["Close"]

        tr1 = high - low
        tr2 = (high - close.shift(1)).abs()
        tr3 = (low - close.shift(1)).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(period).mean().iloc[-1]
        return float(atr) if not math.isnan(atr) else 0.0
    except Exception as exc:
        logger.warning("ATR calculation failed for %s: %s", symbol, exc)
        return 0.0


def _get_returns_matrix(symbols: list[str], days: int = 90) -> pd.DataFrame:
    """
    Download daily close prices and return a DataFrame of daily returns,
    one column per symbol.
    """
    period = f"{days}d"
    frames = {}
    for sym in symbols:
        try:
            df = get_price_history(sym, period=period, interval="1d")
            if not df.empty:
                frames[sym] = df["Close"]
        except Exception:
            continue

    if not frames:
        return pd.DataFrame()

    prices = pd.DataFrame(frames)
    returns = prices.pct_change().dropna()
    return returns


def _z_score(confidence: float) -> float:
    """Approximate z-score for common confidence levels."""
    # Use scipy if available, otherwise a lookup table is fine
    table = {
        0.90: 1.2816,
        0.95: 1.6449,
        0.99: 2.3263,
    }
    if confidence in table:
        return table[confidence]

    # Fallback: Beasley-Springer-Moro approximation is overkill here;
    # use a simple linear interp between known values.
    try:
        from scipy.stats import norm
        return float(norm.ppf(confidence))
    except ImportError:
        return 1.6449  # default to 95 %
