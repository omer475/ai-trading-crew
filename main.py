"""
AI Trading Crew — Main Entry Point

Two-Tier Model Strategy (Option A: Best Quality):
  - Claude Opus 4.6 → Head Coach, Risk Manager, Devil's Advocate, Lead Analysts
  - DeepSeek V3.2  → All other analysis & data agents (42 agents)

Usage:
    python main.py                  # Run full analysis cycle
    python main.py --test           # Run with 5 test agents only
    python main.py --symbol AAPL    # Analyze a specific stock
"""

import argparse
import autogen
from agents.personas.definitions import PERSONAS, TEAMS
from agents.head_coach import HEAD_COACH_PROMPT
from config.llm_config import llm_config_decision, llm_config_analysis, llm_config_manager

# These 8 agents use Claude Opus 4.6 (Tier 1 — best reasoning)
DECISION_AGENTS = {
    "head_coach",           # Supervises everything
    "risk_portfolio",       # Viktor — portfolio risk, has VETO power
    "risk_devils_advocate", # Mei — challenges every trade
    "risk_compliance",      # David — regulatory compliance
    "ta_trend_follower",    # Marcus — Technical Analysis team lead
    "fa_value_investor",    # Warren — Fundamental Analysis team lead
    "macro_fed_watcher",    # Janet — Macro team lead
    "quant_stat_arb",       # Dr. Chen — Quant team lead
}


def create_agent(persona_id: str, persona: dict) -> autogen.AssistantAgent:
    """Create an AutoGen agent with the right model tier."""
    # Decision agents → Claude Opus 4.6, all others → DeepSeek V3.2
    if persona_id in DECISION_AGENTS:
        config = llm_config_decision
    else:
        config = llm_config_analysis

    return autogen.AssistantAgent(
        name=persona["name"].replace(" ", "_").replace(".", ""),
        system_message=persona["system_message"],
        description=f"{persona['name']} - {persona['team']} team",  # Used for speaker selection
        llm_config=config,
    )


def create_head_coach() -> autogen.AssistantAgent:
    """Create the Head Coach — always uses Claude Opus 4.6."""
    return autogen.AssistantAgent(
        name="Head_Coach",
        system_message=HEAD_COACH_PROMPT,
        description="Head Coach - supervises all teams and makes final trading decisions",
        llm_config=llm_config_decision,  # Claude Opus 4.6
    )


def create_human_proxy() -> autogen.UserProxyAgent:
    """Create a human proxy for oversight and approvals."""
    return autogen.UserProxyAgent(
        name="Human_Trader",
        human_input_mode="TERMINATE",
        max_consecutive_auto_reply=0,
        code_execution_config=False,
    )


def run_analysis(symbol: str = "AAPL", test_mode: bool = False):
    """Run a full analysis cycle for a stock."""

    print(f"\n{'='*60}")
    print(f"  AI TRADING CREW — Analyzing {symbol}")
    print(f"  Mode: {'TEST (5 agents)' if test_mode else 'FULL (50 agents)'}")
    print(f"  Decision model: Claude Opus 4.6")
    print(f"  Analysis model: DeepSeek V3.2")
    print(f"{'='*60}\n")

    coach = create_head_coach()
    human = create_human_proxy()

    if test_mode:
        # Quick test with 5 key agents (all use Claude Opus in test mode)
        test_agents = [
            create_agent("ta_trend_follower", PERSONAS["ta_trend_follower"]),
            create_agent("fa_value_investor", PERSONAS["fa_value_investor"]),
            create_agent("macro_fed_watcher", PERSONAS["macro_fed_watcher"]),
            create_agent("risk_portfolio", PERSONAS["risk_portfolio"]),
            create_agent("risk_devils_advocate", PERSONAS["risk_devils_advocate"]),
        ]

        group_chat = autogen.GroupChat(
            agents=[coach] + test_agents + [human],
            messages=[],
            max_round=15,
        )
        # GroupChat manager uses cheap DeepSeek for speaker selection
        manager = autogen.GroupChatManager(
            groupchat=group_chat,
            llm_config=llm_config_manager,
        )

        human.initiate_chat(
            manager,
            message=f"Analyze {symbol} for a potential trade. Each specialist should give their "
                    f"analysis, then the Head Coach makes the final decision. "
                    f"Consider current market conditions as of today.",
        )
    else:
        # Full mode: Each team debates internally, then Head Coach decides
        team_summaries = {}

        for team_key, team_info in TEAMS.items():
            print(f"\n--- {team_info['name']} analyzing {symbol} ---")
            print(f"    Agents: {len(team_info['members'])} | Lead: {team_info['lead']}")
            print()

            team_agents = [
                create_agent(mid, PERSONAS[mid])
                for mid in team_info["members"]
            ]

            group_chat = autogen.GroupChat(
                agents=team_agents,
                messages=[],
                max_round=8,
            )
            # Cheap model for "who speaks next" within each team
            manager = autogen.GroupChatManager(
                groupchat=group_chat,
                llm_config=llm_config_manager,
            )

            team_agents[0].initiate_chat(
                manager,
                message=f"Team, analyze {symbol} from our {team_info['name']} perspective. "
                        f"Each member give your specific analysis. Conclude with a team "
                        f"recommendation: BUY, SELL, or HOLD with confidence level.",
            )

            team_summaries[team_key] = (
                group_chat.messages[-1]["content"] if group_chat.messages else "No analysis"
            )

        # Head Coach (Claude Opus 4.6) reviews all team summaries
        print(f"\n{'='*60}")
        print("  HEAD COACH (Claude Opus 4.6) — Final Decision")
        print(f"{'='*60}\n")

        combined_analysis = "\n\n".join(
            f"=== {TEAMS[k]['name']} ===\n{v}" for k, v in team_summaries.items()
        )

        final_chat = autogen.GroupChat(
            agents=[coach, human],
            messages=[],
            max_round=5,
        )
        final_manager = autogen.GroupChatManager(
            groupchat=final_chat,
            llm_config=llm_config_manager,
        )

        human.initiate_chat(
            final_manager,
            message=f"Here are the team analyses for {symbol}:\n\n{combined_analysis}\n\n"
                    f"Head Coach, make your final trading decision.",
        )

    print(f"\n{'='*60}")
    print("  Analysis Complete")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Trading Crew")
    parser.add_argument("--symbol", default="AAPL", help="Stock symbol to analyze")
    parser.add_argument("--test", action="store_true", help="Run in test mode (5 agents)")
    args = parser.parse_args()

    run_analysis(symbol=args.symbol, test_mode=args.test)
