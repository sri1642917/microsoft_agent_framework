"""
Memory and persistence for the Eddie chatbot (Microsoft Agent Framework).

Provides:
- UserMemoryProvider: context provider that stores user info in session state
  and injects personalization instructions (e.g. user name).
- SessionStorage protocol and FileSessionStorage: pluggable storage for
  persisting session across process runs (customize how memory is stored).
"""

from __future__ import annotations

import json
import os
from typing import Any, Protocol

from agent_framework import AgentSession, BaseContextProvider, SessionContext


# ---------------------------------------------------------------------------
# User information: context provider (store user info, inject instructions)
# ---------------------------------------------------------------------------


class UserMemoryProvider(BaseContextProvider):
    """
    Task:
        Context provider that stores user info (e.g. name) in session state and injects
        personalization instructions before each agent run (Microsoft Agent Framework).

    Input Parameters:
        (constructor) source_id : str | None
            Optional source identifier; defaults to "user_memory" (state key in session.state).

    Output Parameters:
        None.

    Returns:
        N/A (class).

    Raises:
        None.
    """

    DEFAULT_SOURCE_ID = "user_memory"

    def __init__(self, source_id: str | None = None) -> None:
        super().__init__(source_id or self.DEFAULT_SOURCE_ID)

    async def before_run(
        self,
        *,
        agent: Any,
        session: AgentSession | None,
        context: SessionContext,
        state: dict[str, Any],
    ) -> None:
        """
        Task:
            Inject personalization instructions into context based on stored user info.

        Input Parameters:
            agent : Any
                The agent instance (unused; required by framework signature).
            session : AgentSession | None
                Current session (unused; state is provider-scoped).
            context : SessionContext
                Per-invocation context; instructions are added via extend_instructions.
            state : dict[str, Any]
                Provider-scoped state (e.g. session.state["user_memory"]). Read-only here.

        Output Parameters:
            context is mutated: instructions are extended.

        Returns:
            None.

        Raises:
            None.
        """
        user_name = state.get("user_name")
        if user_name:
            context.extend_instructions(
                self.source_id,
                f"The user's name is {user_name}. Always address them by name when appropriate.",
            )
        else:
            context.extend_instructions(
                self.source_id,
                "You don't know the user's name yet. Ask for it politely if relevant.",
            )

    async def after_run(
        self,
        *,
        agent: Any,
        session: AgentSession | None,
        context: SessionContext,
        state: dict[str, Any],
    ) -> None:
        """
        Task:
            Extract user info from input messages and store in session state (e.g. "my name is X").

        Input Parameters:
            agent : Any
                The agent instance (unused; required by framework signature).
            session : AgentSession | None
                Current session (unused).
            context : SessionContext
                Contains input_messages to scan for user name.
            state : dict[str, Any]
                Provider-scoped mutable state; we write state["user_name"] here.

        Output Parameters:
            state may be updated with "user_name" if detected in message text.

        Returns:
            None.

        Raises:
            None.
        """
        for msg in context.input_messages:
            text = msg.text if hasattr(msg, "text") else ""
            if isinstance(text, str) and "my name is" in text.lower():
                part = text.lower().split("my name is")[-1].strip()
                name = part.split()[0].capitalize() if part else ""
                if name:
                    state["user_name"] = name
                break


# ---------------------------------------------------------------------------
# Pluggable session storage (customize how memory is stored)
# ---------------------------------------------------------------------------


class SessionStorage(Protocol):
    """
    Task:
        Protocol for pluggable session storage (e.g. file or database).

    Input Parameters:
        N/A (protocol).

    Output Parameters:
        N/A.

    Returns:
        N/A.

    Raises:
        N/A.
    """

    def load_session(self) -> dict[str, Any] | None:
        """
        Task:
            Load serialized session data from the backing store.

        Input Parameters:
            None.

        Output Parameters:
            None.

        Returns:
            dict[str, Any] | None
                Session data suitable for AgentSession.from_dict(), or None if no data or error.

        Raises:
            None.
            Implementations should catch errors and return None.
        """
        ...

    def save_session(self, data: dict[str, Any]) -> None:
        """
        Task:
            Persist serialized session data to the backing store.

        Input Parameters:
            data : dict[str, Any]
                Output of AgentSession.to_dict().

        Output Parameters:
            None.

        Returns:
            None.

        Raises:
            None.
            Implementations should not raise; handle errors internally (e.g. log).
        """
        ...


class FileSessionStorage:
    """
    Task:
        Default session storage that reads/writes session data as JSON to a file.

    Input Parameters:
        (constructor) path : str
            File path for the JSON session file.

    Output Parameters:
        None.

    Returns:
        N/A (class).

    Raises:
        None.
    """

    def __init__(self, path: str) -> None:
        self._path = path

    def load_session(self) -> dict[str, Any] | None:
        """
        Task:
            Load session from the JSON file at self._path.

        Input Parameters:
            None.

        Output Parameters:
            None.

        Returns:
            dict[str, Any] | None
                Parsed JSON dict, or None if file is missing or invalid.

        Raises:
            None.
            OSError and JSONDecodeError are caught and None is returned.
        """
        if not os.path.isfile(self._path):
            return None
        try:
            with open(self._path, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return None

    def save_session(self, data: dict[str, Any]) -> None:
        """
        Task:
            Save session data to the JSON file at self._path.

        Input Parameters:
            data : dict[str, Any]
                Serialized session (e.g. from AgentSession.to_dict()).

        Output Parameters:
            None.

        Returns:
            None.

        Raises:
            None.
            On OSError, logs to stderr and continues (does not fail the process).
        """
        try:
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except OSError as e:
            # Graceful: do not fail the process on save errors
            import sys
            print(f"[Eddie] Could not save session: {e}", file=sys.stderr)
