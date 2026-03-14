"""News aggregation and sentiment analysis tool for the trading crew.

Pulls news from free sources (yfinance, RSS feeds, SEC EDGAR) and scores
each item for sentiment.  Provides per-stock and market-wide sentiment
summaries together with upcoming-event and insider-activity helpers.
"""

import re
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional

import yfinance as yf

try:
    import feedparser
except ImportError:
    feedparser = None  # graceful degradation; RSS functions will warn

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class AlertCategory(str, Enum):
    EARNINGS = "EARNINGS"
    ANALYST = "ANALYST"
    INSIDER = "INSIDER"
    MACRO = "MACRO"
    COMPANY = "COMPANY"
    MARKET = "MARKET"


# ---- RSS feed URLs (free, public) -----------------------------------------

RSS_FEEDS: dict[str, str] = {
    "MarketWatch Top Stories": "https://feeds.marketwatch.com/marketwatch/topstories/",
    "MarketWatch Market Pulse": "https://feeds.marketwatch.com/marketwatch/marketpulse/",
    "Reuters Business": "https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best",
    "CNBC Top News": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114",
    "CNBC Finance": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664",
    "Seeking Alpha Market News": "https://seekingalpha.com/market_currents.xml",
    "Seeking Alpha Wall St Breakfast": "https://seekingalpha.com/tag/wall-st-breakfast.xml",
    "Bloomberg Markets": "https://feeds.bloomberg.com/markets/news.rss",
}

SEC_EDGAR_FEEDS: dict[str, str] = {
    "SEC Full-Text Search": "https://efts.sec.gov/LATEST/search-index?q=%22form+4%22&dateRange=custom&startdt={start}&enddt={end}",
    # Public RSS feed for EDGAR filings
    "SEC EDGAR Company RSS": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company={symbol}&CIK=&type={form_type}&dateb=&owner=include&count=20&search_text=&action=getcompany&output=atom",
    # Full-text RSS for recent filings
    "SEC EDGAR Recent": "https://efts.sec.gov/LATEST/search-index?q={symbol}&forms={form_type}&dateRange=custom&startdt={start}&enddt={end}",
}

# EDGAR full-text search API (JSON, no auth needed)
SEC_EFTS_URL = "https://efts.sec.gov/LATEST/search-index"

# ---------------------------------------------------------------------------
# Sentiment word lists
# ---------------------------------------------------------------------------

BULLISH_WORDS: set[str] = {
    # strong positive
    "surge", "soar", "rally", "breakout", "upgrade", "outperform",
    "beat", "exceeds", "record", "boom", "bullish", "buy",
    "strong", "growth", "profit", "gains", "jumps", "spikes",
    "optimistic", "momentum", "recovery", "rebound", "accelerate",
    "overweight", "upside", "positive", "raises", "dividend",
    "innovation", "expansion", "acquires", "partnership",
    "approval", "launch", "milestone", "breakthrough",
    # moderate positive
    "steady", "resilient", "healthy", "solid", "stable",
    "improving", "higher", "up", "rises", "advances",
    "outpace", "lifts", "tops", "surpasses", "confidence",
}

BEARISH_WORDS: set[str] = {
    # strong negative
    "crash", "plunge", "collapse", "downgrade", "underperform",
    "miss", "misses", "warning", "sell", "bearish", "short",
    "weak", "decline", "loss", "losses", "drops", "tumbles",
    "pessimistic", "recession", "default", "bankruptcy",
    "underweight", "downside", "negative", "cuts", "layoffs",
    "fraud", "investigation", "lawsuit", "recall", "scandal",
    "delisted", "halt", "suspension", "probe", "crisis",
    # moderate negative
    "slows", "slowing", "concern", "risk", "fears",
    "lower", "down", "falls", "retreats", "pressure",
    "disappoints", "caution", "volatile", "uncertainty", "debt",
}

# Words that make headlines feel urgent / high-impact
URGENCY_WORDS: set[str] = {
    "crash", "surge", "warning", "breaking", "urgent", "alert",
    "upgrade", "downgrade", "halt", "plunge", "soar", "crisis",
    "bankruptcy", "default", "recall", "investigation", "fraud",
    "record", "unprecedented", "shock", "surprise", "explosion",
}

# ---- Category keyword mapping ---------------------------------------------

_CATEGORY_KEYWORDS: dict[AlertCategory, set[str]] = {
    AlertCategory.EARNINGS: {
        "earnings", "revenue", "eps", "guidance", "forecast",
        "quarterly", "annual", "profit", "income", "results",
        "beat", "miss", "outlook", "q1", "q2", "q3", "q4",
    },
    AlertCategory.ANALYST: {
        "upgrade", "downgrade", "price target", "analyst",
        "rating", "overweight", "underweight", "outperform",
        "underperform", "buy", "sell", "hold", "neutral",
        "initiates", "coverage", "maintains", "reiterates",
    },
    AlertCategory.INSIDER: {
        "insider", "form 4", "sec filing", "director",
        "officer", "10b5-1", "purchase", "sale", "acquisition",
        "beneficial", "ownership", "ceo buy", "cfo buy",
    },
    AlertCategory.MACRO: {
        "fed", "federal reserve", "interest rate", "inflation",
        "cpi", "ppi", "gdp", "unemployment", "jobs", "nonfarm",
        "fomc", "powell", "treasury", "yield", "tariff",
        "geopolitical", "sanctions", "oil", "opec", "war",
    },
    AlertCategory.COMPANY: {
        "launch", "product", "lawsuit", "settlement", "ceo",
        "management", "appoint", "resign", "restructure",
        "merger", "acquisition", "partnership", "contract",
        "patent", "fda", "approval", "regulatory",
    },
    AlertCategory.MARKET: {
        "s&p", "nasdaq", "dow", "index", "sector", "rotation",
        "correction", "bear market", "bull market", "etf",
        "market", "breadth", "volatility", "vix",
    },
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class NewsItem:
    """A single scored news item."""
    title: str
    source: str
    url: str
    published: Optional[datetime]
    sentiment_score: float          # -1.0 to +1.0
    category: AlertCategory
    is_urgent: bool
    symbol: Optional[str] = None    # None for market-wide news
    summary: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        d["category"] = self.category.value
        if self.published:
            d["published"] = self.published.isoformat()
        return d


@dataclass
class SentimentSummary:
    """Aggregate sentiment for a stock or the market."""
    symbol: Optional[str]
    score: float                    # -1.0 to +1.0
    num_articles: int
    bullish_count: int
    bearish_count: int
    neutral_count: int
    urgent_count: int
    top_categories: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _parse_dt(raw) -> Optional[datetime]:
    """Best-effort parse of various date formats found in feeds."""
    if raw is None:
        return None
    if isinstance(raw, datetime):
        return raw if raw.tzinfo else raw.replace(tzinfo=timezone.utc)
    for fmt in (
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            dt = datetime.strptime(str(raw), fmt)
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def _tokenize(text: str) -> list[str]:
    """Lowercase tokenization, keeping multi-word patterns intact for matching."""
    return re.findall(r"[a-z0-9&]+(?:'[a-z]+)?", text.lower())


def _score_text(text: str) -> float:
    """Return sentiment score in [-1.0, +1.0] for a block of text."""
    tokens = set(_tokenize(text))
    lower_text = text.lower()

    bullish_hits = tokens & BULLISH_WORDS
    bearish_hits = tokens & BEARISH_WORDS

    # Also check multi-word phrases (e.g. "price target", "bear market")
    all_phrases = set()
    for wordset in (BULLISH_WORDS, BEARISH_WORDS):
        for w in wordset:
            if " " in w:
                all_phrases.add(w)
    for phrase in all_phrases:
        if phrase in lower_text:
            if phrase in BULLISH_WORDS:
                bullish_hits.add(phrase)
            else:
                bearish_hits.add(phrase)

    total = len(bullish_hits) + len(bearish_hits)
    if total == 0:
        return 0.0

    raw = (len(bullish_hits) - len(bearish_hits)) / total
    # Clamp to [-1, 1]
    return max(-1.0, min(1.0, raw))


def _detect_urgency(text: str) -> bool:
    tokens = set(_tokenize(text))
    return bool(tokens & URGENCY_WORDS)


def _classify(text: str) -> AlertCategory:
    """Pick the best-matching alert category for a piece of text."""
    lower = text.lower()
    best_cat = AlertCategory.MARKET
    best_score = 0
    for cat, keywords in _CATEGORY_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in lower)
        if hits > best_score:
            best_score = hits
            best_cat = cat
    return best_cat


def _within_days(dt: Optional[datetime], days: int) -> bool:
    if dt is None:
        return True  # include items without a date
    cutoff = _now_utc() - timedelta(days=days)
    try:
        return dt >= cutoff
    except TypeError:
        return True


# ---------------------------------------------------------------------------
# News fetching — yfinance
# ---------------------------------------------------------------------------

def _fetch_yfinance_news(symbol: str, days: int = 7) -> list[NewsItem]:
    """Pull news items from yfinance for *symbol*."""
    items: list[NewsItem] = []
    try:
        ticker = yf.Ticker(symbol)
        news_list = ticker.news or []
    except Exception as exc:
        logger.warning("yfinance news fetch failed for %s: %s", symbol, exc)
        return items

    for entry in news_list:
        # yfinance >= 0.2.31 returns dicts with 'title', 'link', 'publisher',
        # 'providerPublishTime' (unix ts) or 'published'.
        title = entry.get("title", "")
        url = entry.get("link", "")
        source = entry.get("publisher", "Yahoo Finance")
        pub_ts = entry.get("providerPublishTime")
        pub_dt = (
            datetime.fromtimestamp(pub_ts, tz=timezone.utc)
            if pub_ts else None
        )

        if not _within_days(pub_dt, days):
            continue

        combined_text = f"{title} {entry.get('summary', '')}"
        items.append(NewsItem(
            title=title,
            source=source,
            url=url,
            published=pub_dt,
            sentiment_score=round(_score_text(combined_text), 3),
            category=_classify(combined_text),
            is_urgent=_detect_urgency(combined_text),
            symbol=symbol,
            summary=entry.get("summary", "")[:300],
        ))
    return items


def _fetch_yfinance_market_news() -> list[NewsItem]:
    """Fetch broad market news via index tickers."""
    items: list[NewsItem] = []
    for idx_symbol in ("^GSPC", "^DJI", "^IXIC"):
        try:
            ticker = yf.Ticker(idx_symbol)
            news_list = ticker.news or []
        except Exception:
            continue
        for entry in news_list:
            title = entry.get("title", "")
            url = entry.get("link", "")
            source = entry.get("publisher", "Yahoo Finance")
            pub_ts = entry.get("providerPublishTime")
            pub_dt = (
                datetime.fromtimestamp(pub_ts, tz=timezone.utc)
                if pub_ts else None
            )
            combined = f"{title} {entry.get('summary', '')}"
            items.append(NewsItem(
                title=title,
                source=source,
                url=url,
                published=pub_dt,
                sentiment_score=round(_score_text(combined), 3),
                category=_classify(combined),
                is_urgent=_detect_urgency(combined),
                symbol=None,
                summary=entry.get("summary", "")[:300],
            ))
    # Deduplicate by title
    seen: set[str] = set()
    unique: list[NewsItem] = []
    for item in items:
        key = item.title.strip().lower()
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique


# ---------------------------------------------------------------------------
# News fetching — RSS feeds
# ---------------------------------------------------------------------------

def _ensure_feedparser():
    if feedparser is None:
        raise ImportError(
            "feedparser is required for RSS functionality. "
            "Install it with: pip install feedparser"
        )


def _fetch_rss_news(
    symbol: Optional[str] = None,
    days: int = 7,
    feeds: Optional[dict[str, str]] = None,
) -> list[NewsItem]:
    """Parse general-purpose RSS feeds and optionally filter by *symbol*."""
    _ensure_feedparser()
    feeds = feeds or RSS_FEEDS
    items: list[NewsItem] = []

    for feed_name, url in feeds.items():
        try:
            parsed = feedparser.parse(url)
        except Exception as exc:
            logger.warning("RSS fetch failed for %s: %s", feed_name, exc)
            continue

        for entry in parsed.entries:
            title = entry.get("title", "")
            link = entry.get("link", "")
            summary = entry.get("summary", entry.get("description", ""))
            pub_raw = entry.get("published", entry.get("updated"))
            pub_dt = _parse_dt(pub_raw)

            if not _within_days(pub_dt, days):
                continue

            combined = f"{title} {summary}"

            # If a symbol was requested, skip articles that don't mention it
            if symbol:
                text_upper = combined.upper()
                # Match $AAPL, (AAPL), or standalone AAPL
                pattern = rf'(?:\$|\b){re.escape(symbol.upper())}\b'
                if not re.search(pattern, text_upper):
                    continue

            items.append(NewsItem(
                title=title,
                source=feed_name,
                url=link,
                published=pub_dt,
                sentiment_score=round(_score_text(combined), 3),
                category=_classify(combined),
                is_urgent=_detect_urgency(combined),
                symbol=symbol,
                summary=(summary or "")[:300],
            ))

    return items


# ---------------------------------------------------------------------------
# News fetching — SEC EDGAR
# ---------------------------------------------------------------------------

def _fetch_sec_filings(
    symbol: str,
    form_types: tuple[str, ...] = ("10-K", "10-Q", "8-K", "4"),
    days: int = 30,
) -> list[NewsItem]:
    """Fetch recent SEC filings for *symbol* via EDGAR's full-text search RSS.

    Form type '4' covers insider-transaction reports (Form 4).
    """
    _ensure_feedparser()
    items: list[NewsItem] = []
    start_dt = (_now_utc() - timedelta(days=days)).strftime("%Y-%m-%d")
    end_dt = _now_utc().strftime("%Y-%m-%d")

    for form_type in form_types:
        url = (
            f"https://efts.sec.gov/LATEST/search-index"
            f"?q=%22{symbol}%22&forms={form_type}"
            f"&dateRange=custom&startdt={start_dt}&enddt={end_dt}"
        )
        # EDGAR also provides an Atom feed per company
        atom_url = (
            f"https://www.sec.gov/cgi-bin/browse-edgar"
            f"?action=getcompany&company=&CIK={symbol}"
            f"&type={form_type}&dateb=&owner=include&count=10"
            f"&search_text=&action=getcompany&output=atom"
        )
        for feed_url in (atom_url,):
            try:
                parsed = feedparser.parse(feed_url)
            except Exception as exc:
                logger.warning("SEC fetch failed for %s/%s: %s", symbol, form_type, exc)
                continue

            for entry in parsed.entries:
                title = entry.get("title", "")
                link = entry.get("link", "")
                summary = entry.get("summary", "")
                pub_dt = _parse_dt(entry.get("updated", entry.get("published")))

                if not _within_days(pub_dt, days):
                    continue

                # Determine category based on form type
                if form_type == "4":
                    cat = AlertCategory.INSIDER
                elif form_type in ("10-K", "10-Q"):
                    cat = AlertCategory.EARNINGS
                else:
                    cat = AlertCategory.COMPANY

                combined = f"{title} {summary}"
                items.append(NewsItem(
                    title=title,
                    source=f"SEC EDGAR ({form_type})",
                    url=link,
                    published=pub_dt,
                    sentiment_score=round(_score_text(combined), 3),
                    category=cat,
                    is_urgent=_detect_urgency(combined),
                    symbol=symbol,
                    summary=(summary or "")[:300],
                ))

    return items


# ---------------------------------------------------------------------------
# Aggregation helpers
# ---------------------------------------------------------------------------

def _aggregate_sentiment(items: list[NewsItem]) -> SentimentSummary:
    """Build a SentimentSummary from a list of scored news items."""
    if not items:
        return SentimentSummary(
            symbol=None, score=0.0, num_articles=0,
            bullish_count=0, bearish_count=0, neutral_count=0,
            urgent_count=0, top_categories=[],
        )

    symbol = items[0].symbol  # may be None for market-wide
    bullish = sum(1 for i in items if i.sentiment_score > 0.1)
    bearish = sum(1 for i in items if i.sentiment_score < -0.1)
    neutral = len(items) - bullish - bearish
    urgent = sum(1 for i in items if i.is_urgent)

    # Weighted average: more recent articles get slightly higher weight
    now = _now_utc()
    weighted_sum = 0.0
    weight_total = 0.0
    for item in items:
        if item.published:
            age_hours = max((now - item.published).total_seconds() / 3600, 1)
            weight = 1.0 / (1.0 + (age_hours / 24))  # decay over days
        else:
            weight = 0.5
        weighted_sum += item.sentiment_score * weight
        weight_total += weight

    avg_score = weighted_sum / weight_total if weight_total else 0.0

    # Top categories by frequency
    cat_counts: dict[str, int] = {}
    for item in items:
        cat_counts[item.category.value] = cat_counts.get(item.category.value, 0) + 1
    top_cats = sorted(cat_counts, key=cat_counts.get, reverse=True)[:3]

    return SentimentSummary(
        symbol=symbol,
        score=round(max(-1.0, min(1.0, avg_score)), 3),
        num_articles=len(items),
        bullish_count=bullish,
        bearish_count=bearish,
        neutral_count=neutral,
        urgent_count=urgent,
        top_categories=top_cats,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_stock_news(symbol: str, days: int = 7) -> list[dict]:
    """Return a list of scored news items for *symbol*.

    Aggregates news from yfinance, RSS feeds, and SEC EDGAR.  Each item is
    a dict with keys: title, source, url, published, sentiment_score,
    category, is_urgent, symbol, summary.
    """
    symbol = symbol.upper().strip()
    all_items: list[NewsItem] = []

    # 1. yfinance (always available)
    all_items.extend(_fetch_yfinance_news(symbol, days=days))

    # 2. RSS feeds (needs feedparser)
    try:
        all_items.extend(_fetch_rss_news(symbol=symbol, days=days))
    except ImportError:
        logger.info("Skipping RSS feeds — feedparser not installed")

    # 3. SEC EDGAR (needs feedparser)
    try:
        all_items.extend(_fetch_sec_filings(symbol, days=max(days, 30)))
    except ImportError:
        logger.info("Skipping SEC EDGAR — feedparser not installed")

    # Deduplicate by normalised title
    seen: set[str] = set()
    unique: list[NewsItem] = []
    for item in all_items:
        key = re.sub(r"\s+", " ", item.title.strip().lower())
        if key and key not in seen:
            seen.add(key)
            unique.append(item)

    # Sort newest first
    unique.sort(
        key=lambda x: x.published or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    return [item.to_dict() for item in unique]


def get_market_news(days: int = 3) -> dict:
    """Return overall market news and an aggregate sentiment summary.

    Returns a dict with keys: ``news`` (list of scored items) and
    ``sentiment`` (aggregate summary dict).
    """
    all_items: list[NewsItem] = []

    # yfinance market news
    all_items.extend(_fetch_yfinance_market_news())

    # RSS feeds (unfiltered by symbol)
    try:
        all_items.extend(_fetch_rss_news(symbol=None, days=days))
    except ImportError:
        logger.info("Skipping RSS feeds — feedparser not installed")

    # Filter by recency
    all_items = [i for i in all_items if _within_days(i.published, days)]

    # Deduplicate
    seen: set[str] = set()
    unique: list[NewsItem] = []
    for item in all_items:
        key = re.sub(r"\s+", " ", item.title.strip().lower())
        if key and key not in seen:
            seen.add(key)
            unique.append(item)

    unique.sort(
        key=lambda x: x.published or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )

    summary = _aggregate_sentiment(unique)
    return {
        "news": [i.to_dict() for i in unique],
        "sentiment": summary.to_dict(),
    }


def get_sentiment_score(symbol: str, days: int = 7) -> dict:
    """Return the aggregate sentiment for *symbol* as a dict.

    Keys: symbol, score (-1 to +1), num_articles, bullish_count,
    bearish_count, neutral_count, urgent_count, top_categories.
    """
    symbol = symbol.upper().strip()
    all_items: list[NewsItem] = []

    all_items.extend(_fetch_yfinance_news(symbol, days=days))
    try:
        all_items.extend(_fetch_rss_news(symbol=symbol, days=days))
    except ImportError:
        pass

    summary = _aggregate_sentiment(all_items)
    summary.symbol = symbol
    return summary.to_dict()


def get_upcoming_events(symbol: str) -> dict:
    """Return upcoming earnings dates, ex-dividend dates, and other events.

    Relies on yfinance's calendar / info fields.
    """
    symbol = symbol.upper().strip()
    ticker = yf.Ticker(symbol)
    info = ticker.info or {}

    events: dict = {
        "symbol": symbol,
        "earnings_dates": [],
        "ex_dividend_date": None,
        "dividend_date": None,
        "next_fiscal_year_end": None,
    }

    # Earnings dates
    try:
        cal = ticker.calendar
        if cal is not None:
            if isinstance(cal, dict):
                for key in ("Earnings Date", "Earnings Average", "Revenue Average"):
                    val = cal.get(key)
                    if val is not None:
                        events[key.lower().replace(" ", "_")] = (
                            val.isoformat() if isinstance(val, datetime) else str(val)
                        )
                earn_dates = cal.get("Earnings Date")
                if isinstance(earn_dates, list):
                    events["earnings_dates"] = [
                        d.isoformat() if isinstance(d, datetime) else str(d)
                        for d in earn_dates
                    ]
                elif earn_dates is not None:
                    events["earnings_dates"] = [str(earn_dates)]
    except Exception as exc:
        logger.debug("Calendar fetch failed for %s: %s", symbol, exc)

    # Dividend dates from info
    for field_name, key in (
        ("exDividendDate", "ex_dividend_date"),
        ("dividendDate", "dividend_date"),
        ("lastFiscalYearEnd", "next_fiscal_year_end"),
    ):
        raw = info.get(field_name)
        if raw:
            try:
                events[key] = datetime.fromtimestamp(raw, tz=timezone.utc).isoformat()
            except (TypeError, ValueError, OSError):
                events[key] = str(raw)

    return events


def scan_insider_activity(symbol: str, days: int = 90) -> dict:
    """Return recent insider trades for *symbol*.

    Combines yfinance insider-transaction data with SEC EDGAR Form 4 filings.
    """
    symbol = symbol.upper().strip()
    ticker = yf.Ticker(symbol)

    result: dict = {
        "symbol": symbol,
        "transactions": [],
        "net_sentiment": 0.0,
        "summary": "",
    }

    # ---- yfinance insider transactions ------------------------------------
    try:
        insider_df = ticker.insider_transactions
        if insider_df is not None and not insider_df.empty:
            cutoff = _now_utc() - timedelta(days=days)
            for _, row in insider_df.iterrows():
                txn_date = row.get("Start Date") or row.get("Date")
                if txn_date is not None:
                    if hasattr(txn_date, "tzinfo") and txn_date.tzinfo is None:
                        txn_date = txn_date.replace(tzinfo=timezone.utc)
                    try:
                        if txn_date < cutoff:
                            continue
                    except TypeError:
                        pass

                txn = {
                    "insider": row.get("Insider") or row.get("Insider Trading"),
                    "relation": row.get("Relation") or row.get("Position"),
                    "transaction": row.get("Transaction") or row.get("Text"),
                    "date": str(txn_date) if txn_date else None,
                    "shares": row.get("Shares") or row.get("Value"),
                    "value": row.get("Value"),
                }
                result["transactions"].append(txn)
    except Exception as exc:
        logger.debug("Insider transactions unavailable for %s: %s", symbol, exc)

    # ---- SEC EDGAR Form 4 filings -----------------------------------------
    try:
        sec_items = _fetch_sec_filings(symbol, form_types=("4",), days=days)
        for item in sec_items:
            result["transactions"].append({
                "insider": None,
                "relation": None,
                "transaction": item.title,
                "date": item.published.isoformat() if item.published else None,
                "shares": None,
                "value": None,
                "source": item.source,
                "url": item.url,
            })
    except ImportError:
        logger.info("SEC Form 4 fetch skipped — feedparser not installed")

    # ---- Simple net-sentiment summary -------------------------------------
    buys = 0
    sells = 0
    for txn in result["transactions"]:
        text = (str(txn.get("transaction", "")) + " " + str(txn.get("insider", ""))).lower()
        if any(w in text for w in ("purchase", "buy", "acquisition", "exercise")):
            buys += 1
        elif any(w in text for w in ("sale", "sell", "disposition")):
            sells += 1

    total = buys + sells
    if total > 0:
        result["net_sentiment"] = round((buys - sells) / total, 3)

    if buys > sells:
        result["summary"] = (
            f"Net insider BUYING ({buys} buys vs {sells} sells in {days}d). "
            "Bullish insider signal."
        )
    elif sells > buys:
        result["summary"] = (
            f"Net insider SELLING ({sells} sells vs {buys} buys in {days}d). "
            "Bearish insider signal — though routine sales are common."
        )
    else:
        result["summary"] = f"Balanced insider activity ({buys} buys, {sells} sells in {days}d)."

    return result


# ---------------------------------------------------------------------------
# Quick CLI test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    logging.basicConfig(level=logging.INFO)
    test_symbol = "AAPL"

    print(f"\n{'='*60}")
    print(f"  News Scanner — quick test for {test_symbol}")
    print(f"{'='*60}\n")

    print(">> get_stock_news")
    news = get_stock_news(test_symbol, days=7)
    print(f"   {len(news)} articles found")
    for item in news[:3]:
        score = item["sentiment_score"]
        arrow = "+" if score > 0 else ("-" if score < 0 else " ")
        print(f"   [{arrow}{abs(score):.2f}] [{item['category']}] {item['title'][:80]}")

    print("\n>> get_sentiment_score")
    sentiment = get_sentiment_score(test_symbol)
    print(f"   {json.dumps(sentiment, indent=2)}")

    print("\n>> get_upcoming_events")
    events = get_upcoming_events(test_symbol)
    print(f"   {json.dumps(events, indent=2, default=str)}")

    print("\n>> scan_insider_activity")
    insiders = scan_insider_activity(test_symbol)
    print(f"   {insiders['summary']}")
    print(f"   {len(insiders['transactions'])} transactions found")

    print("\n>> get_market_news")
    mkt = get_market_news(days=2)
    print(f"   {len(mkt['news'])} market articles")
    print(f"   Market sentiment: {mkt['sentiment']['score']:.3f}")
