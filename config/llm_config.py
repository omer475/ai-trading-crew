"""
LLM configuration — Two-Tier Strategy (Option A: Best Quality)

Tier 1: Claude Opus 4.6 → Decision agents (Head Coach, Risk Manager, etc.)
         ~$95/month | 87.82% financial accuracy | 5x more token-efficient than GPT-5
Tier 2: DeepSeek V3.2 → Analysis & data agents (42 agents)
         ~$10/month | Strong reasoning | 90% cache discount on system prompts
Tier 3: DeepSeek V3.2 → GroupChat manager speaker selection (cheap & fast)
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ─── Tier 1: Decision Agents (8 agents) ───────────────────────────────
# Claude Opus 4.6 via Anthropic API (OpenAI-compatible endpoint)
# Used for: Head Coach, Risk Manager, Devil's Advocate, Lead Analysts, Compliance
llm_config_decision = {
    "config_list": [
        {
            "model": "claude-opus-4-6",
            "api_key": os.getenv("ANTHROPIC_API_KEY"),
            "api_type": "anthropic",
        }
    ],
    "temperature": 0.2,  # Low temp for critical financial decisions
    "timeout": 120,
}

# ─── Tier 2: Analysis & Data Agents (42 agents) ──────────────────────
# DeepSeek V3.2 via OpenAI-compatible API
# Used for: All analysts, sector specialists, sentiment, data agents
llm_config_analysis = {
    "config_list": [
        {
            "model": "deepseek-chat",
            "api_key": os.getenv("DEEPSEEK_API_KEY"),
            "base_url": "https://api.deepseek.com/v1",
        }
    ],
    "temperature": 0.3,
    "timeout": 90,
}

# ─── Tier 3: GroupChat Manager (speaker selection only) ───────────────
# DeepSeek V3.2 — cheapest option for the "who speaks next?" calls
llm_config_manager = {
    "config_list": [
        {
            "model": "deepseek-chat",
            "api_key": os.getenv("DEEPSEEK_API_KEY"),
            "base_url": "https://api.deepseek.com/v1",
        }
    ],
    "temperature": 0.1,  # Very low — just picking the next speaker
    "timeout": 30,
}

# ─── Backward compatibility aliases ──────────────────────────────────
# These map to the old variable names used in main.py
llm_config = llm_config_decision       # Default: best model
llm_config_lite = llm_config_analysis   # Lite: cheap model
