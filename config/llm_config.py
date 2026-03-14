"""
LLM configuration — Two-Tier Strategy (Option A: Best Quality)

Tier 1: Claude Opus 4.6 → Decision agents (Head Coach, Risk Manager, etc.)
Tier 2: DeepSeek V3.2  → Analysis & data agents (42 agents)
"""

import os
from dotenv import load_dotenv
from autogen_ext.models.anthropic import AnthropicChatCompletionClient
from autogen_ext.models.openai import OpenAIChatCompletionClient

load_dotenv()


def get_decision_client():
    """Claude Opus 4.6 — for the 8 decision agents."""
    return AnthropicChatCompletionClient(
        model="claude-opus-4-6",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        temperature=0.2,
        max_tokens=4096,
    )


def get_analysis_client():
    """DeepSeek V3.2 — for the 42 analysis & data agents."""
    return OpenAIChatCompletionClient(
        model="deepseek-chat",
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com/v1",
        temperature=0.3,
        model_info={
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "family": "unknown",
            "structured_output": True,
        },
    )


def get_manager_client():
    """DeepSeek V3.2 — cheap model for GroupChat speaker selection."""
    return OpenAIChatCompletionClient(
        model="deepseek-chat",
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com/v1",
        temperature=0.1,
        model_info={
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "family": "unknown",
            "structured_output": True,
        },
    )
