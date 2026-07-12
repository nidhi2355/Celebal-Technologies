"""
Calculator tool: safely evaluates arithmetic expressions extracted from
a natural-language query.

Exposes:
  - CALCULATOR_SCHEMA: JSON-schema-style definition of the tool's I/O contract
  - run(tool_input: dict) -> str
"""

import ast
import operator
import re


CALCULATOR_SCHEMA = {
    "name": "calculator",
    "description": "Evaluates a mathematical expression and returns the numeric result.",
    "input_schema": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "A mathematical expression, e.g. '12 * (3 + 4)'",
            }
        },
        "required": ["expression"],
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "result": {"type": "number"},
            "expression": {"type": "string"},
        },
    },
}

# Only these operators are allowed -- this is what makes eval-by-AST safe,
# unlike calling Python's raw eval() on user input.
_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_eval(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Only numeric constants are allowed.")
    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _ALLOWED_OPERATORS:
            raise ValueError(f"Operator {op_type.__name__} is not allowed.")
        return _ALLOWED_OPERATORS[op_type](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _ALLOWED_OPERATORS:
            raise ValueError(f"Operator {op_type.__name__} is not allowed.")
        return _ALLOWED_OPERATORS[op_type](_safe_eval(node.operand))
    raise ValueError(f"Unsupported expression element: {type(node).__name__}")


_ALLOWED_CHARS_PATTERN = re.compile(r"[\d\s.()+\-*/%^]+")


def _balance_parentheses(expr: str) -> str:
    depth = 0
    kept_chars = []
    for ch in expr:
        if ch == "(":
            depth += 1
            kept_chars.append(ch)
        elif ch == ")":
            if depth == 0:
                continue
            depth -= 1
            kept_chars.append(ch)
        else:
            kept_chars.append(ch)
    kept_chars.append(")" * depth)
    return "".join(kept_chars)


def extract_expression(query: str) -> str:
    """Pulls a math-looking substring out of a free-form query."""
    chunks = [c.strip() for c in _ALLOWED_CHARS_PATTERN.findall(query)]

    candidates = [c for c in chunks if re.search(r"\d", c)]
    if not candidates:
        raise ValueError("No mathematical expression found in query.")

    with_operator = [c for c in candidates if re.search(r"[+\-*/%^]", c)]
    chosen = max(with_operator, key=len, default=None) or max(candidates, key=len)

    expr = _balance_parentheses(chosen).replace("^", "**")
    if not expr:
        raise ValueError("No mathematical expression found in query.")
    return expr


def run(tool_input: dict) -> dict:
    """
    tool_input: {"expression": "<string>"}
    returns: {"result": <number>, "expression": "<string>"}
    raises: ValueError on invalid/unsafe expressions
    """
    expression = tool_input.get("expression", "")
    if not expression:
        raise ValueError("No expression provided to calculator tool.")

    try:
        parsed = ast.parse(expression, mode="eval").body
        result = _safe_eval(parsed)
    except (SyntaxError, ZeroDivisionError, ValueError) as e:
        raise ValueError(f"Could not evaluate expression '{expression}': {e}")

    return {"result": result, "expression": expression}
