"""Alpaca broker integration for paper trading."""

import os
from alpaca_trade_api import REST
from dotenv import load_dotenv

load_dotenv()


def get_broker():
    """Get Alpaca API client (paper trading)."""
    return REST(
        key_id=os.getenv("ALPACA_API_KEY"),
        secret_key=os.getenv("ALPACA_SECRET_KEY"),
        base_url=os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets"),
    )


def get_account_info() -> dict:
    """Get current account status and buying power."""
    api = get_broker()
    account = api.get_account()
    return {
        "equity": float(account.equity),
        "cash": float(account.cash),
        "buying_power": float(account.buying_power),
        "portfolio_value": float(account.portfolio_value),
        "daily_pnl": float(account.equity) - float(account.last_equity),
    }


def get_positions() -> list[dict]:
    """Get all current open positions."""
    api = get_broker()
    positions = api.list_positions()
    return [
        {
            "symbol": p.symbol,
            "qty": float(p.qty),
            "avg_entry": float(p.avg_entry_price),
            "current_price": float(p.current_price),
            "pnl": float(p.unrealized_pl),
            "pnl_pct": float(p.unrealized_plpc),
            "market_value": float(p.market_value),
        }
        for p in positions
    ]


def place_order(symbol: str, qty: int, side: str, order_type: str = "limit",
                limit_price: float = None, stop_price: float = None) -> dict:
    """Place a trade order via Alpaca paper trading."""
    api = get_broker()

    params = {
        "symbol": symbol,
        "qty": qty,
        "side": side,  # "buy" or "sell"
        "type": order_type,  # "market", "limit", "stop", "stop_limit"
        "time_in_force": "day",
    }

    if limit_price and order_type in ("limit", "stop_limit"):
        params["limit_price"] = limit_price
    if stop_price and order_type in ("stop", "stop_limit"):
        params["stop_price"] = stop_price

    order = api.submit_order(**params)
    return {
        "order_id": order.id,
        "symbol": order.symbol,
        "qty": order.qty,
        "side": order.side,
        "type": order.type,
        "status": order.status,
    }


def close_position(symbol: str) -> dict:
    """Close an entire position."""
    api = get_broker()
    order = api.close_position(symbol)
    return {"symbol": symbol, "status": "closing", "order_id": order.id}
