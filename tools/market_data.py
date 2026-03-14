"""Market data tools that agents can use during analysis."""

import os
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


def get_stock_price(symbol: str) -> dict:
    """Get current price and basic info for a stock."""
    ticker = yf.Ticker(symbol)
    info = ticker.info
    return {
        "symbol": symbol,
        "price": info.get("currentPrice") or info.get("regularMarketPrice"),
        "market_cap": info.get("marketCap"),
        "pe_ratio": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "dividend_yield": info.get("dividendYield"),
        "52w_high": info.get("fiftyTwoWeekHigh"),
        "52w_low": info.get("fiftyTwoWeekLow"),
        "avg_volume": info.get("averageVolume"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
    }


def get_price_history(symbol: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
    """Get historical price data."""
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period, interval=interval)
    return df


def get_technical_indicators(symbol: str) -> dict:
    """Calculate key technical indicators."""
    df = get_price_history(symbol, period="1y", interval="1d")
    if df.empty:
        return {"error": f"No data for {symbol}"}

    close = df["Close"]
    volume = df["Volume"]

    # Moving averages
    sma_50 = close.rolling(50).mean().iloc[-1]
    sma_200 = close.rolling(200).mean().iloc[-1]
    ema_12 = close.ewm(span=12).mean().iloc[-1]
    ema_26 = close.ewm(span=26).mean().iloc[-1]

    # RSI (14-day)
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi = (100 - (100 / (1 + rs))).iloc[-1]

    # MACD
    macd_line = ema_12 - ema_26
    signal_line = close.ewm(span=9).mean().iloc[-1]

    current_price = close.iloc[-1]

    return {
        "symbol": symbol,
        "price": current_price,
        "sma_50": round(sma_50, 2),
        "sma_200": round(sma_200, 2),
        "ema_12": round(ema_12, 2),
        "ema_26": round(ema_26, 2),
        "rsi_14": round(rsi, 2),
        "macd": round(macd_line, 2),
        "above_sma_50": current_price > sma_50,
        "above_sma_200": current_price > sma_200,
        "golden_cross": sma_50 > sma_200,
        "avg_volume_20d": int(volume.rolling(20).mean().iloc[-1]),
        "volume_today": int(volume.iloc[-1]),
        "volume_spike": volume.iloc[-1] > volume.rolling(20).mean().iloc[-1] * 1.5,
    }


def get_financials(symbol: str) -> dict:
    """Get key financial data from latest filings."""
    ticker = yf.Ticker(symbol)

    try:
        income = ticker.quarterly_income_stmt
        balance = ticker.quarterly_balance_sheet
        cashflow = ticker.quarterly_cashflow

        return {
            "symbol": symbol,
            "revenue": income.iloc[0].get("Total Revenue") if not income.empty else None,
            "net_income": income.iloc[0].get("Net Income") if not income.empty else None,
            "total_debt": balance.iloc[0].get("Total Debt") if not balance.empty else None,
            "total_cash": balance.iloc[0].get("Cash And Cash Equivalents") if not balance.empty else None,
            "free_cash_flow": cashflow.iloc[0].get("Free Cash Flow") if not cashflow.empty else None,
        }
    except Exception as e:
        return {"symbol": symbol, "error": str(e)}


def screen_stocks(min_market_cap: float = 1e9, max_pe: float = 30) -> list[str]:
    """Simple stock screener — returns list of tickers matching criteria."""
    # Start with S&P 500 components (you'd expand this)
    watchlist = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B",
        "JPM", "JNJ", "V", "UNH", "HD", "PG", "MA", "DIS", "PYPL", "NFLX",
        "ADBE", "CRM", "INTC", "AMD", "QCOM", "TXN", "COST", "WMT",
    ]
    results = []
    for sym in watchlist:
        try:
            info = yf.Ticker(sym).info
            mc = info.get("marketCap", 0)
            pe = info.get("trailingPE", 999)
            if mc >= min_market_cap and pe <= max_pe:
                results.append(sym)
        except Exception:
            continue
    return results
