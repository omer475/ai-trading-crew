"""Trade Memory & Learning System — lets agents learn from past trades.

Provides four core capabilities:
  1. Trade Journal     - Log every trade with full context
  2. Pattern Recognition - Query past trades by conditions / tags
  3. Agent Performance   - Track accuracy & reliability of all 50 agents
  4. Learning Summaries  - Generate periodic lessons and rankings

Uses ChromaDB for semantic search and JSON files for structured data.
"""

import json
import os
import time
import uuid
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional

from tools.knowledge_base import get_or_create_collection, search as kb_search

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "trade_memory")
_TRADES_FILE = os.path.join(_DATA_DIR, "trades.json")
_AGENT_STATS_FILE = os.path.join(_DATA_DIR, "agent_stats.json")

# ChromaDB collection names
_TRADE_JOURNAL_COLLECTION = "trade_memory_journal"
_LESSONS_COLLECTION = "trade_memory_lessons"


def _ensure_data_dir():
    """Create the data directory if it doesn't exist."""
    os.makedirs(_DATA_DIR, exist_ok=True)


def _load_json(path: str) -> list | dict:
    """Load a JSON file, returning an empty list/dict if missing."""
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)


def _save_json(path: str, data):
    """Atomically write JSON data to a file."""
    _ensure_data_dir()
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2, default=str)
    os.replace(tmp, path)


# ===================================================================
# 1. TRADE JOURNAL
# ===================================================================

def log_trade(
    symbol: str,
    side: str,
    entry_price: float,
    exit_price: Optional[float] = None,
    quantity: int = 0,
    pnl: Optional[float] = None,
    agents_agreed: Optional[list[str]] = None,
    agents_disagreed: Optional[list[str]] = None,
    agree_reasons: Optional[dict[str, str]] = None,
    disagree_reasons: Optional[dict[str, str]] = None,
    market_conditions: Optional[dict] = None,
    confidence: float = 0.0,
    outcome: str = "pending",
    lesson: str = "",
    tags: Optional[list[str]] = None,
    strategy: str = "",
    notes: str = "",
) -> str:
    """Log a trade with full context to both JSON and ChromaDB.

    Args:
        symbol:             Ticker, e.g. "AAPL".
        side:               "buy" or "sell".
        entry_price:        Price at entry.
        exit_price:         Price at exit (None if still open).
        quantity:           Number of shares.
        pnl:                Realized profit/loss in dollars.
        agents_agreed:      List of agent IDs that supported the trade.
        agents_disagreed:   List of agent IDs that opposed the trade.
        agree_reasons:      {agent_id: reason_string} for supporters.
        disagree_reasons:   {agent_id: reason_string} for opponents.
        market_conditions:  Dict with keys like rsi, trend, vix, sector_performance.
        confidence:         Confidence at entry, 0.0-1.0.
        outcome:            "win", "loss", "breakeven", or "pending".
        lesson:             What was learned from this trade.
        tags:               E.g. ["momentum", "earnings_play", "breakout"].
        strategy:           Strategy name that generated the trade.
        notes:              Free-form notes.

    Returns:
        The trade_id of the logged trade.
    """
    agents_agreed = agents_agreed or []
    agents_disagreed = agents_disagreed or []
    agree_reasons = agree_reasons or {}
    disagree_reasons = disagree_reasons or {}
    market_conditions = market_conditions or {}
    tags = tags or []

    timestamp = datetime.utcnow().isoformat()
    trade_id = f"trade_{symbol}_{int(time.time())}_{uuid.uuid4().hex[:6]}"

    trade_record = {
        "trade_id": trade_id,
        "timestamp": timestamp,
        "symbol": symbol,
        "side": side.lower(),
        "entry_price": entry_price,
        "exit_price": exit_price,
        "quantity": quantity,
        "pnl": pnl,
        "pnl_pct": (
            round((exit_price - entry_price) / entry_price * 100, 4)
            if exit_price and entry_price
            else None
        ),
        "agents_agreed": agents_agreed,
        "agents_disagreed": agents_disagreed,
        "agree_reasons": agree_reasons,
        "disagree_reasons": disagree_reasons,
        "market_conditions": market_conditions,
        "confidence": confidence,
        "outcome": outcome,
        "lesson": lesson,
        "tags": tags,
        "strategy": strategy,
        "notes": notes,
    }

    # If side is sell, flip pnl_pct sign convention
    if side.lower() == "sell" and trade_record["pnl_pct"] is not None:
        trade_record["pnl_pct"] = -trade_record["pnl_pct"]

    # ---- Persist to JSON ----
    trades = _load_json(_TRADES_FILE)
    trades.append(trade_record)
    _save_json(_TRADES_FILE, trades)

    # ---- Persist to ChromaDB for semantic search ----
    mc = market_conditions
    doc_text = (
        f"{side.upper()} {symbol} at ${entry_price:.2f}. "
        f"Exit: ${exit_price:.2f}. " if exit_price else f"{side.upper()} {symbol} at ${entry_price:.2f}. "
    )
    doc_text += (
        f"P/L: ${pnl:.2f}. " if pnl is not None else ""
    )
    doc_text += (
        f"Outcome: {outcome}. "
        f"Confidence: {confidence:.0%}. "
        f"Strategy: {strategy}. "
        f"Tags: {', '.join(tags)}. "
        f"RSI: {mc.get('rsi', 'N/A')}. "
        f"Trend: {mc.get('trend', 'N/A')}. "
        f"VIX: {mc.get('vix', 'N/A')}. "
        f"Sector: {mc.get('sector_performance', 'N/A')}. "
        f"Agents agreed: {', '.join(agents_agreed)}. "
        f"Agents disagreed: {', '.join(agents_disagreed)}. "
        f"Lesson: {lesson}"
    )

    # Flatten metadata for ChromaDB (it only supports str/int/float/bool values)
    chroma_meta = {
        "trade_id": trade_id,
        "timestamp": timestamp,
        "symbol": symbol,
        "side": side.lower(),
        "entry_price": entry_price,
        "exit_price": exit_price or 0.0,
        "pnl": pnl if pnl is not None else 0.0,
        "pnl_pct": trade_record["pnl_pct"] if trade_record["pnl_pct"] is not None else 0.0,
        "confidence": confidence,
        "outcome": outcome,
        "strategy": strategy,
        "tags": ",".join(tags),
        "rsi": mc.get("rsi", 0.0),
        "trend": str(mc.get("trend", "")),
        "vix": mc.get("vix", 0.0),
        "num_agreed": len(agents_agreed),
        "num_disagreed": len(agents_disagreed),
    }

    collection = get_or_create_collection(_TRADE_JOURNAL_COLLECTION)
    collection.add(documents=[doc_text], metadatas=[chroma_meta], ids=[trade_id])

    # ---- Update agent stats ----
    _update_agent_stats_from_trade(trade_record)

    return trade_id


def update_trade(trade_id: str, **updates) -> bool:
    """Update fields on an existing trade (e.g. set exit_price, pnl, outcome, lesson).

    Returns True if the trade was found and updated.
    """
    trades = _load_json(_TRADES_FILE)
    for trade in trades:
        if trade["trade_id"] == trade_id:
            trade.update(updates)
            # Recalculate pnl_pct if prices changed
            if "exit_price" in updates or "entry_price" in updates:
                ep = trade.get("exit_price")
                en = trade.get("entry_price")
                if ep and en:
                    pct = round((ep - en) / en * 100, 4)
                    if trade["side"] == "sell":
                        pct = -pct
                    trade["pnl_pct"] = pct
            _save_json(_TRADES_FILE, trades)

            # Update the agent stats if outcome changed
            if "outcome" in updates:
                _rebuild_agent_stats()

            return True
    return False


def get_trade(trade_id: str) -> Optional[dict]:
    """Retrieve a single trade by ID."""
    trades = _load_json(_TRADES_FILE)
    for t in trades:
        if t["trade_id"] == trade_id:
            return t
    return None


def get_all_trades() -> list[dict]:
    """Return all trade records from the JSON store."""
    return _load_json(_TRADES_FILE)


# ===================================================================
# 2. PATTERN RECOGNITION — query past trades
# ===================================================================

def search_trades(query: str, n_results: int = 10) -> list[dict]:
    """Semantic search over past trades using ChromaDB.

    Examples:
        search_trades("bought AAPL when RSI was below 30")
        search_trades("momentum breakout trades")
        search_trades("biggest losses in high VIX environment")
    """
    collection = get_or_create_collection(_TRADE_JOURNAL_COLLECTION)
    if collection.count() == 0:
        return []
    n = min(n_results, collection.count())
    results = collection.query(query_texts=[query], n_results=n)
    return [
        {"text": doc, "metadata": meta}
        for doc, meta in zip(results["documents"][0], results["metadatas"][0])
    ]


def query_trades_by_symbol(symbol: str) -> list[dict]:
    """Return all trades for a specific symbol."""
    return [t for t in get_all_trades() if t["symbol"].upper() == symbol.upper()]


def query_trades_by_tag(tag: str) -> list[dict]:
    """Return all trades with a specific tag."""
    tag_lower = tag.lower()
    return [t for t in get_all_trades() if tag_lower in [tg.lower() for tg in t.get("tags", [])]]


def query_trades_by_outcome(outcome: str) -> list[dict]:
    """Return all trades with a specific outcome ('win', 'loss', 'breakeven')."""
    return [t for t in get_all_trades() if t.get("outcome", "").lower() == outcome.lower()]


def query_trades_by_conditions(
    symbol: Optional[str] = None,
    side: Optional[str] = None,
    outcome: Optional[str] = None,
    tag: Optional[str] = None,
    min_confidence: Optional[float] = None,
    max_confidence: Optional[float] = None,
    rsi_below: Optional[float] = None,
    rsi_above: Optional[float] = None,
    vix_above: Optional[float] = None,
    vix_below: Optional[float] = None,
    trend: Optional[str] = None,
    strategy: Optional[str] = None,
    since: Optional[str] = None,
    agent_agreed: Optional[str] = None,
    agent_disagreed: Optional[str] = None,
) -> list[dict]:
    """Filter trades by structured conditions.

    Args:
        symbol:         Filter by ticker.
        side:           "buy" or "sell".
        outcome:        "win", "loss", "breakeven", "pending".
        tag:            Must have this tag.
        min_confidence: Confidence >= this value.
        max_confidence: Confidence <= this value.
        rsi_below:      RSI was below this at entry.
        rsi_above:      RSI was above this at entry.
        vix_above:      VIX was above this at entry.
        vix_below:      VIX was below this at entry.
        trend:          Market trend at entry (e.g. "uptrend", "downtrend").
        strategy:       Strategy name.
        since:          ISO date string — only trades after this date.
        agent_agreed:   Agent ID that agreed on the trade.
        agent_disagreed: Agent ID that disagreed on the trade.

    Returns:
        List of matching trade dicts.
    """
    trades = get_all_trades()
    results = []
    for t in trades:
        mc = t.get("market_conditions", {})
        if symbol and t["symbol"].upper() != symbol.upper():
            continue
        if side and t["side"] != side.lower():
            continue
        if outcome and t.get("outcome", "").lower() != outcome.lower():
            continue
        if tag and tag.lower() not in [tg.lower() for tg in t.get("tags", [])]:
            continue
        if min_confidence is not None and t.get("confidence", 0) < min_confidence:
            continue
        if max_confidence is not None and t.get("confidence", 0) > max_confidence:
            continue
        if rsi_below is not None and mc.get("rsi") is not None and mc["rsi"] >= rsi_below:
            continue
        if rsi_above is not None and mc.get("rsi") is not None and mc["rsi"] <= rsi_above:
            continue
        if vix_above is not None and mc.get("vix") is not None and mc["vix"] <= vix_above:
            continue
        if vix_below is not None and mc.get("vix") is not None and mc["vix"] >= vix_below:
            continue
        if trend and str(mc.get("trend", "")).lower() != trend.lower():
            continue
        if strategy and t.get("strategy", "").lower() != strategy.lower():
            continue
        if since:
            if t.get("timestamp", "") < since:
                continue
        if agent_agreed and agent_agreed not in t.get("agents_agreed", []):
            continue
        if agent_disagreed and agent_disagreed not in t.get("agents_disagreed", []):
            continue
        results.append(t)
    return results


def get_win_rate(
    tag: Optional[str] = None,
    strategy: Optional[str] = None,
    symbol: Optional[str] = None,
    agent_id: Optional[str] = None,
) -> dict:
    """Calculate win rate, optionally filtered by tag / strategy / symbol / agent.

    Returns:
        {total, wins, losses, breakeven, pending, win_rate, avg_pnl, avg_pnl_pct}
    """
    filters = {}
    if tag:
        filters["tag"] = tag
    if strategy:
        filters["strategy"] = strategy
    if symbol:
        filters["symbol"] = symbol
    if agent_id:
        filters["agent_agreed"] = agent_id

    trades = query_trades_by_conditions(**filters) if filters else get_all_trades()

    wins = [t for t in trades if t.get("outcome") == "win"]
    losses = [t for t in trades if t.get("outcome") == "loss"]
    breakevens = [t for t in trades if t.get("outcome") == "breakeven"]
    pending = [t for t in trades if t.get("outcome") == "pending"]
    resolved = wins + losses + breakevens

    pnls = [t["pnl"] for t in resolved if t.get("pnl") is not None]
    pnl_pcts = [t["pnl_pct"] for t in resolved if t.get("pnl_pct") is not None]

    return {
        "total": len(trades),
        "wins": len(wins),
        "losses": len(losses),
        "breakeven": len(breakevens),
        "pending": len(pending),
        "win_rate": round(len(wins) / len(resolved), 4) if resolved else 0.0,
        "avg_pnl": round(sum(pnls) / len(pnls), 2) if pnls else 0.0,
        "avg_pnl_pct": round(sum(pnl_pcts) / len(pnl_pcts), 4) if pnl_pcts else 0.0,
        "total_pnl": round(sum(pnls), 2) if pnls else 0.0,
        "best_trade_pnl": round(max(pnls), 2) if pnls else 0.0,
        "worst_trade_pnl": round(min(pnls), 2) if pnls else 0.0,
    }


def biggest_losses(n: int = 5) -> list[dict]:
    """Return the N trades with the largest losses."""
    trades = [t for t in get_all_trades() if t.get("pnl") is not None]
    trades.sort(key=lambda t: t["pnl"])
    return trades[:n]


def biggest_wins(n: int = 5) -> list[dict]:
    """Return the N trades with the largest gains."""
    trades = [t for t in get_all_trades() if t.get("pnl") is not None]
    trades.sort(key=lambda t: t["pnl"], reverse=True)
    return trades[:n]


def conditions_leading_to_losses(n: int = 10) -> dict:
    """Analyze market conditions that are common among the worst trades.

    Returns a summary dict describing frequent conditions in the worst trades.
    """
    losses = [t for t in get_all_trades() if t.get("outcome") == "loss"]
    if not losses:
        return {"message": "No losing trades recorded yet."}

    # Sort by severity
    losses.sort(key=lambda t: t.get("pnl", 0))
    worst = losses[:n]

    trends = defaultdict(int)
    rsi_values = []
    vix_values = []
    tags_freq = defaultdict(int)
    strategies_freq = defaultdict(int)
    avg_confidence = []

    for t in worst:
        mc = t.get("market_conditions", {})
        if mc.get("trend"):
            trends[mc["trend"]] += 1
        if mc.get("rsi") is not None:
            rsi_values.append(mc["rsi"])
        if mc.get("vix") is not None:
            vix_values.append(mc["vix"])
        for tag in t.get("tags", []):
            tags_freq[tag] += 1
        if t.get("strategy"):
            strategies_freq[t["strategy"]] += 1
        if t.get("confidence") is not None:
            avg_confidence.append(t["confidence"])

    return {
        "analyzed_trades": len(worst),
        "common_trends": dict(trends),
        "avg_rsi_at_entry": round(sum(rsi_values) / len(rsi_values), 2) if rsi_values else None,
        "avg_vix_at_entry": round(sum(vix_values) / len(vix_values), 2) if vix_values else None,
        "common_tags": dict(tags_freq),
        "common_strategies": dict(strategies_freq),
        "avg_confidence": round(sum(avg_confidence) / len(avg_confidence), 4) if avg_confidence else None,
        "total_pnl_of_worst": round(sum(t.get("pnl", 0) for t in worst), 2),
    }


# ===================================================================
# 3. AGENT PERFORMANCE TRACKING
# ===================================================================

def _empty_agent_stats() -> dict:
    """Return default stats structure for a single agent."""
    return {
        "total_calls": 0,
        "correct_calls": 0,
        "incorrect_calls": 0,
        "pending_calls": 0,
        "buy_calls": 0,
        "sell_calls": 0,
        "hold_calls": 0,
        "correct_buys": 0,
        "correct_sells": 0,
        "correct_holds": 0,
        "reliability_score": 0.0,
        "by_market_condition": {},  # {condition_key: {correct, total}}
        "by_symbol": {},            # {symbol: {correct, total}}
    }


def _load_agent_stats() -> dict:
    """Load agent performance stats from disk."""
    data = _load_json(_AGENT_STATS_FILE)
    return data if isinstance(data, dict) else {}


def _save_agent_stats(stats: dict):
    """Persist agent stats to disk."""
    _save_json(_AGENT_STATS_FILE, stats)


def _update_agent_stats_from_trade(trade: dict):
    """Update every agent's stats based on a single trade record."""
    outcome = trade.get("outcome", "pending")
    symbol = trade.get("symbol", "UNK")
    side = trade.get("side", "")
    mc = trade.get("market_conditions", {})
    trend = str(mc.get("trend", "unknown"))
    vix = mc.get("vix")

    # Determine market regime label
    if vix is not None:
        if vix > 25:
            regime = "high_volatility"
        elif vix < 15:
            regime = "low_volatility"
        else:
            regime = "normal_volatility"
    else:
        regime = "unknown_volatility"

    condition_key = f"{trend}_{regime}"

    stats = _load_agent_stats()

    # Agents who agreed predicted the trade direction correctly if trade won
    is_resolved = outcome in ("win", "loss", "breakeven")
    is_correct = outcome == "win"

    for agent_id in trade.get("agents_agreed", []):
        if agent_id not in stats:
            stats[agent_id] = _empty_agent_stats()
        s = stats[agent_id]
        s["total_calls"] += 1
        if side == "buy":
            s["buy_calls"] += 1
        elif side == "sell":
            s["sell_calls"] += 1

        if is_resolved:
            if is_correct:
                s["correct_calls"] += 1
                if side == "buy":
                    s["correct_buys"] += 1
                elif side == "sell":
                    s["correct_sells"] += 1
            else:
                s["incorrect_calls"] += 1
        else:
            s["pending_calls"] += 1

        # By market condition
        if condition_key not in s["by_market_condition"]:
            s["by_market_condition"][condition_key] = {"correct": 0, "total": 0}
        s["by_market_condition"][condition_key]["total"] += 1
        if is_correct:
            s["by_market_condition"][condition_key]["correct"] += 1

        # By symbol
        if symbol not in s["by_symbol"]:
            s["by_symbol"][symbol] = {"correct": 0, "total": 0}
        s["by_symbol"][symbol]["total"] += 1
        if is_correct:
            s["by_symbol"][symbol]["correct"] += 1

        # Recalculate reliability
        resolved_total = s["correct_calls"] + s["incorrect_calls"]
        s["reliability_score"] = (
            round(s["correct_calls"] / resolved_total, 4) if resolved_total > 0 else 0.0
        )

    # Agents who disagreed — they were correct if the trade *lost*
    is_disagree_correct = outcome == "loss"

    for agent_id in trade.get("agents_disagreed", []):
        if agent_id not in stats:
            stats[agent_id] = _empty_agent_stats()
        s = stats[agent_id]
        s["total_calls"] += 1
        s["hold_calls"] += 1  # disagreeing counts as a hold/contra call

        if is_resolved:
            if is_disagree_correct:
                s["correct_calls"] += 1
                s["correct_holds"] += 1
            else:
                s["incorrect_calls"] += 1
        else:
            s["pending_calls"] += 1

        # By market condition
        if condition_key not in s["by_market_condition"]:
            s["by_market_condition"][condition_key] = {"correct": 0, "total": 0}
        s["by_market_condition"][condition_key]["total"] += 1
        if is_disagree_correct:
            s["by_market_condition"][condition_key]["correct"] += 1

        # By symbol
        if symbol not in s["by_symbol"]:
            s["by_symbol"][symbol] = {"correct": 0, "total": 0}
        s["by_symbol"][symbol]["total"] += 1
        if is_disagree_correct:
            s["by_symbol"][symbol]["correct"] += 1

        # Recalculate reliability
        resolved_total = s["correct_calls"] + s["incorrect_calls"]
        s["reliability_score"] = (
            round(s["correct_calls"] / resolved_total, 4) if resolved_total > 0 else 0.0
        )

    _save_agent_stats(stats)


def _rebuild_agent_stats():
    """Rebuild all agent stats from scratch by replaying every trade."""
    _save_agent_stats({})
    for trade in get_all_trades():
        _update_agent_stats_from_trade(trade)


def get_agent_stats(agent_id: str) -> dict:
    """Get performance stats for a specific agent.

    Returns:
        Dict with total_calls, correct_calls, reliability_score,
        by_market_condition, by_symbol, etc.
    """
    stats = _load_agent_stats()
    return stats.get(agent_id, _empty_agent_stats())


def get_all_agent_stats() -> dict:
    """Return stats for all agents that have participated in trades."""
    return _load_agent_stats()


def get_agent_rankings(min_calls: int = 5) -> list[dict]:
    """Rank agents by reliability score.

    Args:
        min_calls: Minimum resolved calls to be included in ranking.

    Returns:
        List of {agent_id, reliability_score, correct, total, ...}
        sorted by reliability descending.
    """
    stats = _load_agent_stats()
    rankings = []
    for agent_id, s in stats.items():
        resolved = s["correct_calls"] + s["incorrect_calls"]
        if resolved < min_calls:
            continue
        rankings.append({
            "agent_id": agent_id,
            "reliability_score": s["reliability_score"],
            "correct_calls": s["correct_calls"],
            "incorrect_calls": s["incorrect_calls"],
            "total_calls": s["total_calls"],
            "buy_accuracy": (
                round(s["correct_buys"] / s["buy_calls"], 4)
                if s["buy_calls"] > 0 else None
            ),
            "sell_accuracy": (
                round(s["correct_sells"] / s["sell_calls"], 4)
                if s["sell_calls"] > 0 else None
            ),
        })

    rankings.sort(key=lambda r: r["reliability_score"], reverse=True)
    return rankings


def get_best_agents_for_condition(condition_key: str, min_calls: int = 3) -> list[dict]:
    """Find which agents perform best under a specific market condition.

    Args:
        condition_key: e.g. "uptrend_high_volatility", "downtrend_low_volatility".
        min_calls:     Minimum calls in that condition to be ranked.

    Returns:
        List of {agent_id, accuracy, correct, total} sorted by accuracy descending.
    """
    stats = _load_agent_stats()
    results = []
    for agent_id, s in stats.items():
        cond = s.get("by_market_condition", {}).get(condition_key)
        if cond and cond["total"] >= min_calls:
            results.append({
                "agent_id": agent_id,
                "accuracy": round(cond["correct"] / cond["total"], 4),
                "correct": cond["correct"],
                "total": cond["total"],
            })
    results.sort(key=lambda r: r["accuracy"], reverse=True)
    return results


def get_most_accurate_agent() -> Optional[dict]:
    """Return the single most accurate agent (with at least 5 resolved calls)."""
    rankings = get_agent_rankings(min_calls=5)
    return rankings[0] if rankings else None


# ===================================================================
# 4. LEARNING SUMMARIES
# ===================================================================

def generate_trade_summary(last_n: int = 30) -> dict:
    """Generate a summary of the last N trades.

    Returns:
        Dict with overall_stats, top_lessons, best_tags, worst_tags,
        best_strategies, worst_strategies.
    """
    trades = get_all_trades()[-last_n:]
    if not trades:
        return {"message": "No trades recorded yet."}

    wins = [t for t in trades if t.get("outcome") == "win"]
    losses = [t for t in trades if t.get("outcome") == "loss"]
    resolved = [t for t in trades if t.get("outcome") in ("win", "loss", "breakeven")]
    pnls = [t["pnl"] for t in resolved if t.get("pnl") is not None]

    # Collect lessons
    lessons = [t["lesson"] for t in trades if t.get("lesson")]

    # Tag performance
    tag_stats = defaultdict(lambda: {"wins": 0, "losses": 0, "total_pnl": 0.0})
    for t in resolved:
        for tag in t.get("tags", []):
            if t["outcome"] == "win":
                tag_stats[tag]["wins"] += 1
            elif t["outcome"] == "loss":
                tag_stats[tag]["losses"] += 1
            tag_stats[tag]["total_pnl"] += t.get("pnl", 0)

    # Strategy performance
    strat_stats = defaultdict(lambda: {"wins": 0, "losses": 0, "total_pnl": 0.0})
    for t in resolved:
        strat = t.get("strategy", "unknown")
        if strat:
            if t["outcome"] == "win":
                strat_stats[strat]["wins"] += 1
            elif t["outcome"] == "loss":
                strat_stats[strat]["losses"] += 1
            strat_stats[strat]["total_pnl"] += t.get("pnl", 0)

    # Sort tags and strategies by total P/L
    best_tags = sorted(tag_stats.items(), key=lambda x: x[1]["total_pnl"], reverse=True)[:5]
    worst_tags = sorted(tag_stats.items(), key=lambda x: x[1]["total_pnl"])[:5]
    best_strategies = sorted(strat_stats.items(), key=lambda x: x[1]["total_pnl"], reverse=True)[:5]
    worst_strategies = sorted(strat_stats.items(), key=lambda x: x[1]["total_pnl"])[:5]

    return {
        "period": f"Last {len(trades)} trades",
        "overall_stats": {
            "total_trades": len(trades),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": round(len(wins) / len(resolved), 4) if resolved else 0.0,
            "total_pnl": round(sum(pnls), 2) if pnls else 0.0,
            "avg_pnl": round(sum(pnls) / len(pnls), 2) if pnls else 0.0,
            "best_trade": round(max(pnls), 2) if pnls else 0.0,
            "worst_trade": round(min(pnls), 2) if pnls else 0.0,
        },
        "top_lessons": lessons[-5:],  # Most recent 5 lessons
        "best_tags": [{"tag": tag, **data} for tag, data in best_tags],
        "worst_tags": [{"tag": tag, **data} for tag, data in worst_tags],
        "best_strategies": [{"strategy": s, **data} for s, data in best_strategies],
        "worst_strategies": [{"strategy": s, **data} for s, data in worst_strategies],
    }


def generate_pattern_report() -> dict:
    """Analyze all trades and identify patterns that consistently work or fail.

    Returns:
        Dict with working_patterns and failing_patterns.
    """
    trades = get_all_trades()
    resolved = [t for t in trades if t.get("outcome") in ("win", "loss", "breakeven")]
    if len(resolved) < 5:
        return {"message": f"Need at least 5 resolved trades. Currently have {len(resolved)}."}

    # Analyze by tag
    tag_perf = defaultdict(lambda: {"wins": 0, "losses": 0, "trades": []})
    for t in resolved:
        for tag in t.get("tags", []):
            outcome = t.get("outcome")
            if outcome == "win":
                tag_perf[tag]["wins"] += 1
            elif outcome == "loss":
                tag_perf[tag]["losses"] += 1
            tag_perf[tag]["trades"].append(t.get("pnl", 0))

    working = []
    failing = []
    for tag, data in tag_perf.items():
        total = data["wins"] + data["losses"]
        if total < 3:
            continue
        win_rate = data["wins"] / total
        avg_pnl = sum(data["trades"]) / len(data["trades"]) if data["trades"] else 0
        entry = {
            "pattern": tag,
            "win_rate": round(win_rate, 4),
            "total_trades": total,
            "avg_pnl": round(avg_pnl, 2),
        }
        if win_rate >= 0.6:
            working.append(entry)
        elif win_rate <= 0.4:
            failing.append(entry)

    # Analyze by market condition
    cond_perf = defaultdict(lambda: {"wins": 0, "losses": 0})
    for t in resolved:
        mc = t.get("market_conditions", {})
        trend = mc.get("trend", "unknown")
        vix = mc.get("vix")
        regime = "high_vol" if (vix and vix > 25) else "low_vol" if (vix and vix < 15) else "normal_vol"
        cond_key = f"{trend}_{regime}"
        if t["outcome"] == "win":
            cond_perf[cond_key]["wins"] += 1
        elif t["outcome"] == "loss":
            cond_perf[cond_key]["losses"] += 1

    condition_insights = []
    for cond, data in cond_perf.items():
        total = data["wins"] + data["losses"]
        if total < 3:
            continue
        win_rate = data["wins"] / total
        condition_insights.append({
            "condition": cond,
            "win_rate": round(win_rate, 4),
            "total_trades": total,
        })
    condition_insights.sort(key=lambda x: x["win_rate"], reverse=True)

    working.sort(key=lambda x: x["win_rate"], reverse=True)
    failing.sort(key=lambda x: x["win_rate"])

    return {
        "working_patterns": working,
        "failing_patterns": failing,
        "condition_insights": condition_insights,
    }


def generate_agent_reliability_report(min_calls: int = 3) -> dict:
    """Generate a full agent reliability ranking report.

    Returns:
        Dict with top_agents, bottom_agents, best_by_condition, and specialist_insights.
    """
    rankings = get_agent_rankings(min_calls=min_calls)

    if not rankings:
        return {"message": f"No agents with at least {min_calls} resolved calls."}

    # Find unique conditions across all agents
    stats = _load_agent_stats()
    all_conditions = set()
    for s in stats.values():
        all_conditions.update(s.get("by_market_condition", {}).keys())

    best_by_condition = {}
    for cond in all_conditions:
        top = get_best_agents_for_condition(cond, min_calls=2)
        if top:
            best_by_condition[cond] = top[:3]

    # Find specialists — agents notably better at specific symbols
    specialist_insights = []
    for agent_id, s in stats.items():
        for sym, sym_data in s.get("by_symbol", {}).items():
            if sym_data["total"] >= 3:
                acc = sym_data["correct"] / sym_data["total"]
                if acc >= 0.7:
                    specialist_insights.append({
                        "agent_id": agent_id,
                        "symbol": sym,
                        "accuracy": round(acc, 4),
                        "total": sym_data["total"],
                    })

    specialist_insights.sort(key=lambda x: x["accuracy"], reverse=True)

    return {
        "top_agents": rankings[:10],
        "bottom_agents": rankings[-5:] if len(rankings) >= 5 else rankings,
        "best_by_condition": best_by_condition,
        "symbol_specialists": specialist_insights[:10],
    }


def generate_lessons(last_n: int = 30, top_k: int = 5) -> list[str]:
    """Extract the top K lessons from the last N trades.

    Prioritizes lessons from trades with extreme outcomes (big wins or big losses).
    """
    trades = get_all_trades()[-last_n:]
    if not trades:
        return ["No trades recorded yet."]

    # Score each lesson by |pnl| — bigger impact = more important lesson
    scored = []
    for t in trades:
        lesson = t.get("lesson", "").strip()
        if not lesson:
            continue
        weight = abs(t.get("pnl", 0)) if t.get("pnl") is not None else 0
        scored.append((weight, lesson, t.get("outcome", ""), t.get("symbol", "")))

    scored.sort(key=lambda x: x[0], reverse=True)

    results = []
    for weight, lesson, outcome, symbol in scored[:top_k]:
        prefix = "[WIN]" if outcome == "win" else "[LOSS]" if outcome == "loss" else f"[{outcome.upper()}]"
        results.append(f"{prefix} {symbol}: {lesson}")

    if not results:
        results.append("No lessons recorded yet. Add lessons to trades using update_trade().")

    return results


def store_lesson(lesson_text: str, tags: Optional[list[str]] = None, source_trade_id: str = ""):
    """Store a standalone lesson in ChromaDB for future retrieval.

    Useful for general insights not tied to a single trade.
    """
    tags = tags or []
    lesson_id = f"lesson_{int(time.time())}_{uuid.uuid4().hex[:6]}"
    meta = {
        "timestamp": datetime.utcnow().isoformat(),
        "tags": ",".join(tags),
        "source_trade_id": source_trade_id,
    }
    collection = get_or_create_collection(_LESSONS_COLLECTION)
    collection.add(documents=[lesson_text], metadatas=[meta], ids=[lesson_id])
    return lesson_id


def search_lessons(query: str, n_results: int = 5) -> list[dict]:
    """Semantic search over stored lessons."""
    collection = get_or_create_collection(_LESSONS_COLLECTION)
    if collection.count() == 0:
        return []
    n = min(n_results, collection.count())
    results = collection.query(query_texts=[query], n_results=n)
    return [
        {"text": doc, "metadata": meta}
        for doc, meta in zip(results["documents"][0], results["metadatas"][0])
    ]


# ===================================================================
# CONVENIENCE — single function for agents to call
# ===================================================================

def remember(query: str, n_results: int = 5) -> dict:
    """One-stop function for agents: search both trades and lessons.

    Args:
        query: Natural language question, e.g.
               "What happened when we bought tech stocks during high VIX?"

    Returns:
        Dict with past_trades and lessons matching the query.
    """
    return {
        "past_trades": search_trades(query, n_results=n_results),
        "lessons": search_lessons(query, n_results=n_results),
    }
