from typing import Literal

from langchain.tools import tool


@tool
def calculator(
    a: float,
    b: float,
    operation: Literal["add", "subtract", "multiply", "divide"],
) -> str:
    """
    Perform basic arithmetic calculations.

    Use this tool when the user asks for addition, subtraction,
    multiplication, or division.

    Args:
        a: The first number.
        b: The second number.
        operation: The arithmetic operation to perform.
    """

    if operation == "add":
        result = a + b

    elif operation == "subtract":
        result = a - b

    elif operation == "multiply":
        result = a * b

    elif operation == "divide":
        if b == 0:
            return "错误：除数不能为0"

        result = a / b

    else:
        return "错误：未知计算类型"

    return str(result)