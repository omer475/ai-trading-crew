"""Risk management and trading rules enforced by the Head Coach."""

TRADING_RULES = {
    # Position sizing
    "max_position_pct": 0.05,         # Max 5% of portfolio per position
    "max_sector_pct": 0.25,           # Max 25% in one sector
    "max_total_positions": 20,        # Max 20 open positions

    # Risk limits
    "max_daily_loss_pct": 0.02,       # Stop trading if down 2% in a day
    "stop_loss_pct": 0.07,            # 7% stop loss per position
    "take_profit_pct": 0.15,          # 15% take profit

    # Consensus rules
    "min_agents_agree": 3,            # At least 3 agents must agree on a trade
    "min_confidence": 0.7,            # Minimum 70% confidence score

    # Human override threshold
    "human_approval_above_pct": 0.02, # Notify human for trades > 2% of portfolio
}
