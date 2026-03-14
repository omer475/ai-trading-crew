"""
AI Trading Crew — Main Entry Point

Boots up the 50-agent trading system using AutoGen.
Starts with a smaller team for testing, then scales to full crew.

Usage:
    python main.py                  # Run full analysis cycle
    python main.py --test           # Run with 5 test agents only
    python main.py --symbol AAPL    # Analyze a specific stock
"""

import argparse
import autogen
from agents.personas.definitions import PERSONAS, TEAMS
from agents.head_coach import HEAD_COACH_PROMPT
from config.llm_config import llm_config, llm_config_lite
from config.trading_rules import TRADING_RULES


def create_agent(persona_id: str, persona: dict, use_lite: bool = False) -> autogen.AssistantAgent:
    """Create a single AutoGen agent from a persona definition."""
    config = llm_config_lite if use_lite else llm_config
    return autogen.AssistantAgent(
        name=persona["name"].replace(" ", "_").replace(".", ""),
        system_message=persona["system_message"],
        llm_config=config,
    )


def create_team_chat(team_key: str, topic: str) -> autogen.GroupChat:
    """Create a GroupChat for one team to discuss a topic."""
    team = TEAMS[team_key]
    agents = []
    for member_id in team["members"]:
        persona = PERSONAS[member_id]
        # Use lite model for sentiment/data agents, full model for analysts
        use_lite = team_key in ("sentiment", "execution")
        agents.append(create_agent(member_id, persona, use_lite=use_lite))

    group_chat = autogen.GroupChat(
        agents=agents,
        messages=[],
        max_round=10,  # Each team gets up to 10 rounds of discussion
    )
    return group_chat


def create_head_coach() -> autogen.AssistantAgent:
    """Create the Head Coach supervisor agent."""
    return autogen.AssistantAgent(
        name="Head_Coach",
        system_message=HEAD_COACH_PROMPT,
        llm_config=llm_config,
    )


def create_human_proxy() -> autogen.UserProxyAgent:
    """Create a human proxy for oversight and approvals."""
    return autogen.UserProxyAgent(
        name="Human_Trader",
        human_input_mode="TERMINATE",  # Only asks for input on termination
        max_consecutive_auto_reply=0,
        code_execution_config=False,
    )


def run_analysis(symbol: str = "AAPL", test_mode: bool = False):
    """Run a full analysis cycle for a stock."""

    print(f"\n{'='*60}")
    print(f"  AI TRADING CREW — Analyzing {symbol}")
    print(f"  Mode: {'TEST (5 agents)' if test_mode else 'FULL (50 agents)'}")
    print(f"{'='*60}\n")

    # Create the Head Coach
    coach = create_head_coach()
    human = create_human_proxy()

    if test_mode:
        # Quick test with 5 key agents
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
        manager = autogen.GroupChatManager(groupchat=group_chat, llm_config=llm_config)

        human.initiate_chat(
            manager,
            message=f"Analyze {symbol} for a potential trade. Each specialist should give their "
                    f"analysis, then the Head Coach makes the final decision. "
                    f"Consider current market conditions as of today.",
        )
    else:
        # Full mode: Run each team's analysis, then combine at Head Coach level
        team_summaries = {}

        for team_key, team_info in TEAMS.items():
            print(f"\n--- {team_info['name']} analyzing {symbol} ---\n")

            team_agents = [
                create_agent(mid, PERSONAS[mid], use_lite=(team_key in ("sentiment", "execution")))
                for mid in team_info["members"]
            ]

            group_chat = autogen.GroupChat(
                agents=team_agents,
                messages=[],
                max_round=8,
            )
            manager = autogen.GroupChatManager(groupchat=group_chat, llm_config=llm_config)

            # Team lead initiates discussion
            team_agents[0].initiate_chat(
                manager,
                message=f"Team, analyze {symbol} from our {team_info['name']} perspective. "
                        f"Each member give your specific analysis. Conclude with a team "
                        f"recommendation: BUY, SELL, or HOLD with confidence level.",
            )

            # Collect team summary (last message)
            team_summaries[team_key] = group_chat.messages[-1]["content"] if group_chat.messages else "No analysis"

        # Head Coach reviews all team summaries
        print(f"\n{'='*60}")
        print("  HEAD COACH — Final Decision")
        print(f"{'='*60}\n")

        combined_analysis = "\n\n".join(
            f"=== {TEAMS[k]['name']} ===\n{v}" for k, v in team_summaries.items()
        )

        final_chat = autogen.GroupChat(
            agents=[coach, human],
            messages=[],
            max_round=5,
        )
        final_manager = autogen.GroupChatManager(groupchat=final_chat, llm_config=llm_config)

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
