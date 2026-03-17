"""
Concurrent orchestration: multiple agents work on the same task in parallel.

Uses Microsoft Agent Framework ConcurrentBuilder with three domain agents
(researcher, marketer, legal). Loads Azure OpenAI settings from .env via config.
Run: python -m orchestration_concurrent.multi_agent
"""

from __future__ import annotations

import asyncio

try:
    from . import config
except ImportError:
    import config  # when run as python multi_agent.py from this directory


def _get_chat_client():
    """
    Task:
        Build Azure OpenAI Chat client used by the concurrent workflow.

    Input Parameters:
        None.

    Output Parameters:
        None.

    Returns:
        AzureOpenAIChatClient
            Client instance from config.get_azure_openai_chat_client().

    Raises:
        ValueError
            If required env vars are not set (propagated from config).
    """
    return config.get_azure_openai_chat_client()


def _build_workflow():
    """
    Task:
        Create three domain agents (researcher, marketer, legal) and a concurrent workflow.

    Input Parameters:
        None.

    Output Parameters:
        None.

    Returns:
        Workflow
            Built concurrent workflow with default aggregator.

    Raises:
        ValueError
            If config or participant setup fails (e.g. missing env vars).
    """
    from agent_framework.orchestrations import ConcurrentBuilder

    client = _get_chat_client()

    researcher = client.as_agent(
        instructions=(
            "You're an expert market and product researcher. Given a prompt, provide concise, factual insights,"
            " opportunities, and risks."
        ),
        name="researcher",
    )
    marketer = client.as_agent(
        instructions=(
            "You're a creative marketing strategist. Craft compelling value propositions and target messaging"
            " aligned to the prompt."
        ),
        name="marketer",
    )
    legal = client.as_agent(
        instructions=(
            "You're a cautious legal/compliance reviewer. Highlight constraints, disclaimers, and policy concerns"
            " based on the prompt."
        ),
        name="legal",
    )

    workflow = ConcurrentBuilder(participants=[researcher, marketer, legal]).build()
    return workflow


async def run_concurrent(prompt: str) -> list:
    """
    Task:
        Run the concurrent workflow with the given prompt and return aggregated messages.

        This loop Run through the workflow’s stream until you see an event of type output, 
        take its data (the list of messages), normalize it to a list, then return it and stop.
        So the script is effectively “run the concurrent workflow and give me the final aggregated messages.”

    Input Parameters:
        prompt : str
            User prompt sent to all agents in parallel.

    Output Parameters:
        None.

    Returns:
        list
            Aggregated list of Message from the default aggregator (user + one per agent).

    Raises:
        None.
    """
    workflow = _build_workflow()  # Build concurrent workflow (researcher, marketer, legal)
    stream = workflow.run(message=prompt, stream=True)  # Run with prompt, get event stream
    output_messages: list = []  # Will hold aggregated list of Message
    async for event in stream:
        if getattr(event, "type", None) == "output":  # Only care about final output event
            data = getattr(event, "data", None)  # Payload is list of Message
            if data is not None:
                output_messages = data if isinstance(data, list) else [data]  # Normalize to list
            break  # First output event is the aggregated result; stop consuming
    return output_messages


def _message_text(msg) -> str:
    """
    Task:
        Get display text from a Message (text attribute or contents).

    Input Parameters:
        msg : object
            Message-like object with optional .text or .contents.

    Output Parameters:
        None.

    Returns:
        str
            Message text, or "(no text)" / "(no content)" if missing.

    Raises:
        None.
    """
    if hasattr(msg, "text") and msg.text:
        return msg.text  # Prefer direct .text when present
    if hasattr(msg, "contents") and msg.contents:
        parts = []  # Collect text from each content item
        for c in msg.contents:
            if hasattr(c, "text") and c.text:
                parts.append(c.text)
        return "\n".join(parts) if parts else "(no text)"  # One line per part, or placeholder
    return "(no content)"  # No text or contents found


def main() -> None:
    """
    Task:
        Run the concurrent multi-agent workflow with a default prompt and print aggregated output.

    Input Parameters:
        None.

    Output Parameters:
        None.
        Prints "===== Final Aggregated Conversation (messages) =====" and each message by author.

    Returns:
        None.

    Raises:
        None.
    """
    default_prompt = (
        "We are launching a new budget-friendly electric bike for urban commuters."
    )
    messages = asyncio.run(run_concurrent(default_prompt))  # Run workflow, get aggregated list of Message
    print("===== Final Aggregated Conversation (messages) =====")  # Section header
    for i, msg in enumerate(messages, start=1):  # Loop with 1-based index (01, 02, ...)
        name = getattr(msg, "author_name", None) or "user"  # Author label or fallback to "user"
        text = _message_text(msg)  # Extract display text from message (text or contents)
        print(f"{'-' * 60}\n\n{i:02d} [{name}]:\n{text}")  # Separator, index, author, then body


if __name__ == "__main__":
    main()



"""
Questions

1. More focused / niche
"We're considering a B2B SaaS product for small restaurant inventory management."
"We plan to sell refurbished smartphones with a one-year warranty in emerging markets."
Good for: seeing how each agent handles a narrower, B2B or warranty-heavy topic.

2. Regulatory / sensitive
"We're launching a new dietary supplement that claims to support sleep and stress."
"We want to advertise a crypto investment product to retail users in the UK."
Good for: stressing the legal agent (claims, financial promotion) and checking researcher/marketer tone.

3. "We are launching a new budget-friendly electric bike for urban commuters."


"""