"""
Math tools for the Neo agent (Microsoft Agent Framework).

Each tool is a separate callable with @tool and typed parameters.
Tools log invocations to the terminal: tool name, inputs, and result.
"""

from typing import Annotated

from agent_framework import tool
from pydantic import Field


# ---------------------------------------------------------------------------
# Internal implementations (used by @tool wrappers for logging)
# ---------------------------------------------------------------------------


def _add_impl(a: float, b: float) -> str:
    """
    Task:
        Compute the sum of two numbers.

    Input Parameters:
        a : float
            First operand.
        b : float
            Second operand.

    Output Parameters:
        None.

    Returns:
        str
            A message of the form "The result is {a + b}".

    Raises:
        None.
    """
    return f"The result is {a + b}"


def _subtract_impl(a: float, b: float) -> str:
    """
    Task:
        Compute the difference (a - b).

    Input Parameters:
        a : float
            Minuend (number to subtract from).
        b : float
            Subtrahend (number to subtract).

    Output Parameters:
        None.

    Returns:
        str
            A message of the form "The result is {a - b}".

    Raises:
        None.
    """
    return f"The result is {a - b}"


def _multiply_impl(a: float, b: float) -> str:
    """
    Task:
        Compute the product of two numbers.

    Input Parameters:
        a : float
            First factor.
        b : float
            Second factor.

    Output Parameters:
        None.

    Returns:
        str
            A message of the form "The result is {a * b}".

    Raises:
        None.
    """
    return f"The result is {a * b}"


def _divide_impl(a: float, b: float) -> str:
    """
    Task:
        Compute the quotient a / b. Division by zero returns an error message.

    Input Parameters:
        a : float
            Dividend.
        b : float
            Divisor.

    Output Parameters:
        None.

    Returns:
        str
            "The result is {a / b}" or "Error: Cannot divide by zero." if b == 0.

    Raises:
        None.
    """
    if b == 0:
        return "Error: Cannot divide by zero."
    return f"The result is {a / b}"


def _format_result_for_log(result: str) -> str:
    """
    Task:
        Extract a short string for terminal logging (numeric result or error message).

    Input Parameters:
        result : str
            Tool return value (e.g. "The result is 30" or "Error: Cannot divide by zero.").

    Output Parameters:
        None.

    Returns:
        str
            The part after "The result is " if present, otherwise result unchanged.

    Raises:
        None.
    """
    if result.startswith("The result is "):
        return result.replace("The result is ", "").strip()
    return result


# ---------------------------------------------------------------------------
# Tool wrappers with @tool and terminal logging (Microsoft Agent Framework)
# ---------------------------------------------------------------------------
# Each wrapper logs: [Detected intent], [Tool called], [Input parameters], [Result].
# NOTE: approval_mode="never_require" for sample; use "always_require" in production.


@tool(approval_mode="never_require")
def add(
    a: Annotated[float, Field(description="First number.")],
    b: Annotated[float, Field(description="Second number.")],
) -> str:
    """
    Task:
        Add two numbers. Use when the user asks to add, sum, or combine two numbers.

    Input Parameters:
        a : float
            First number.
        b : float
            Second number.

    Output Parameters:
        None.

    Returns:
        str
            Message "The result is {a + b}".

    Raises:
        None.
    """
    print("[Detected intent] arithmetic (addition)")
    print("[Tool called] add")
    print(f"[Input parameters] a={a}, b={b}")
    result = _add_impl(a, b)
    print(f"[Result] {_format_result_for_log(result)}")
    return result


@tool(approval_mode="never_require")
def subtract(
    a: Annotated[float, Field(description="Number to subtract from (minuend).")],
    b: Annotated[float, Field(description="Number to subtract (subtrahend).")],
) -> str:
    """
    Task:
        Subtract the second number from the first. Use for subtraction or 'minus' questions.

    Input Parameters:
        a : float
            Minuend.
        b : float
            Subtrahend.

    Output Parameters:
        None.

    Returns:
        str
            Message "The result is {a - b}".

    Raises:
        None.
    """
    print("[Detected intent] arithmetic (subtraction)")
    print("[Tool called] subtract")
    print(f"[Input parameters] a={a}, b={b}")
    result = _subtract_impl(a, b)
    print(f"[Result] {_format_result_for_log(result)}")
    return result


@tool(approval_mode="never_require")
def multiply(
    a: Annotated[float, Field(description="First number.")],
    b: Annotated[float, Field(description="Second number.")],
) -> str:
    """
    Task:
        Multiply two numbers. Use for 'times', 'multiply', or product questions.

    Input Parameters:
        a : float
            First factor.
        b : float
            Second factor.

    Output Parameters:
        None.

    Returns:
        str
            Message "The result is {a * b}".

    Raises:
        None.
    """
    print("[Detected intent] arithmetic (multiplication)")
    print("[Tool called] multiply")
    print(f"[Input parameters] a={a}, b={b}")
    result = _multiply_impl(a, b)
    print(f"[Result] {_format_result_for_log(result)}")
    return result


@tool(approval_mode="never_require")
def divide(
    a: Annotated[float, Field(description="Dividend (number to be divided).")],
    b: Annotated[float, Field(description="Divisor (number to divide by).")],
) -> str:
    """
    Task:
        Divide the first number by the second. Use for division or 'divided by'. Cannot divide by zero.

    Input Parameters:
        a : float
            Dividend.
        b : float
            Divisor.

    Output Parameters:
        None.

    Returns:
        str
            "The result is {a/b}" or "Error: Cannot divide by zero." if b == 0.

    Raises:
        None.
    """
    print("[Detected intent] arithmetic (division)")
    print("[Tool called] divide")
    print(f"[Input parameters] a={a}, b={b}")
    result = _divide_impl(a, b)
    print(f"[Result] {_format_result_for_log(result)}")
    return result
