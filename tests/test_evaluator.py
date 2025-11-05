from __future__ import annotations

import pytest

from decimal import Decimal

from src.core.evaluator import EvaluationError, ExpressionEvaluator


evaluator = ExpressionEvaluator()


@pytest.mark.parametrize(
    "expression, expected",
    [
        ("2+3", Decimal("5")),
        ("2+3*4", Decimal("14")),
        ("10/2+3", Decimal("8")),
        ("5-10", Decimal("-5")),
        ("2.5+4.75", Decimal("7.25")),
        ("0.1+0.2", Decimal("0.3")),
        ("1/3", pytest.approx(1 / 3, rel=1e-10)),
        ("(.5+.5)*4", Decimal("4")),
        ("3+-2", Decimal("1")),
        ("200*10%", Decimal("20")),
        ("50%", Decimal("0.5")),
        ("200/4/5", Decimal("10")),
        ("((2+3)*4)-5", Decimal("15")),
        ("5--3", Decimal("8")),
        ("12÷4", Decimal("3")),
        ("7×8-4", Decimal("52")),
        ("1.5×2.0", Decimal("3")),
        ("-.5+1", Decimal("0.5")),
        ("(((((1+1)))))", Decimal("2")),
        ("10-3*2+4/2", Decimal("6")),
        ("5-2+3-4+6", Decimal("8")),
    ],
)
def test_expression_evaluation(expression, expected):
    result = evaluator.evaluate(expression)
    if isinstance(expected, Decimal):
        assert result == expected
    else:
        assert float(result) == expected


def test_division_by_zero():
    with pytest.raises(ZeroDivisionError):
        evaluator.evaluate("0/0")


@pytest.mark.parametrize(
    "expression",
    [
        "5++",
        "abc",
        "(1+2",
        "1//2",
    ],
)
def test_invalid_expressions_raise(expression):
    with pytest.raises(EvaluationError):
        evaluator.evaluate(expression)
