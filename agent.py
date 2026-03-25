"""
Eddie chatbot agent using Microsoft Agent Framework.

Creates AzureOpenAIResponsesClient and an agent named "eddie" that:
- Responds conversationally to any general user question
- Detects arithmetic queries and invokes add, subtract, multiply, or divide via the framework
- Remembers conversation history and user info via context providers (memory)
- Uses only Microsoft Agent Framework syntax for agent creation and tool registration/calling
"""

from __future__ import annotations

import os
from typing import Sequence

from agent_framework import InMemoryHistoryProvider
from agent_framework.azure import AzureOpenAIResponsesClient

from memory import UserMemoryProvider
from tools import add, divide, multiply, subtract


def _default_context_providers() -> list:
    """
    Task:
        Return the default list of context providers for Eddie (chat history + user memory).

    Input Parameters:
        None.

    Output Parameters:
        None.

    Returns:
        list
            [InMemoryHistoryProvider("memory", load_messages=True), UserMemoryProvider()].
            Only one provider has load_messages=True per framework guidance.

    Raises:
        None.
    """
    return [
        InMemoryHistoryProvider("memory", load_messages=True),
        UserMemoryProvider(),
    ]


def create_agent(
    context_providers: Sequence | None = None,
):
    """
    Task:
        Build the Azure OpenAI client and return the Eddie chatbot agent with math tools and memory.

    Input Parameters:
        context_providers : Sequence | None, optional
            Custom list of context providers. If None, uses default (InMemoryHistoryProvider
            for chat history and UserMemoryProvider for user info). Only one provider
            should have load_messages=True.

    Output Parameters:
        None.

    Returns:
        Agent
            Agent instance with name "eddie", conversational instructions,
            tools [add, subtract, multiply, divide], and context_providers (Microsoft Agent Framework).

    Raises:
        KeyError
            If required env vars (AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, DEPLOYMENT_NAME) are missing.
    """
    # Resolve deployment name from env (framework supports both variable names)
    deployment_name = (
        os.environ.get("AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME")
        or os.environ["DEPLOYMENT_NAME"]
    )
    # Responses API requires api-version 2025-03-01-preview or later
    client = AzureOpenAIResponsesClient(
        endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        deployment_name=deployment_name,
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version=os.environ.get("OPENAI_API_VERSION", "2025-03-01-preview"),
    )
    # Use custom providers if given; otherwise default (history + user memory)
    providers = list(context_providers) if context_providers is not None else _default_context_providers()
    # Build agent with tools and context providers (Microsoft Agent Framework as_agent API)
    agent = client.as_agent(
        name="eddie",
        instructions=(
            "You are Eddie, a friendly and helpful chatbot. "
            "Respond conversationally to any general question the user asks. "
            "When the user asks for arithmetic (add, subtract, multiply, divide, sum, difference, "
            "product, quotient, or similar), you MUST call the appropriate tool for EVERY "
            "mathematical operation requested. Do NOT perform any math internally. "
            "For compound requests (e.g., 'multiply 2 and 3 then divide by 6'), you MUST call "
            "the tools sequentially or in parallel as needed (e.g., call 'multiply' first, then "
            "use the result to call 'divide'). All math tools now accept a list of numbers. "
            "Reply with the final result in a natural way. "
            "For non-arithmetic questions, answer from your knowledge without calling any tool. "
            "Keep responses clear and concise."
        ),
        tools=[add, subtract, multiply, divide],
        context_providers=providers,
    )
    return agent
