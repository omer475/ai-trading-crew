"""
Automated end-to-end long-term investment pipeline.

Runs a 5-stage process:
  1. Market regime detection (adjust strategy to conditions)
  2. Full universe scan (300+ tickers, filter to top 30)
  3. AI deep analysis with 5 key agents (condensed from 50)
  4. Final ranking and recommendation
  5. Report generation (HTML + JSON + terminal)

Usage:
    python pipeline.py                    # Full run
    python pipeline.py --market lse       # LSE only
    python pipeline.py --market us        # US only
    python pipeline.py --skip-ai          # Scanner only, no AI analysis (fast)
    python pipeline.py --top 5            # Show top 5 only
"""

import asyncio
import argparse
import json
import logging
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger("pipeline")

# ---------------------------------------------------------------------------
# Project imports
# ---------------------------------------------------------------------------
from tools.regime_detector import detect_regime, RegimeResult, MarketRegime
from tools.scanner import scan, _fetch_histories, _fetch_infos, _analyze_stock, _score_opportunity
from agents.personas.definitions import PERSONAS
from agents.head_coach import HEAD_COACH_PROMPT
from config.llm_config import get_decision_client, get_analysis_client, get_manager_client

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SCAN_INTERVAL_WEEKS = 2
MAX_POSITIONS = 8               # for an under-10K portfolio
MIN_CONFIDENCE = 0.65
HOLDING_PERIOD_MONTHS = (3, 12) # long-term focus

REPORTS_DIR = Path(__file__).resolve().parent / "reports"

# The 5 condensed agents used for quick AI analysis
PIPELINE_AGENTS = {
    "fa_value_investor":     "Warren",     # Value perspective
    "fa_growth_analyst":     "Catherine",   # Growth perspective
    "risk_portfolio":        "Viktor",      # Risk assessment
    "risk_devils_advocate":  "Mei",         # Bear case / devil's advocate
}
HEAD_COACH_ID = "head_coach"

# ---------------------------------------------------------------------------
# Universe — try to import from tools/universe.py, fallback to built-in
# ---------------------------------------------------------------------------
def _get_universe(market: Optional[str] = None) -> list[str]:
    """Return the stock universe for scanning.

    Attempts to import ``tools.universe.get_universe``; if it does not exist
    falls back to a hard-coded universe of ~300 tickers covering US and LSE.
    """
    try:
        from tools.universe import get_universe
        if market:
            return get_universe(market)
        return get_universe("all")
    except (ImportError, ModuleNotFoundError):
        logger.info("tools/universe.py not found — using built-in universe")

    # --- Built-in fallback universe ---
    us_tickers = [
        # Mega / large cap
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B",
        "JPM", "JNJ", "V", "UNH", "HD", "PG", "MA", "DIS", "NFLX",
        "ADBE", "CRM", "INTC", "AMD", "QCOM", "TXN", "COST", "WMT", "MRK",
        "PFE", "ABBV", "LLY", "TMO", "ABT", "DHR", "AVGO", "CSCO", "ACN",
        "PEP", "KO", "MCD", "NKE", "LIN", "NEE", "UNP", "LOW", "MDT",
        "HON", "AMGN", "IBM", "GE", "CAT", "BA", "RTX", "GS", "BLK",
        "ISRG", "SPGI", "AXP", "SYK", "GILD", "MDLZ", "CVX", "XOM",
        "COP", "EOG", "SLB", "DE", "CI", "ELV", "CB", "SO",
        "DUK", "MO", "PM", "BMY", "VRTX", "REGN", "ZTS", "SCHW",
        "MS", "C", "USB", "PNC", "TFC", "ADP", "CME", "ICE", "MCO",
        "APD", "SHW", "ECL", "NSC", "ITW", "EMR", "FDX", "UPS",
        "ORCL", "NOW", "PANW", "CRWD", "UBER",
        # Mid cap value / growth
        "PYPL", "SQ", "COIN", "PLTR", "MRVL", "ABNB", "RIVN", "SNOW",
        "DDOG", "ZS", "NET", "OKTA", "MDB", "TTD", "SHOP",
        "ENPH", "SEDG", "FSLR", "PLUG", "CHPT",
        "MRNA", "BNTX", "CRSP", "EDIT", "NTLA",
        "SOFI", "AFRM", "HOOD", "RBLX", "U",
        "ROKU", "PINS", "SNAP", "SPOT", "LYFT",
        "DASH", "GRAB", "SE", "MELI", "NU",
        "LULU", "DECK", "ON", "SMCI", "ARM",
        # Dividend aristocrats / value
        "JNJ", "PG", "KO", "PEP", "MMM", "EMR", "SWK", "ABT",
        "T", "VZ", "O", "MAIN", "STAG", "ADC",
        "SPG", "PSA", "DLR", "EQIX", "AMT",
        "WBA", "CVS", "HUM", "CNC",
        "TGT", "DLTR", "DG", "FIVE",
        "F", "GM", "TM",
        "GD", "LMT", "NOC",
        "WM", "RSG", "VRSK",
    ]

    lse_tickers = [
        # FTSE 100
        "SHEL.L", "AZN.L", "HSBA.L", "ULVR.L", "BP.L", "GSK.L", "RIO.L",
        "DGE.L", "LSEG.L", "REL.L", "AAL.L", "GLEN.L", "BATS.L", "IMB.L",
        "NG.L", "SSE.L", "CRH.L", "AHT.L", "ANTO.L", "WPP.L",
        "LLOY.L", "BARC.L", "NWG.L", "STAN.L", "ABDN.L",
        "TSCO.L", "SBRY.L", "MKS.L", "JD.L",
        "RR.L", "BA.L", "SMIN.L",
        "VOD.L", "BT-A.L", "AUTO.L", "SGE.L",
        "PSN.L", "BNZL.L", "EXPN.L", "III.L",
        "RKT.L", "HLMA.L", "SMDS.L", "MNDI.L",
        "AVV.L", "BRBY.L", "KGF.L", "LAND.L",
        # FTSE 250 selection
        "DARK.L", "GAW.L", "BDEV.L", "TW.L", "FDEV.L",
        "DPLM.L", "WEIR.L", "IMI.L", "RTO.L",
        "PHNX.L", "LGEN.L", "JMAT.L",
    ]

    # Remove duplicates
    us_tickers = list(dict.fromkeys(us_tickers))
    lse_tickers = list(dict.fromkeys(lse_tickers))

    if market == "lse":
        return lse_tickers
    elif market == "us":
        return us_tickers
    else:
        return us_tickers + lse_tickers


# ---------------------------------------------------------------------------
# Data classes for pipeline results
# ---------------------------------------------------------------------------
@dataclass
class AgentVerdict:
    """A single agent's quick assessment of a stock."""
    agent_id: str
    agent_name: str
    verdict: str        # BUY / WATCH / PASS
    confidence: int     # 0-100
    reasoning: str


@dataclass
class CandidateResult:
    """Full pipeline result for a single stock candidate."""
    rank: int
    symbol: str
    name: str
    price: float
    scanner_score: float
    ai_consensus_score: float
    combined_score: float
    verdict: str
    confidence: float
    buy_reason: str
    entry_low: float
    entry_high: float
    stop_loss: float
    target_price: float
    holding_period: str
    agent_verdicts: list[AgentVerdict] = field(default_factory=list)
    agents_agreed: list[str] = field(default_factory=list)
    agents_disagreed: list[str] = field(default_factory=list)
    scanner_signals: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = asdict(self)
        return d


# ---------------------------------------------------------------------------
# Stage 1: Market Regime
# ---------------------------------------------------------------------------
def stage_1_regime(verbose: bool = True) -> RegimeResult:
    """Detect the current market regime and return strategy adjustments."""
    print("\n" + "=" * 70)
    print("  STAGE 1: MARKET REGIME DETECTION")
    print("=" * 70)

    result = detect_regime(verbose=verbose)

    print(f"\n  Regime:     {result.regime.value}")
    print(f"  Score:      {result.composite_score:+.4f}")
    print(f"  Confidence: {result.confidence:.1%}")
    print(f"  Strategy:   {result.strategy['strategy']}")
    print(f"  Sizing:     {result.strategy['position_size_multiplier']}x")
    print(f"  Bias:       {result.strategy['sector_bias']}")
    print(f"\n  {result.strategy['description']}")
    print()

    return result


# ---------------------------------------------------------------------------
# Stage 2: Full Universe Scan
# ---------------------------------------------------------------------------
def _long_term_score(signals: dict, regime: MarketRegime) -> float:
    """Custom long-term scoring that emphasises fundamentals over technicals.

    Profiles covered:
      - Strong fundamentals (low P/E, margins, revenue growth)
      - Undervalued with catalysts
      - Consistent dividend growers (approximated via low volatility + value)
      - Growth at reasonable price (GARP)
    """
    score = 50.0

    # --- Fundamental Quality (max +30) ---
    pe = signals.get("pe_ratio")
    fwd_pe = signals.get("forward_pe")
    rev_growth = signals.get("revenue_growth")
    margins = signals.get("profit_margins")
    ptb = signals.get("price_to_book")

    # P/E: lower is better for value, but avoid negative earnings
    if pe is not None and 0 < pe <= 12:
        score += 10
    elif pe is not None and 12 < pe <= 18:
        score += 6
    elif pe is not None and 18 < pe <= 25:
        score += 2

    # Forward P/E discount relative to trailing (earnings growth expected)
    if pe is not None and fwd_pe is not None and pe > 0 and fwd_pe > 0:
        if fwd_pe < pe * 0.85:
            score += 5  # forward P/E is 15%+ lower = earnings acceleration

    # Revenue growth
    if rev_growth is not None:
        if rev_growth > 0.20:
            score += 8
        elif rev_growth > 0.10:
            score += 5
        elif rev_growth > 0.05:
            score += 3
        elif rev_growth < -0.05:
            score -= 5

    # Profit margins — quality indicator
    if margins is not None:
        if margins > 0.20:
            score += 5
        elif margins > 0.10:
            score += 3
        elif margins < 0:
            score -= 5

    # Price to book — deep value
    if ptb is not None:
        if 0 < ptb < 1.5:
            score += 5
        elif 1.5 <= ptb < 3.0:
            score += 2

    # --- Technical Health (max +15) ---
    if signals.get("above_sma_200"):
        score += 5   # above long-term trend
    if signals.get("above_sma_50"):
        score += 3   # above medium-term trend
    if signals.get("golden_cross"):
        score += 5   # major bullish signal

    rsi = signals.get("rsi", 50)
    # Favour stocks in the "healthy" RSI zone for long-term entries
    if 30 <= rsi <= 50:
        score += 4   # pulling back into value zone
    elif rsi < 30:
        score += 2   # oversold can be opportunity but risky

    # Penalize extremely overbought for long-term entry
    if rsi > 75:
        score -= 3

    # MACD bullish crossover is a plus
    if signals.get("macd_bullish_cross"):
        score += 3

    # --- Volume Confirmation (max +5) ---
    vol_ratio = signals.get("volume_ratio", 1.0)
    if vol_ratio >= 1.5:
        score += 3
    if signals.get("breakout_up"):
        score += 5

    # --- Divergence bonus ---
    if signals.get("rsi_bullish_divergence"):
        score += 6

    # Penalize bearish signals
    if signals.get("death_cross"):
        score -= 8
    if signals.get("breakdown"):
        score -= 5
    if signals.get("rsi_bearish_divergence"):
        score -= 3

    # --- Regime adjustments ---
    if regime in (MarketRegime.BEAR, MarketRegime.STRONG_BEAR):
        # In bear markets, heavily weight value and penalize growth
        if pe is not None and 0 < pe <= 15:
            score += 5
        if rev_growth is not None and rev_growth < 0:
            score -= 8
        if not signals.get("above_sma_200"):
            score -= 5
    elif regime == MarketRegime.STRONG_BULL:
        # In strong bull, give momentum a boost
        if signals.get("above_sma_50") and signals.get("above_sma_200"):
            score += 3
        if rev_growth is not None and rev_growth > 0.15:
            score += 3

    return round(max(0.0, min(100.0, score)), 1)


def stage_2_scan(universe: list[str],
                 regime: RegimeResult,
                 top_n: int = 30) -> list[dict]:
    """Scan the full universe and return the top N candidates by long-term score."""
    print("\n" + "=" * 70)
    print("  STAGE 2: FULL UNIVERSE SCAN")
    print(f"  Scanning {len(universe)} stocks for long-term opportunities...")
    print("=" * 70 + "\n")

    # Fetch data in batch
    logger.info("Downloading price history for %d symbols...", len(universe))
    histories = _fetch_histories(universe)
    logger.info("Fetching fundamental data...")
    infos = _fetch_infos(list(histories.keys()))

    results: list[dict] = []
    scanned = 0
    skipped = 0

    for sym in universe:
        hist = histories.get(sym)
        info = infos.get(sym, {})
        signals = _analyze_stock(sym, hist, info)
        if signals is None:
            skipped += 1
            continue

        # Use our custom long-term scoring
        signals["score"] = _long_term_score(signals, regime.regime)
        # Also keep the standard scanner score for reference
        signals["scanner_score_standard"] = _score_opportunity(signals)
        signals["company_name"] = info.get("shortName") or info.get("longName") or sym
        results.append(signals)
        scanned += 1

    # Sort by long-term score
    results.sort(key=lambda x: x["score"], reverse=True)

    print(f"  Scanned: {scanned} | Skipped (no data): {skipped}")
    print(f"  Top {min(top_n, len(results))} candidates selected\n")

    top = results[:top_n]
    for i, r in enumerate(top[:10], 1):
        name = r.get("company_name", r["symbol"])[:25]
        print(f"  {i:>3}. {r['symbol']:<8} {name:<26} "
              f"Score: {r['score']:5.1f}  "
              f"Price: ${r['price']:.2f}  "
              f"P/E: {r.get('pe_ratio', 'N/A')}  "
              f"RevGr: {r.get('revenue_growth', 'N/A')}")

    if len(top) > 10:
        print(f"  ... and {len(top) - 10} more candidates")

    return top


# ---------------------------------------------------------------------------
# Stage 3: AI Deep Analysis
# ---------------------------------------------------------------------------
def _make_safe_name(name: str) -> str:
    """Convert persona name to a valid Python identifier for AutoGen."""
    safe = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    safe = re.sub(r"_+", "_", safe).strip("_")
    return safe


def _build_stock_brief(candidate: dict) -> str:
    """Build a concise data brief about a stock for the AI agents."""
    sym = candidate["symbol"]
    name = candidate.get("company_name", sym)
    price = candidate["price"]

    lines = [
        f"STOCK: {name} ({sym})",
        f"Current Price: ${price:.2f}",
    ]

    # Fundamentals
    if candidate.get("pe_ratio"):
        lines.append(f"P/E Ratio: {candidate['pe_ratio']:.1f}")
    if candidate.get("forward_pe"):
        lines.append(f"Forward P/E: {candidate['forward_pe']:.1f}")
    if candidate.get("price_to_book"):
        lines.append(f"P/B Ratio: {candidate['price_to_book']:.2f}")
    if candidate.get("revenue_growth") is not None:
        lines.append(f"Revenue Growth: {candidate['revenue_growth']:.1%}")
    if candidate.get("profit_margins") is not None:
        lines.append(f"Profit Margins: {candidate['profit_margins']:.1%}")
    if candidate.get("market_cap"):
        mc = candidate["market_cap"]
        if mc >= 1e12:
            lines.append(f"Market Cap: ${mc/1e12:.1f}T")
        elif mc >= 1e9:
            lines.append(f"Market Cap: ${mc/1e9:.1f}B")
        else:
            lines.append(f"Market Cap: ${mc/1e6:.0f}M")

    # Technicals
    lines.append(f"RSI(14): {candidate.get('rsi', 'N/A')}")
    if candidate.get("sma_50"):
        lines.append(f"50-SMA: ${candidate['sma_50']:.2f} "
                      f"({'above' if candidate.get('above_sma_50') else 'below'})")
    if candidate.get("sma_200"):
        lines.append(f"200-SMA: ${candidate['sma_200']:.2f} "
                      f"({'above' if candidate.get('above_sma_200') else 'below'})")
    lines.append(f"Volume Ratio (vs 20d avg): {candidate.get('volume_ratio', 1.0):.1f}x")
    lines.append(f"Support: ${candidate.get('support', 0):.2f} | "
                 f"Resistance: ${candidate.get('resistance', 0):.2f}")
    lines.append(f"ATR: ${candidate.get('atr', 0):.2f} ({candidate.get('atr_pct', 0):.1f}%)")
    lines.append(f"1d Change: {candidate.get('pct_change_1d', 0):+.2f}%")
    lines.append(f"5d Change: {candidate.get('pct_change_5d', 0):+.2f}%")
    lines.append(f"Scanner Score: {candidate['score']:.1f}/100")

    # Signals
    flags = []
    if candidate.get("golden_cross"):
        flags.append("GOLDEN CROSS")
    if candidate.get("death_cross"):
        flags.append("DEATH CROSS")
    if candidate.get("macd_bullish_cross"):
        flags.append("MACD BULLISH CROSSOVER")
    if candidate.get("breakout_up"):
        flags.append("BREAKOUT ABOVE RESISTANCE")
    if candidate.get("rsi_bullish_divergence"):
        flags.append("RSI BULLISH DIVERGENCE")
    if candidate.get("volume_spike"):
        flags.append("VOLUME SPIKE")
    if flags:
        lines.append(f"Signals: {', '.join(flags)}")

    return "\n".join(lines)


def _parse_agent_response(text: str, agent_id: str, agent_name: str) -> AgentVerdict:
    """Extract verdict, confidence, and reasoning from an agent's response."""
    text_upper = text.upper()

    # Determine verdict
    if "BUY" in text_upper and "PASS" not in text_upper[:50]:
        verdict = "BUY"
    elif "WATCH" in text_upper:
        verdict = "WATCH"
    else:
        verdict = "PASS"

    # Extract confidence (look for patterns like "confidence: 75" or "75%")
    confidence = 50  # default
    import re as _re
    conf_patterns = [
        r'confidence[:\s]*(\d{1,3})\s*[%/]?',
        r'(\d{1,3})\s*%\s*confiden',
        r'(\d{1,3})/100',
    ]
    for pat in conf_patterns:
        match = _re.search(pat, text, _re.IGNORECASE)
        if match:
            val = int(match.group(1))
            if 0 <= val <= 100:
                confidence = val
                break

    # Take the first 2-3 sentences as reasoning
    sentences = text.replace("\n", " ").split(".")
    reasoning = ". ".join(s.strip() for s in sentences[:3] if s.strip())
    if len(reasoning) > 300:
        reasoning = reasoning[:297] + "..."

    return AgentVerdict(
        agent_id=agent_id,
        agent_name=agent_name,
        verdict=verdict,
        confidence=confidence,
        reasoning=reasoning,
    )


async def _analyze_single_stock(candidate: dict,
                                 regime: RegimeResult) -> list[AgentVerdict]:
    """Run the 5 key agents on a single stock using a SelectorGroupChat."""
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.teams import SelectorGroupChat
    from autogen_agentchat.conditions import MaxMessageTermination

    decision_client = get_decision_client()
    analysis_client = get_analysis_client()
    manager_client = get_manager_client()

    brief = _build_stock_brief(candidate)
    regime_context = (
        f"Current market regime: {regime.regime.value} "
        f"(score {regime.composite_score:+.3f}, confidence {regime.confidence:.0%}). "
        f"Strategy: {regime.strategy['description']}"
    )

    # Create the 4 specialist agents
    agents = []
    for pid, short_name in PIPELINE_AGENTS.items():
        persona = PERSONAS[pid]
        # Decision-tier agents get Claude, others get DeepSeek
        is_decision = pid in ("risk_portfolio", "risk_devils_advocate", "fa_value_investor")
        client = decision_client if is_decision else analysis_client

        long_term_addendum = (
            "\n\nIMPORTANT: This is for LONG-TERM investing (3-12 month holding period). "
            "Focus on fundamentals, competitive moats, and long-term value creation. "
            "Provide your verdict as exactly one of: BUY / WATCH / PASS "
            "with a confidence level 0-100. Be concise (under 150 words)."
        )
        agent = AssistantAgent(
            name=_make_safe_name(persona["name"]),
            system_message=persona["system_message"] + long_term_addendum,
            description=f"{persona['name']} - {persona['team']} team",
            model_client=client,
        )
        agents.append((pid, short_name, agent))

    # Create Head Coach
    coach_addendum = (
        "\n\nYou are reviewing a LONG-TERM investment candidate (3-12 month hold). "
        "After hearing from the specialists, synthesize their views. "
        "Give your final verdict: BUY / WATCH / PASS with confidence 0-100. "
        "Briefly state the bull case, bear case, and your decision. Be concise."
    )
    coach = AssistantAgent(
        name="Head_Coach",
        system_message=HEAD_COACH_PROMPT + coach_addendum,
        description="Head Coach - makes final trading decisions",
        model_client=decision_client,
    )

    all_participants = [a for _, _, a in agents] + [coach]
    termination = MaxMessageTermination(max_messages=8)

    team = SelectorGroupChat(
        participants=all_participants,
        model_client=manager_client,
        termination_condition=termination,
    )

    task = (
        f"Evaluate this stock for a LONG-TERM investment (3-12 months).\n\n"
        f"{regime_context}\n\n"
        f"{brief}\n\n"
        f"Each specialist: give your quick verdict (BUY/WATCH/PASS) with "
        f"confidence 0-100 and brief reasoning. Head Coach: synthesize and decide."
    )

    # Collect responses
    verdicts: list[AgentVerdict] = []
    agent_name_map = {_make_safe_name(PERSONAS[pid]["name"]): (pid, sn) for pid, sn in PIPELINE_AGENTS.items()}
    agent_name_map["Head_Coach"] = (HEAD_COACH_ID, "Head Coach")

    try:
        async for message in team.run_stream(task=task):
            if hasattr(message, "source") and hasattr(message, "content"):
                source = message.source
                content = message.content or ""
                if source in agent_name_map and content.strip():
                    pid, sn = agent_name_map[source]
                    verdict = _parse_agent_response(content, pid, sn)
                    verdicts.append(verdict)
                    logger.debug("  [%s] %s (conf=%d): %s",
                                 sn, verdict.verdict, verdict.confidence,
                                 verdict.reasoning[:80])
    except Exception as exc:
        logger.error("AI analysis failed for %s: %s", candidate["symbol"], exc)

    return verdicts


async def stage_3_ai_analysis(candidates: list[dict],
                               regime: RegimeResult,
                               max_candidates: int = 20) -> dict[str, list[AgentVerdict]]:
    """Run AI agents on the top candidates. Returns symbol -> verdicts mapping."""
    print("\n" + "=" * 70)
    print("  STAGE 3: AI DEEP ANALYSIS")
    print(f"  Running 5 key agents on top {min(max_candidates, len(candidates))} candidates...")
    print(f"  Agents: Warren (Value), Catherine (Growth), Viktor (Risk),")
    print(f"          Mei (Devil's Advocate), Head Coach")
    print("=" * 70 + "\n")

    analysis_results: dict[str, list[AgentVerdict]] = {}
    batch = candidates[:max_candidates]

    for i, candidate in enumerate(batch, 1):
        sym = candidate["symbol"]
        name = candidate.get("company_name", sym)
        print(f"  [{i}/{len(batch)}] Analyzing {sym} ({name})...", end="", flush=True)

        try:
            verdicts = await _analyze_single_stock(candidate, regime)
            analysis_results[sym] = verdicts

            # Quick summary
            buy_count = sum(1 for v in verdicts if v.verdict == "BUY")
            avg_conf = sum(v.confidence for v in verdicts) / len(verdicts) if verdicts else 0
            print(f" {buy_count}/{len(verdicts)} BUY, avg conf {avg_conf:.0f}")
        except Exception as exc:
            logger.error("Failed to analyze %s: %s", sym, exc)
            analysis_results[sym] = []
            print(f" ERROR: {exc}")

    return analysis_results


# ---------------------------------------------------------------------------
# Stage 4: Final Rankings
# ---------------------------------------------------------------------------
def stage_4_rankings(candidates: list[dict],
                     ai_results: Optional[dict[str, list[AgentVerdict]]],
                     regime: RegimeResult,
                     top_n: int = 10) -> list[CandidateResult]:
    """Combine scanner + AI scores and produce final ranked recommendations."""
    print("\n" + "=" * 70)
    print("  STAGE 4: FINAL RANKINGS")
    print("=" * 70 + "\n")

    results: list[CandidateResult] = []

    for candidate in candidates:
        sym = candidate["symbol"]
        price = candidate["price"]
        name = candidate.get("company_name", sym)
        scanner_score = candidate["score"]

        # AI consensus score
        verdicts = (ai_results or {}).get(sym, [])
        if verdicts:
            # Score: BUY=100, WATCH=50, PASS=0, weighted by confidence
            verdict_scores = []
            for v in verdicts:
                if v.verdict == "BUY":
                    vs = 100
                elif v.verdict == "WATCH":
                    vs = 50
                else:
                    vs = 0
                verdict_scores.append(vs * (v.confidence / 100.0))
            ai_score = sum(verdict_scores) / len(verdict_scores) if verdict_scores else 0
        else:
            ai_score = 50.0  # neutral if no AI analysis

        # Combined score: 40% scanner + 60% AI (when available)
        if ai_results is not None and sym in ai_results:
            combined = scanner_score * 0.4 + ai_score * 0.6
        else:
            combined = scanner_score

        # Determine overall verdict from AI
        if verdicts:
            buy_count = sum(1 for v in verdicts if v.verdict == "BUY")
            watch_count = sum(1 for v in verdicts if v.verdict == "WATCH")
            pass_count = sum(1 for v in verdicts if v.verdict == "PASS")
            if buy_count > pass_count and buy_count >= watch_count:
                overall_verdict = "BUY"
            elif watch_count > pass_count:
                overall_verdict = "WATCH"
            else:
                overall_verdict = "PASS"
            avg_confidence = sum(v.confidence for v in verdicts) / len(verdicts) / 100.0
        else:
            overall_verdict = "SCAN_ONLY"
            avg_confidence = scanner_score / 100.0

        # Price levels
        atr = candidate.get("atr", price * 0.02)
        support = candidate.get("support", price * 0.95)
        resistance = candidate.get("resistance", price * 1.05)

        entry_low = round(max(support, price - atr), 2)
        entry_high = round(price + atr * 0.5, 2)
        stop_loss_val = round(max(support - atr, price * 0.93), 2)

        # Target: use regime-adjusted multiplier
        regime_mult = regime.strategy.get("position_size_multiplier", 1.0)
        if regime.regime in (MarketRegime.STRONG_BULL, MarketRegime.BULL):
            target_mult = 1.20 + (regime_mult - 1.0) * 0.1
        elif regime.regime in (MarketRegime.BEAR, MarketRegime.STRONG_BEAR):
            target_mult = 1.08
        else:
            target_mult = 1.15
        target_price = round(price * target_mult, 2)

        # Holding period estimate based on regime + stock profile
        if regime.regime in (MarketRegime.STRONG_BULL, MarketRegime.BULL):
            holding = "3-6 months"
        elif regime.regime in (MarketRegime.BEAR, MarketRegime.STRONG_BEAR):
            holding = "6-12 months (accumulate slowly)"
        else:
            holding = "4-8 months"

        # Build professional investment thesis
        pe = candidate.get("pe_ratio")
        fwd_pe = candidate.get("forward_pe")
        rev_gr = candidate.get("revenue_growth")
        margins = candidate.get("profit_margins")
        pb = candidate.get("price_to_book")
        rsi_val = candidate.get("rsi", 50)
        above_200 = candidate.get("above_sma_200", False)
        above_50 = candidate.get("above_sma_50", False)
        vol_ratio = candidate.get("volume_ratio", 1.0)
        atr_pct = candidate.get("atr_pct", 0)

        thesis_parts = []

        # Valuation thesis
        val_points = []
        if pe and 0 < pe <= 20:
            val_points.append(f"trailing P/E of {pe:.1f}x")
        if fwd_pe and 0 < fwd_pe < (pe or 999):
            val_points.append(f"forward P/E of {fwd_pe:.1f}x (indicating earnings acceleration)")
        if pb and 0 < pb <= 2:
            val_points.append(f"P/B of {pb:.2f}x")
        if val_points:
            thesis_parts.append(f"Valuation: Trading at {', '.join(val_points)}, well below sector averages. This suggests the market is underpricing the company's earnings power and asset base.")

        # Growth thesis
        growth_points = []
        if rev_gr and rev_gr > 0.05:
            growth_points.append(f"revenue growing at {rev_gr:.0%} year-over-year")
        if margins and margins > 0.1:
            growth_points.append(f"profit margins of {margins:.0%} demonstrating operational efficiency")
        if growth_points:
            thesis_parts.append(f"Fundamentals: {', '.join(growth_points).capitalize()}. The combination of growth and profitability indicates a business with sustainable competitive advantages and strong pricing power.")

        # Technical thesis
        tech_points = []
        if above_200:
            tech_points.append("price remains above the 200-day moving average, confirming the long-term structural uptrend is intact")
        if above_50:
            tech_points.append("holding above the 50-day SMA showing medium-term strength")
        elif not above_50 and above_200:
            tech_points.append("pulled back below the 50-day SMA while the 200-day uptrend remains intact — a potential mean-reversion entry opportunity")
        if candidate.get("golden_cross"):
            tech_points.append("a golden cross (50-day crossing above 200-day) has formed, historically a strong bullish signal")
        if rsi_val < 35:
            tech_points.append(f"RSI at {rsi_val:.0f} indicates oversold conditions — contrarian buying opportunity")
        if candidate.get("rsi_bullish_divergence"):
            tech_points.append("RSI bullish divergence detected, suggesting downside momentum is fading while the price prepares for a reversal")
        if candidate.get("macd_bullish_cross"):
            tech_points.append("MACD bullish crossover confirms shifting momentum to the upside")
        if tech_points:
            thesis_parts.append(f"Technical picture: {tech_points[0].capitalize()}{', and ' + ', '.join(tech_points[1:]) if len(tech_points) > 1 else ''}.")

        # Risk/reward summary
        if entry_low and stop_loss_val and target_price:
            potential_upside = ((target_price - price) / price) * 100
            potential_downside = ((price - stop_loss_val) / price) * 100
            rr_ratio = potential_upside / potential_downside if potential_downside > 0 else 0
            thesis_parts.append(
                f"Risk/reward: Entry zone ${entry_low:.2f}–${entry_high:.2f} with a target of ${target_price:.2f} "
                f"(+{potential_upside:.1f}% upside) against a stop loss at ${stop_loss_val:.2f} "
                f"(-{potential_downside:.1f}% risk), yielding a {rr_ratio:.1f}:1 reward-to-risk ratio. "
                f"Recommended holding period: {holding}."
            )

        if not thesis_parts:
            thesis_parts.append(f"High composite score ({scanner_score:.1f}/100) across multiple fundamental and technical factors.")

        buy_reason = " ".join(thesis_parts)

        # Agent agreement
        agreed = [v.agent_name for v in verdicts if v.verdict == "BUY"]
        disagreed = [v.agent_name for v in verdicts if v.verdict == "PASS"]

        result = CandidateResult(
            rank=0,  # will be set after sorting
            symbol=sym,
            name=name,
            price=price,
            scanner_score=scanner_score,
            ai_consensus_score=round(ai_score, 1),
            combined_score=round(combined, 1),
            verdict=overall_verdict,
            confidence=round(avg_confidence, 2),
            buy_reason=buy_reason,
            entry_low=entry_low,
            entry_high=entry_high,
            stop_loss=stop_loss_val,
            target_price=target_price,
            holding_period=holding,
            agent_verdicts=verdicts,
            agents_agreed=agreed,
            agents_disagreed=disagreed,
            scanner_signals=candidate,
        )
        results.append(result)

    # Sort by combined score
    results.sort(key=lambda x: x.combined_score, reverse=True)

    # Filter by minimum confidence
    results = [r for r in results if r.confidence >= MIN_CONFIDENCE or r.verdict == "SCAN_ONLY"]

    # Save all ranked candidates before truncating
    all_ranked = list(results)
    for i, r in enumerate(all_ranked, 1):
        r.rank = i

    # Limit to top_n for display/recommendations
    results = results[:top_n]

    # Print summary
    print(f"  {'Rank':<5} {'Symbol':<8} {'Name':<25} {'Score':>6} {'Verdict':<10} "
          f"{'Conf':>5} {'Price':>8} {'Target':>8}")
    print("  " + "-" * 85)
    for r in results:
        print(f"  {r.rank:<5} {r.symbol:<8} {r.name[:24]:<25} {r.combined_score:>5.1f} "
              f"{r.verdict:<10} {r.confidence:>4.0%} ${r.price:>7.2f} ${r.target_price:>7.2f}")

    return results


# ---------------------------------------------------------------------------
# Stage 5: Report Generation
# ---------------------------------------------------------------------------
def _generate_html_report(results: list[CandidateResult],
                          regime: RegimeResult,
                          scan_date: str) -> str:
    """Generate a detailed HTML report."""
    regime_colors = {
        "STRONG_BULL": "#2ecc71",
        "BULL": "#27ae60",
        "NEUTRAL": "#f39c12",
        "BEAR": "#e74c3c",
        "STRONG_BEAR": "#c0392b",
        "VOLATILE": "#9b59b6",
    }
    regime_color = regime_colors.get(regime.regime.value, "#95a5a6")

    verdict_colors = {
        "BUY": "#27ae60",
        "WATCH": "#f39c12",
        "PASS": "#e74c3c",
        "SCAN_ONLY": "#3498db",
    }

    rows_html = ""
    for r in results:
        vc = verdict_colors.get(r.verdict, "#95a5a6")
        agreed_str = ", ".join(r.agents_agreed) if r.agents_agreed else "-"
        disagreed_str = ", ".join(r.agents_disagreed) if r.agents_disagreed else "-"
        rows_html += f"""
        <tr>
            <td><strong>{r.rank}</strong></td>
            <td><strong>{r.symbol}</strong><br><small>{r.name}</small></td>
            <td>${r.price:.2f}</td>
            <td>{r.scanner_score:.1f}</td>
            <td>{r.ai_consensus_score:.1f}</td>
            <td><strong>{r.combined_score:.1f}</strong></td>
            <td style="color:{vc};font-weight:bold">{r.verdict}</td>
            <td>{r.confidence:.0%}</td>
            <td>${r.entry_low:.2f} - ${r.entry_high:.2f}</td>
            <td>${r.stop_loss:.2f}</td>
            <td>${r.target_price:.2f}</td>
            <td>{r.holding_period}</td>
            <td><small>{r.buy_reason[:120]}</small></td>
            <td style="color:green"><small>{agreed_str}</small></td>
            <td style="color:red"><small>{disagreed_str}</small></td>
        </tr>"""

    # Detail cards for top picks
    detail_cards = ""
    for r in results[:5]:
        agent_lines = ""
        for v in r.agent_verdicts:
            avc = verdict_colors.get(v.verdict, "#95a5a6")
            agent_lines += (
                f'<div style="margin:4px 0;padding:6px;background:#f8f9fa;border-radius:4px">'
                f'<strong>{v.agent_name}</strong>: '
                f'<span style="color:{avc};font-weight:bold">{v.verdict}</span> '
                f'(conf: {v.confidence}%) '
                f'<br><small>{v.reasoning[:200]}</small></div>'
            )
        if not agent_lines:
            agent_lines = "<p><em>No AI analysis (scanner-only mode)</em></p>"

        detail_cards += f"""
        <div style="border:1px solid #ddd;border-radius:8px;padding:16px;margin:12px 0;
                     background:#fff;box-shadow:0 1px 3px rgba(0,0,0,0.1)">
            <h3>#{r.rank} {r.symbol} - {r.name}</h3>
            <table style="width:100%;margin:8px 0">
                <tr>
                    <td><strong>Price:</strong> ${r.price:.2f}</td>
                    <td><strong>Entry Range:</strong> ${r.entry_low:.2f} - ${r.entry_high:.2f}</td>
                    <td><strong>Stop Loss:</strong> ${r.stop_loss:.2f}</td>
                    <td><strong>Target:</strong> ${r.target_price:.2f}</td>
                </tr>
                <tr>
                    <td><strong>Scanner Score:</strong> {r.scanner_score:.1f}</td>
                    <td><strong>AI Score:</strong> {r.ai_consensus_score:.1f}</td>
                    <td><strong>Combined:</strong> {r.combined_score:.1f}</td>
                    <td><strong>Holding:</strong> {r.holding_period}</td>
                </tr>
            </table>
            <p><strong>Why Buy:</strong> {r.buy_reason}</p>
            <h4>Agent Verdicts:</h4>
            {agent_lines}
        </div>"""

    # Signal summary for regime
    signal_rows = ""
    for sig in regime.signals:
        bar_width = abs(sig.score) * 100
        bar_color = "#27ae60" if sig.score > 0 else "#e74c3c"
        bar_dir = "right" if sig.score > 0 else "left"
        signal_rows += f"""
        <tr>
            <td>{sig.name}</td>
            <td>{sig.score:+.3f}</td>
            <td>
                <div style="width:200px;height:12px;background:#eee;border-radius:6px;position:relative">
                    <div style="width:{bar_width:.0f}%;height:100%;background:{bar_color};
                                border-radius:6px;float:{bar_dir}"></div>
                </div>
            </td>
            <td><small>{sig.interpretation}</small></td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Investment Scan Report - {scan_date}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
               max-width: 1400px; margin: 0 auto; padding: 20px; background: #f5f6fa; color: #2c3e50; }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 10px 0; background: #fff;
                 border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        th {{ background: #34495e; color: white; padding: 10px 8px; text-align: left; font-size: 13px; }}
        td {{ padding: 8px; border-bottom: 1px solid #ecf0f1; font-size: 13px; }}
        tr:hover {{ background: #f8f9fa; }}
        .regime-badge {{ display: inline-block; padding: 8px 16px; border-radius: 20px;
                         color: white; font-weight: bold; font-size: 18px; }}
        .config {{ background: #fff; padding: 15px; border-radius: 8px; margin: 10px 0;
                   box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
    <h1>AI Trading Crew - Long-Term Investment Scan</h1>
    <p><strong>Date:</strong> {scan_date} | <strong>Pipeline:</strong> 5-Stage Automated Scan
       | <strong>Focus:</strong> Long-term (3-12 months)</p>

    <h2>Market Regime</h2>
    <div class="config">
        <span class="regime-badge" style="background:{regime_color}">{regime.regime.value}</span>
        <p>Composite Score: {regime.composite_score:+.4f} | Confidence: {regime.confidence:.1%}</p>
        <p><strong>Strategy:</strong> {regime.strategy['description']}</p>
        <p>Position sizing: {regime.strategy['position_size_multiplier']}x |
           Sector bias: {regime.strategy['sector_bias']} |
           Hedging: {regime.strategy['hedging']}</p>
    </div>

    <h3>Regime Signals</h3>
    <table>
        <tr><th>Signal</th><th>Score</th><th>Bar</th><th>Detail</th></tr>
        {signal_rows}
    </table>

    <h2>Top Investment Picks</h2>
    <table>
        <tr>
            <th>#</th><th>Stock</th><th>Price</th><th>Scan</th><th>AI</th>
            <th>Combined</th><th>Verdict</th><th>Conf</th><th>Entry Range</th>
            <th>Stop</th><th>Target</th><th>Hold</th><th>Reason</th>
            <th>Agreed</th><th>Disagreed</th>
        </tr>
        {rows_html}
    </table>

    <h2>Detailed Analysis - Top 5</h2>
    {detail_cards}

    <div class="config" style="margin-top:30px">
        <h3>Pipeline Configuration</h3>
        <p>Scan Interval: {SCAN_INTERVAL_WEEKS} weeks |
           Max Positions: {MAX_POSITIONS} |
           Min Confidence: {MIN_CONFIDENCE:.0%} |
           Holding Period: {HOLDING_PERIOD_MONTHS[0]}-{HOLDING_PERIOD_MONTHS[1]} months</p>
        <p><small>Generated by AI Trading Crew Pipeline v1.0</small></p>
    </div>
</body>
</html>"""
    return html


def stage_5_reports(results: list[CandidateResult],
                    regime: RegimeResult) -> tuple[Path, Path]:
    """Generate HTML and JSON reports, print terminal summary."""
    print("\n" + "=" * 70)
    print("  STAGE 5: REPORT GENERATION")
    print("=" * 70 + "\n")

    scan_date = datetime.now().strftime("%Y-%m-%d")
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # --- HTML Report ---
    html_path = REPORTS_DIR / f"{scan_date}_scan.html"
    html_content = _generate_html_report(results, regime, scan_date)
    html_path.write_text(html_content, encoding="utf-8")
    print(f"  HTML report saved: {html_path}")

    # --- JSON Summary ---
    json_path = REPORTS_DIR / f"{scan_date}_scan.json"
    json_data = {
        "scan_date": scan_date,
        "regime": regime.to_dict(),
        "config": {
            "scan_interval_weeks": SCAN_INTERVAL_WEEKS,
            "max_positions": MAX_POSITIONS,
            "min_confidence": MIN_CONFIDENCE,
            "holding_period_months": list(HOLDING_PERIOD_MONTHS),
        },
        "picks": [r.to_dict() for r in results],
        "all_candidates": [r.to_dict() for r in all_ranked] if 'all_ranked' in dir() else [r.to_dict() for r in results],
        "total_candidates_scanned": len(results),
        "stocks_scanned": stocks_scanned if 'stocks_scanned' in dir() else len(results),
    }
    json_path.write_text(json.dumps(json_data, indent=2, default=str), encoding="utf-8")
    print(f"  JSON report saved: {json_path}")

    # --- Terminal Summary ---
    print(f"\n{'=' * 70}")
    print(f"  FINAL RECOMMENDATIONS - {scan_date}")
    print(f"  Market Regime: {regime.regime.value} | Strategy: {regime.strategy['strategy']}")
    print(f"{'=' * 70}\n")

    for r in results:
        conf_bar = "#" * int(r.confidence * 20)
        conf_empty = "-" * (20 - int(r.confidence * 20))
        print(f"  #{r.rank} {r.symbol} ({r.name})")
        print(f"     Verdict: {r.verdict} | Confidence: [{conf_bar}{conf_empty}] {r.confidence:.0%}")
        print(f"     Price: ${r.price:.2f} | Entry: ${r.entry_low:.2f}-${r.entry_high:.2f} "
              f"| Stop: ${r.stop_loss:.2f} | Target: ${r.target_price:.2f}")
        print(f"     Hold: {r.holding_period} | Score: {r.combined_score:.1f} "
              f"(scan={r.scanner_score:.1f}, ai={r.ai_consensus_score:.1f})")
        print(f"     Reason: {r.buy_reason[:100]}")
        if r.agents_agreed:
            print(f"     Agreed: {', '.join(r.agents_agreed)}")
        if r.agents_disagreed:
            print(f"     Disagreed: {', '.join(r.agents_disagreed)}")
        print()

    return html_path, json_path


# ---------------------------------------------------------------------------
# Main Pipeline Orchestrator
# ---------------------------------------------------------------------------
async def run_pipeline(market: Optional[str] = None,
                       skip_ai: bool = False,
                       top_n: int = 10):
    """Execute the full 5-stage investment pipeline."""
    start_time = datetime.now()

    print("\n" + "#" * 70)
    print("#" + " " * 68 + "#")
    print("#    AI TRADING CREW — LONG-TERM INVESTMENT PIPELINE" + " " * 17 + "#")
    print("#" + " " * 68 + "#")
    print("#" * 70)
    print(f"\n  Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Market:  {market or 'all (US + LSE)'}")
    print(f"  Mode:    {'Scanner only (--skip-ai)' if skip_ai else 'Full (Scanner + AI Analysis)'}")
    print(f"  Top N:   {top_n}")
    print(f"  Config:  Max positions={MAX_POSITIONS}, Min confidence={MIN_CONFIDENCE:.0%}")
    print(f"  Focus:   Long-term ({HOLDING_PERIOD_MONTHS[0]}-{HOLDING_PERIOD_MONTHS[1]} months)")

    # STAGE 1: Market Regime
    regime = stage_1_regime()

    # STAGE 2: Full Universe Scan
    universe = _get_universe(market)
    # Adjust number of candidates based on regime
    scan_top_n = 30
    if regime.regime in (MarketRegime.BEAR, MarketRegime.STRONG_BEAR):
        scan_top_n = 20  # be more selective in bear markets
        print("\n  [Regime adjustment] Reducing candidate pool — bear market detected")

    candidates = stage_2_scan(universe, regime, top_n=scan_top_n)

    if not candidates:
        print("\n  No candidates found matching criteria. Exiting.")
        return

    # STAGE 3: AI Deep Analysis (optional)
    ai_results = None
    if not skip_ai:
        max_ai = min(20, len(candidates))
        ai_results = await stage_3_ai_analysis(candidates, regime, max_candidates=max_ai)
    else:
        print("\n  [--skip-ai] Skipping AI analysis stage")

    # STAGE 4: Final Rankings
    final = stage_4_rankings(candidates, ai_results, regime, top_n=top_n)

    if not final:
        print("\n  No stocks passed the confidence threshold. Try lowering --min-confidence.")
        return

    # STAGE 5: Reports
    html_path, json_path = stage_5_reports(final, regime)

    elapsed = datetime.now() - start_time
    print(f"\n{'=' * 70}")
    print(f"  Pipeline complete in {elapsed.total_seconds():.1f}s")
    print(f"  HTML: {html_path}")
    print(f"  JSON: {json_path}")
    print(f"  Next scan recommended: {SCAN_INTERVAL_WEEKS} weeks from now")
    print(f"{'=' * 70}\n")


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="AI Trading Crew — Long-Term Investment Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pipeline.py                    # Full run (US + LSE, with AI)
  python pipeline.py --market lse       # LSE stocks only
  python pipeline.py --market us        # US stocks only
  python pipeline.py --skip-ai          # Scanner only, no AI (fast)
  python pipeline.py --top 5            # Show top 5 picks only
        """,
    )
    parser.add_argument(
        "--market", type=str, choices=["lse", "us"],
        default=None, help="Market to scan: 'lse' or 'us' (default: all)",
    )
    parser.add_argument(
        "--skip-ai", action="store_true",
        help="Skip AI agent analysis (scanner only — much faster)",
    )
    parser.add_argument(
        "--top", type=int, default=10,
        help="Number of top picks to show (default: 10)",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    asyncio.run(run_pipeline(
        market=args.market,
        skip_ai=args.skip_ai,
        top_n=args.top,
    ))


if __name__ == "__main__":
    main()
