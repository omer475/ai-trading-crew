"""
AI Trading Crew — Main Entry Point (AutoGen 0.7+)

Two-Tier Model Strategy (Option A: Best Quality):
  - Claude Opus 4.6 → Head Coach, Risk Manager, Devil's Advocate, Lead Analysts
  - DeepSeek V3.2  → All other analysis & data agents (42 agents)

Usage:
    python main.py                  # Run full analysis cycle
    python main.py --test           # Run with 5 test agents only
    python main.py --symbol AAPL    # Analyze a specific stock
"""

import asyncio
import argparse
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import MaxMessageTermination
from agents.personas.definitions import PERSONAS, TEAMS
from agents.head_coach import HEAD_COACH_PROMPT
from config.llm_config import get_decision_client, get_analysis_client, get_manager_client

# These 8 agents use Claude Opus 4.6 (Tier 1 — best reasoning)
DECISION_AGENT_IDS = {
    "head_coach",
    "risk_portfolio",
    "risk_devils_advocate",
    "risk_compliance",
    "ta_trend_follower",
    "fa_value_investor",
    "macro_fed_watcher",
    "quant_stat_arb",
}


def create_agent(persona_id: str, persona: dict,
                 decision_client, analysis_client) -> AssistantAgent:
    """Create an AutoGen agent with the right model tier."""
    client = decision_client if persona_id in DECISION_AGENT_IDS else analysis_client

    # AutoGen 0.7 requires names to be valid Python identifiers
    import re
    safe_name = re.sub(r"[^a-zA-Z0-9_]", "_", persona["name"])
    safe_name = re.sub(r"_+", "_", safe_name).strip("_")

    return AssistantAgent(
        name=safe_name,
        system_message=persona["system_message"],
        description=f"{persona['name']} - {persona['team']} team specialist",
        model_client=client,
    )


def create_head_coach(decision_client) -> AssistantAgent:
    """Create the Head Coach — always uses Claude Opus 4.6."""
    return AssistantAgent(
        name="Head_Coach",
        system_message=HEAD_COACH_PROMPT,
        description="Head Coach - supervises all teams and makes final trading decisions",
        model_client=decision_client,
    )


async def run_analysis(symbol: str = "AAPL", test_mode: bool = False):
    """Run a full analysis cycle for a stock."""

    print(f"\n{'='*60}")
    print(f"  AI TRADING CREW — Analyzing {symbol}")
    print(f"  Mode: {'TEST (5 agents)' if test_mode else 'FULL (50 agents)'}")
    print(f"  Decision model: Claude Opus 4.6")
    print(f"  Analysis model: DeepSeek V3.2")
    print(f"{'='*60}\n")

    # Create model clients (shared across agents of same tier)
    decision_client = get_decision_client()
    analysis_client = get_analysis_client()
    manager_client = get_manager_client()

    coach = create_head_coach(decision_client)

    if test_mode:
        # Quick test with 5 key agents + Head Coach
        test_agents = [
            create_agent("ta_trend_follower", PERSONAS["ta_trend_follower"],
                        decision_client, analysis_client),
            create_agent("fa_value_investor", PERSONAS["fa_value_investor"],
                        decision_client, analysis_client),
            create_agent("macro_fed_watcher", PERSONAS["macro_fed_watcher"],
                        decision_client, analysis_client),
            create_agent("risk_portfolio", PERSONAS["risk_portfolio"],
                        decision_client, analysis_client),
            create_agent("risk_devils_advocate", PERSONAS["risk_devils_advocate"],
                        decision_client, analysis_client),
        ]

        termination = MaxMessageTermination(max_messages=15)

        team = SelectorGroupChat(
            participants=[coach] + test_agents,
            model_client=manager_client,  # Cheap model for speaker selection
            termination_condition=termination,
        )

        task = (
            f"Analyze {symbol} for a potential trade. Each specialist should give their "
            f"analysis, then the Head Coach makes the final decision. "
            f"Consider current market conditions as of today."
        )

        print(f"Starting analysis of {symbol} with 5 agents + Head Coach...\n")

        async for message in team.run_stream(task=task):
            if hasattr(message, "source") and hasattr(message, "content"):
                print(f"\n--- {message.source} ---")
                print(message.content)

    else:
        # Full mode: Each team debates internally, then Head Coach decides
        team_summaries = {}

        for team_key, team_info in TEAMS.items():
            print(f"\n--- {team_info['name']} analyzing {symbol} ---")
            print(f"    Agents: {len(team_info['members'])} | Lead: {team_info['lead']}")
            print()

            team_agents = [
                create_agent(mid, PERSONAS[mid], decision_client, analysis_client)
                for mid in team_info["members"]
            ]

            termination = MaxMessageTermination(max_messages=8)

            team_chat = SelectorGroupChat(
                participants=team_agents,
                model_client=manager_client,
                termination_condition=termination,
            )

            task = (
                f"Team, analyze {symbol} from our {team_info['name']} perspective. "
                f"Each member give your specific analysis. Conclude with a team "
                f"recommendation: BUY, SELL, or HOLD with confidence level."
            )

            last_message = ""
            async for message in team_chat.run_stream(task=task):
                if hasattr(message, "source") and hasattr(message, "content"):
                    print(f"  [{message.source}]: {message.content[:200]}...")
                    last_message = message.content

            team_summaries[team_key] = last_message

        # Head Coach (Claude Opus 4.6) reviews all team summaries
        print(f"\n{'='*60}")
        print("  HEAD COACH (Claude Opus 4.6) — Final Decision")
        print(f"{'='*60}\n")

        combined_analysis = "\n\n".join(
            f"=== {TEAMS[k]['name']} ===\n{v}" for k, v in team_summaries.items()
        )

        final_termination = MaxMessageTermination(max_messages=3)
        final_team = SelectorGroupChat(
            participants=[coach],
            model_client=manager_client,
            termination_condition=final_termination,
        )

        final_task = (
            f"Here are the team analyses for {symbol}:\n\n{combined_analysis}\n\n"
            f"Head Coach, make your final trading decision."
        )

        async for message in final_team.run_stream(task=final_task):
            if hasattr(message, "source") and hasattr(message, "content"):
                print(f"\n{message.content}")

    print(f"\n{'='*60}")
    print("  Analysis Complete")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Trading Crew")
    parser.add_argument("--symbol", default="AAPL", help="Stock symbol to analyze")
    parser.add_argument("--test", action="store_true", help="Run in test mode (5 agents)")
    args = parser.parse_args()

    asyncio.run(run_analysis(symbol=args.symbol, test_mode=args.test))
