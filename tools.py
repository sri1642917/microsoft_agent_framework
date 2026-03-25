"""
Math tools for the Eddie agent (Microsoft Agent Framework).

Each tool is a separate callable with @tool and typed parameters.
Tools log invocations to the terminal: tool name, inputs, and result.
"""

from typing import Annotated

from agent_framework import tool
from pydantic import Field


# ---------------------------------------------------------------------------
# Internal implementations (used by @tool wrappers for logging)
# ---------------------------------------------------------------------------


def _add_impl(numbers: list[float]) -> str:
    """
    Task:
        Compute the sum of a list of numbers.

    Input Parameters:
        numbers : list[float]
            The list of numbers to sum.

    Output Parameters:
        None.

    Returns:
        str
            A message of the form "The result is {sum(numbers)}".

    Raises:
        None.
    """
    return f"The result is {sum(numbers)}"


def _subtract_impl(numbers: list[float]) -> str:
    """
    Task:
        Compute the difference: numbers[0] - sum(numbers[1:]).

    Input Parameters:
        numbers : list[float]
            The list of numbers to subtract.

    Output Parameters:
        None.

    Returns:
        str
            A message of the form "The result is {numbers[0] - sum(numbers[1:])}".

    Raises:
        None.
    """
    if not numbers:
        return "The result is 0"
    res = numbers[0] - sum(numbers[1:])
    return f"The result is {res}"


def _multiply_impl(numbers: list[float]) -> str:
    """
    Task:
        Compute the product of a list of numbers.

    Input Parameters:
        numbers : list[float]
            The list of factors.

    Output Parameters:
        None.

    Returns:
        str
            A message of the form "The result is {product}".

    Raises:
        None.
    """
    if not numbers:
        return "The result is 0"
    res = 1.0
    for n in numbers:
        res *= n
    return f"The result is {res}"


def _divide_impl(numbers: list[float]) -> str:
    """
    Task:
        Compute the quotient numbers[0] / product(numbers[1:]).
        Division by zero returns an error message.

    Input Parameters:
        numbers : list[float]
            The list of numbers (dividend then divisors).

    Output Parameters:
        None.

    Returns:
        str
            "The result is {quotient}" or "Error: Cannot divide by zero."

    Raises:
        None.
    """
    if not numbers:
        return "The result is 0"
    if len(numbers) == 1:
        return f"The result is {numbers[0]}"
    
    # Check for zero in divisors
    for n in numbers[1:]:
        if n == 0:
            return "Error: Cannot divide by zero."
            
    res = numbers[0]
    for n in numbers[1:]:
        res /= n
    return f"The result is {res}"


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
    numbers: Annotated[list[float], Field(description="List of numbers to add. Use when the user asks to add, sum, or combine multiple numbers.")],
) -> str:
    """
    Task:
        Add multiple numbers. Use when the user asks to add, sum, or combine two or more numbers.

    Input Parameters:
        numbers : list[float]
            The numbers to sum.

    Output Parameters:
        None.

    Returns:
        str
            Message "The result is {sum(numbers)}".

    Raises:
        None.
    """
    print("[Detected intent] arithmetic (addition)")
    print("[Tool called] add")
    print(f"[Input parameters] numbers={numbers}")
    result = _add_impl(numbers)
    print(f"[Result] {_format_result_for_log(result)}")
    return result


@tool(approval_mode="never_require")
def subtract(
    numbers: Annotated[list[float], Field(description="List of numbers for subtraction. Logic: numbers[0] - sum(numbers[1:]).")],
) -> str:
    """
    Task:
        Subtract numbers sequentially. Logic: numbers[0] - sum(numbers[1:]).
        Use for 'minus', 'difference', or when subtracting multiple values from a total.

    Input Parameters:
        numbers : list[float]
            The numbers to subtract.

    Output Parameters:
        None.

    Returns:
        str
            Message "The result is {res}".

    Raises:
        None.
    """
    print("[Detected intent] arithmetic (subtraction)")
    print("[Tool called] subtract")
    print(f"[Input parameters] numbers={numbers}")
    result = _subtract_impl(numbers)
    print(f"[Result] {_format_result_for_log(result)}")
    return result


@tool(approval_mode="never_require")
def multiply(
    numbers: Annotated[list[float], Field(description="List of numbers to multiply.")],
) -> str:
    """
    Task:
        Multiply multiple numbers. Use for 'times', 'multiply', or product of several numbers.

    Input Parameters:
        numbers : list[float]
            The numbers to multiply.

    Output Parameters:
        None.

    Returns:
        str
            Message "The result is {res}".

    Raises:
        None.
    """
    print("[Detected intent] arithmetic (multiplication)")
    print("[Tool called] multiply")
    print(f"[Input parameters] numbers={numbers}")
    result = _multiply_impl(numbers)
    print(f"[Result] {_format_result_for_log(result)}")
    return result


@tool(approval_mode="never_require")
def divide(
    numbers: Annotated[list[float], Field(description="List of numbers for division. Logic: numbers[0] / product(numbers[1:]).")],
) -> str:
    """
    Task:
        Divide numbers sequentially. Logic: numbers[0] / product(numbers[1:]).
        Use for 'divided by' or quotient questions involving multiple divisors.

    Input Parameters:
        numbers : list[float]
            The numbers to divide.

    Output Parameters:
        None.

    Returns:
        str
            "The result is {res}" or "Error: Cannot divide by zero."

    Raises:
        None.
    """
    print("[Detected intent] arithmetic (division)")
    print("[Tool called] divide")
    print(f"[Input parameters] numbers={numbers}")
    result = _divide_impl(numbers)
    print(f"[Result] {_format_result_for_log(result)}")
    return result
