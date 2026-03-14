"""LLM configuration for all agents."""
import os
from dotenv import load_dotenv

load_dotenv()

# Base LLM config — all 50 agents share this
llm_config = {
    "config_list": [
        {
            "model": "gpt-4o",
            "api_key": os.getenv("OPENAI_API_KEY"),
        }
    ],
    "temperature": 0.3,  # Low temp for financial decisions
    "timeout": 120,
}

# Cheaper model for routine agents (sentiment, data fetchers)
llm_config_lite = {
    "config_list": [
        {
            "model": "gpt-4o-mini",
            "api_key": os.getenv("OPENAI_API_KEY"),
        }
    ],
    "temperature": 0.2,
    "timeout": 60,
}
