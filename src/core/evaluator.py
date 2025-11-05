"""Expression evaluator for the calculator application.

Implements a tokenizer, shunting-yard parser, and reverse polish notation
interpreter to safely evaluate arithmetic expressions without relying on
Python's ``eval`` or ``ast`` based evaluation.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, DivisionByZero, DivisionUndefined, InvalidOperation, getcontext
from typing import Callable, Iterable, List

__all__ = [
    "EvaluationError",
    "ExpressionEvaluator",
]

# Increase the precision to support common calculator use-cases involving
# recurring decimals while keeping performance reasonable.
getcontext().prec = 28


class EvaluationError(Exception):
    """Raised when an expression cannot be evaluated safely."""


@dataclass(frozen=True)
class Operator:
    precedence: int
    associativity: str  # "L" for left, "R" for right
    operands: int
    function: Callable[..., Decimal]


class ExpressionEvaluator:
    """Safely evaluate arithmetic expressions."""

    _OPERATORS = {
        "+": Operator(1, "L", 2, lambda a, b: a + b),
        "-": Operator(1, "L", 2, lambda a, b: a - b),
        "*": Operator(2, "L", 2, lambda a, b: a * b),
        "/": Operator(2, "L", 2, lambda a, b: a / b),
        "%": Operator(3, "L", 1, lambda a: a / Decimal("100")),
        "u-": Operator(4, "R", 1, lambda a: -a),
    }

    _REPLACEMENTS = {
        "×": "*",
        "÷": "/",
        "−": "-",
    }

    def evaluate(self, expression: str) -> Decimal:
        """Evaluate an arithmetic expression and return the result as ``Decimal``.

        Parameters
        ----------
        expression:
            The expression to evaluate. Supports +, -, ×/-, *, ÷, /, %, unary minus
            and parentheses.

        Returns
        -------
        decimal.Decimal
            The result of the evaluated expression.

        Raises
        ------
        EvaluationError
            If the expression contains invalid syntax or cannot be evaluated.
        ZeroDivisionError
            If division by zero is attempted.
        """

        cleaned = self._normalise_expression(expression)
        tokens = self._tokenise(cleaned)
        rpn = self._to_rpn(tokens)
        return self._evaluate_rpn(rpn)

    # ------------------------------------------------------------------
    # Tokenisation and parsing helpers
    # ------------------------------------------------------------------
    @classmethod
    def _normalise_expression(cls, expression: str) -> str:
        normalised = expression.replace(" ", "")
        for original, replacement in cls._REPLACEMENTS.items():
            normalised = normalised.replace(original, replacement)
        return normalised

    @staticmethod
    def _is_number(token: str) -> bool:
        if not token:
            return False
        if token.count(".") > 1:
            return False
        if token == ".":
            return False
        try:
            Decimal(token)
        except InvalidOperation:
            return False
        return True

    @classmethod
    def _tokenise(cls, expression: str) -> List[str]:
        tokens: List[str] = []
        i = 0
        length = len(expression)
        while i < length:
            ch = expression[i]
            if ch.isdigit() or ch == ".":
                start = i
                i += 1
                while i < length and (expression[i].isdigit() or expression[i] == "."):
                    i += 1
                token = expression[start:i]
                if token.count(".") > 1:
                    raise EvaluationError("Invalid numeric literal")
                tokens.append(token)
                continue
            if ch in "+-*/()%":
                tokens.append(ch)
                i += 1
                continue
            raise EvaluationError(f"Invalid character in expression: '{ch}'")
        return cls._handle_unary_minus(tokens)

    @classmethod
    def _handle_unary_minus(cls, tokens: Iterable[str]) -> List[str]:
        processed: List[str] = []
        prev_token: str | None = None
        for token in tokens:
            if token == "-":
                if prev_token is None or prev_token in cls._OPERATORS or prev_token == "(":
                    processed.append("u-")
                else:
                    processed.append(token)
            else:
                processed.append(token)
            if token != "%":  # percent is postfix and does not change unary detection
                prev_token = processed[-1]
        return processed

    @classmethod
    def _to_rpn(cls, tokens: Iterable[str]) -> List[str]:
        output: List[str] = []
        stack: List[str] = []
        for token in tokens:
            if cls._is_number(token):
                output.append(token)
                continue
            if token == "(":
                stack.append(token)
                continue
            if token == ")":
                while stack and stack[-1] != "(":
                    output.append(stack.pop())
                if not stack or stack[-1] != "(":
                    raise EvaluationError("Mismatched parentheses")
                stack.pop()  # remove '('
                continue
            if token in cls._OPERATORS:
                op_token = token
                op_info = cls._OPERATORS[op_token]
                while stack:
                    top = stack[-1]
                    if top == "(":
                        break
                    top_info = cls._OPERATORS.get(top)
                    if top_info is None:
                        break
                    if (
                        (op_info.associativity == "L" and op_info.precedence <= top_info.precedence)
                        or (
                            op_info.associativity == "R"
                            and op_info.precedence < top_info.precedence
                        )
                    ):
                        output.append(stack.pop())
                    else:
                        break
                stack.append(op_token)
                continue
            raise EvaluationError(f"Unknown token: {token}")

        while stack:
            top = stack.pop()
            if top in {"(", ")"}:
                raise EvaluationError("Mismatched parentheses")
            output.append(top)
        return output

    @classmethod
    def _evaluate_rpn(cls, tokens: Iterable[str]) -> Decimal:
        stack: List[Decimal] = []
        for token in tokens:
            if cls._is_number(token):
                stack.append(Decimal(token))
                continue
            operator = cls._OPERATORS.get(token)
            if operator is None:
                raise EvaluationError(f"Unknown operator during evaluation: {token}")
            if len(stack) < operator.operands:
                raise EvaluationError("Insufficient operands")
            try:
                if operator.operands == 1:
                    a = stack.pop()
                    result = operator.function(a)
                else:
                    b = stack.pop()
                    a = stack.pop()
                    result = operator.function(a, b)
            except (DivisionByZero, DivisionUndefined) as exc:
                raise ZeroDivisionError("Division by zero") from exc
            except InvalidOperation as exc:
                raise EvaluationError("Invalid operation") from exc
            stack.append(result)
        if len(stack) != 1:
            raise EvaluationError("Malformed expression")
        return stack[0]

    @staticmethod
    def format_decimal(value: Decimal) -> str:
        """Format a Decimal into a user-friendly string for display."""
        normalized = value.normalize()
        text = format(normalized, "f")
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        if text in {"-0", "-0.0"}:
            return "0"
        return text
