"""
Neo chatbot — runnable CLI entry point.

Usage:
  python main.py
    Start interactive chatbot. Type your message and press Enter.
    A fresh session is created every run; previous session file is deleted
    before initializing. When the session ends (quit/exit/q), the session
    file is cleared automatically.
    Commands: 'quit', 'exit', or 'q' to end the session.

  python main.py "Your question here"
    Run a single query and exit. Uses a fresh session; session file is
    cleared when the run completes.

Environment:
  Loads .env automatically. Requires AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY,
  DEPLOYMENT_NAME, and optionally OPENAI_API_VERSION (default 2025-03-01-preview).
  NEO_SESSION_PATH: optional path to session file (default .neo_session.json).
    This file is deleted before each run and when the session ends.
"""

import asyncio
import os
import sys

from dotenv import load_dotenv

# Load .env so AZURE_OPENAI_* and DEPLOYMENT_NAME are available
load_dotenv()

from agent_framework import AgentSession
from agent_framework.exceptions import ChatClientException

from core.agent import create_agent
from core.memory import FileSessionStorage


# Commands that end the chatbot session (case-insensitive)
EXIT_COMMANDS = frozenset({"quit", "exit", "q"})

# InMemoryHistoryProvider state key used in agent.py (must match context_providers)
MEMORY_PROVIDER_SOURCE_ID = "memory"


def _clear_session_chat_history(session: AgentSession) -> None:
    """
    Task:
        Clear chat history in session state to avoid duplicate-item errors from the API.

    Input Parameters:
        session : AgentSession
            Session whose "memory" provider state will be cleared.

    Output Parameters:
        session.state["memory"]["messages"] is set to [].

    Returns:
        None.

    Raises:
        None.
    """
    state = session.state.setdefault(MEMORY_PROVIDER_SOURCE_ID, {})
    if isinstance(state, dict):
        state["messages"] = []


def _is_duplicate_item_error(ex: BaseException) -> bool:
    """
    Task:
        Detect whether the exception is due to duplicate item id from the API.

    Input Parameters:
        ex : BaseException
            The exception to inspect (and its __cause__).

    Output Parameters:
        None.

    Returns:
        bool
            True if "duplicate item" appears in the exception message; otherwise False.

    Raises:
        None.
    """
    msg = str(ex).lower()
    if "duplicate item" in msg:
        return True
    cause = getattr(ex, "__cause__", None)
    if cause is not None:
        if "duplicate item" in str(cause).lower():
            return True
    return False


def _clear_session_file() -> None:
    """
    Task:
        Delete the session file (e.g. .neo_session.json) if it exists so the next run starts fresh.

    Input Parameters:
        None.
        Uses NEO_SESSION_PATH or default path from _default_session_path().

    Output Parameters:
        None.
        The file at the session path is removed if present.

    Returns:
        None.

    Raises:
        None.
        FileNotFoundError and other OSErrors are ignored so startup is not blocked.
    """
    path = _default_session_path()
    try:
        if os.path.isfile(path):
            os.remove(path)
    except OSError:
        pass


def _default_session_path() -> str:
    """
    Task:
        Return the file path to use for persisting the session (env or default).

    Input Parameters:
        None.

    Output Parameters:
        None.

    Returns:
        str
            Value of NEO_SESSION_PATH if set, otherwise ".neo_session.json".

    Raises:
        None.
    """
    return os.environ.get("NEO_SESSION_PATH", ".neo_session.json")


def _get_storage() -> FileSessionStorage:
    """
    Task:
        Create and return the session storage instance (file-backed, path from env or default).

    Input Parameters:
        None.

    Output Parameters:
        None.

    Returns:
        FileSessionStorage
            Storage backed by the default or NEO_SESSION_PATH file.

    Raises:
        None.
    """
    return FileSessionStorage(_default_session_path())


def _create_fresh_session(agent) -> AgentSession:
    """
    Task:
        Create a new session using Microsoft Agent Framework (agent.create_session()).

    Input Parameters:
        agent : Agent
            Neo agent instance (from create_agent()).

    Output Parameters:
        None.

    Returns:
        AgentSession
            New session with empty state; no previous session data is loaded.

    Raises:
        None.
    """
    return agent.create_session()


def _save_session(session: AgentSession, storage: FileSessionStorage) -> None:
    """
    Task:
        Persist the session to storage (e.g. on exit) using session.to_dict().

    Input Parameters:
        session : AgentSession
            Current session to serialize.
        storage : FileSessionStorage
            Backing store to write to.

    Output Parameters:
        None.

    Returns:
        None.

    Raises:
        None.
        Errors during save are swallowed so exit is not blocked.
    """
    try:
        storage.save_session(session.to_dict())
    except Exception:
        pass


def _is_exit_command(text: str) -> bool:
    """
    Task:
        Determine whether the user input is a command to end the chatbot (quit/exit/q).

    Input Parameters:
        text : str
            Raw user input line.

    Output Parameters:
        None.

    Returns:
        bool
            True if stripped lowercased text is one of quit, exit, q; otherwise False.

    Raises:
        None.
    """
    return text.strip().lower() in EXIT_COMMANDS


async def run_turn(agent, user_input: str, session: AgentSession | None = None) -> None:
    """
    Task:
        Run one chatbot turn: print user message, call agent.run(), print Neo's reply and tool logs.
        Handles duplicate-item API errors by clearing session chat history and retrying once.
        Other errors are caught and reported in a user-friendly way.

    Input Parameters:
        agent : Agent
            Neo agent instance (from create_agent()).
        user_input : str
            User message string.
        session : AgentSession | None, optional
            If provided, passed to agent.run() for conversation history and user memory.

    Output Parameters:
        None.

    Returns:
        None.

    Raises:
        None.
        Exceptions from agent.run() are caught; duplicate-item triggers one retry after clearing history.
    """
    print(f"\nYou: {user_input}")
    print("-" * 50)

    async def _run():
        if session is not None:
            return await agent.run(user_input, session=session)
        return await agent.run(user_input)

    response = None
    try:
        response = await _run()
    except ChatClientException as e:
        # Recover from duplicate-item error (common with persisted session history)
        if session is not None and _is_duplicate_item_error(e):
            _clear_session_chat_history(session)
            try:
                response = await _run()
            except Exception as retry_ex:
                print(f"Neo: Sorry, I hit an error even after retry: {retry_ex}")
                print("-" * 50)
                return
        else:
            print(f"Neo: Sorry, the service reported an error: {e}")
            print("-" * 50)
            return
    except Exception as e:
        print(f"Neo: Something went wrong: {e}")
        print("-" * 50)
        return

    if response is not None:
        print("-" * 50)
        print(f"Neo: {response}\n")


async def run_chatbot(agent, session: AgentSession, storage: FileSessionStorage) -> None:
    """
    Task:
        Run the interactive Neo chatbot loop until the user types quit/exit/q.
        On exit, save session then clear the session file (fresh session next run).

    Input Parameters:
        agent : Agent
            Neo agent instance.
        session : AgentSession
            Session to use for all turns (conversation history and user memory).
        storage : FileSessionStorage
            Storage to save session to when the loop exits (before clearing the file).

    Output Parameters:
        None.

    Returns:
        None.

    Raises:
        None.
        EOFError from input() is handled (e.g. Ctrl+D). finally: save session, then _clear_session_file().
    """
    print("\nNeo (chatbot). Say hello or ask anything. For math, try e.g. 'Add 10 and 20'.")
    print("I'll remember your name if you tell me (e.g. 'My name is Alice').")
    print("Type 'quit', 'exit', or 'q' to end.\n")

    try:
        while True:
            try:
                user_input = input("You: ").strip()
            except EOFError:
                print("\nGoodbye.")
                break

            if not user_input:
                continue
            if _is_exit_command(user_input):
                print("Neo: Goodbye!\n")
                break

            await run_turn(agent, user_input, session=session)
    finally:
        # Save current session state, then clear session file so next run starts fresh
        _save_session(session, storage)
        _clear_session_file()


async def main() -> None:
    """
    Task:
        Entry point: create agent and storage, then run single-query or interactive chatbot.

    Input Parameters:
        None.
        Uses sys.argv to decide: single query if argv has args, else interactive loop.

    Output Parameters:
        None.

    Returns:
        None.

    Raises:
        Propagates exceptions from create_agent(), run_turn(), or run_chatbot().
    """
    # Delete previous session file before initializing so every run starts with fresh session state
    _clear_session_file()

    agent = create_agent()
    storage = _get_storage()

    # Create fresh session using Microsoft Agent Framework (no load from file)
    session = _create_fresh_session(agent)

    if len(sys.argv) > 1:
        # Single query from command line: run one turn, save then clear session file
        query = " ".join(sys.argv[1:])
        await run_turn(agent, query, session=session)
        _save_session(session, storage)
        _clear_session_file()
    else:
        # Interactive CLI chatbot: run loop; on exit run_chatbot finally saves and clears file
        await run_chatbot(agent, session, storage)


if __name__ == "__main__":
    asyncio.run(main())
