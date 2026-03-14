"""Risk management and trading rules enforced by the Head Coach."""

TRADING_RULES = {
    # Position sizing
    "max_position_pct": 0.12,         # Max 12% of portfolio per position (concentrated for £10K)
    "max_sector_pct": 0.30,           # Max 30% in one sector
    "max_total_positions": 8,         # Max 8 open positions (focused portfolio)

    # Risk limits
    "max_daily_loss_pct": 0.05,       # Stop trading if down 5% in a day (wider for long-term)
    "stop_loss_pct": 0.15,            # 15% stop loss per position (wider for long-term holdings)
    "take_profit_pct": 0.40,          # 40% take profit (aim for bigger gains)

    # Consensus rules
    "min_agents_agree": 3,            # At least 3 agents must agree on a trade
    "min_confidence": 0.65,           # Minimum 65% confidence (long-term has more uncertainty)

    # Human override threshold
    "human_approval_above_pct": 0.10, # Notify human for trades > 10% of portfolio

    # Long-term holding parameters
    "min_holding_weeks": 8,           # Minimum 2 months hold
    "target_holding_months": 6,       # Target 6 month hold
    "rebalance_interval_weeks": 2,    # Check portfolio every 2 weeks
    "portfolio_currency": "GBP",
    "markets": ["LSE", "US"],
}
