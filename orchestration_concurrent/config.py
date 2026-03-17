"""
Config helper for orchestration_concurrent: loads .env and provides Azure OpenAI Chat client settings.

Reusable by multi_agent.py and other orchestration samples. Uses:
- AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, OPENAI_API_VERSION
- AZURE_OPENAI_CHAT_DEPLOYMENT_NAME or DEPLOYMENT_NAME for the Chat API deployment.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


def get_chat_deployment_name() -> str:
    """
    Task:
        Resolve Chat API deployment name from environment variables.

    Input Parameters:
        None.

    Output Parameters:
        None.

    Returns:
        str
            Value of AZURE_OPENAI_CHAT_DEPLOYMENT_NAME or DEPLOYMENT_NAME.

    Raises:
        ValueError
            If neither AZURE_OPENAI_CHAT_DEPLOYMENT_NAME nor DEPLOYMENT_NAME is set.
    """
    name = os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME") or os.environ.get("DEPLOYMENT_NAME")
    if not name:
        raise ValueError(
            "Set AZURE_OPENAI_CHAT_DEPLOYMENT_NAME or DEPLOYMENT_NAME in .env or environment."
        )
    return name


def get_azure_openai_chat_client():
    """
    Task:
        Build Azure OpenAI Chat client from .env or environment (for workflows/orchestrations).

    Input Parameters:
        None.
        Uses AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, OPENAI_API_VERSION, and deployment name.

    Output Parameters:
        None.

    Returns:
        AzureOpenAIChatClient
            Configured client instance.

    Raises:
        ValueError
            If AZURE_OPENAI_ENDPOINT or AZURE_OPENAI_API_KEY is missing, or deployment name is missing.
    """
    from agent_framework.azure import AzureOpenAIChatClient

    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    api_version = os.environ.get("OPENAI_API_VERSION", "2025-03-01-preview")
    if not endpoint or not api_key:
        raise ValueError(
            "Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY in .env or environment."
        )
    return AzureOpenAIChatClient(
        endpoint=endpoint,
        api_key=api_key,
        deployment_name=get_chat_deployment_name(),
        api_version=api_version,
    )
