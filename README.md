# AI Trading Crew

A multi-agent AI trading system built with **AutoGen**. 50 specialized AI personas collaborate, debate, and reach consensus on US stock trades.

## Architecture

```
Human Trader (you)
    └── Head Coach (supervisor)
            ├── Technical Analysis Team (7 agents)
            ├── Fundamental Analysis Team (7 agents)
            ├── Macro & Economics Team (6 agents)
            ├── Sentiment & News Team (6 agents)
            ├── Quantitative Team (6 agents)
            ├── Risk Management Team (5 agents) ← has VETO power
            ├── Execution & Operations Team (5 agents)
            └── Strategy & Special Situations Team (8 agents)
```

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/omer475/ai-trading-crew.git
cd ai-trading-crew
pip install -r requirements.txt

# 2. Set up API keys
cp .env.example .env
# Edit .env with your keys (OpenAI, Alpaca paper trading, Polygon)

# 3. Run test mode (5 agents)
python main.py --test --symbol AAPL

# 4. Run full crew (50 agents)
python main.py --symbol AAPL
```

## API Keys Needed

| Service | Purpose | Get it at |
|---------|---------|-----------|
| OpenAI | LLM for all agents | platform.openai.com |
| Alpaca | Paper trading (free) | alpaca.markets |
| Polygon.io | Market data | polygon.io |

## Project Structure

```
ai-trading-crew/
├── main.py                          # Entry point
├── agents/
│   ├── head_coach.py                # Supervisor agent
│   └── personas/
│       └── definitions.py           # All 50 persona definitions
├── config/
│   ├── llm_config.py                # LLM settings
│   └── trading_rules.py             # Risk limits & rules
├── tools/
│   ├── market_data.py               # Price, technicals, financials
│   ├── broker.py                    # Alpaca paper trading
│   └── knowledge_base.py            # RAG with ChromaDB
├── data/
│   ├── books/                       # PDF/text books for RAG
│   └── knowledge_base/              # ChromaDB vector store
├── memory/                          # Agent trade memory
└── tests/
```

## How It Works

1. You pick a stock (e.g., `AAPL`)
2. Each of the 8 teams debates internally using AutoGen GroupChat
3. Team leads report their analysis to the Head Coach
4. Risk Team reviews and can veto
5. Devil's Advocate challenges the trade
6. Head Coach makes final BUY/SELL/HOLD decision
7. If approved, Execution Team places the order via Alpaca paper trading

## Safety

- **Paper trading only** — uses Alpaca paper API by default
- **Human oversight** — large trades require your approval
- **Risk limits** — built-in stop losses, position limits, daily loss limits
- **Devil's Advocate** — one agent's entire job is to argue against every trade

> ⚠️ This is an educational/experimental project. Not financial advice. Always paper trade first.
