from decimal import Decimal

import pytest

from app.calculator import DivisionByZeroError, ExpressionError, evaluate_expression


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("12+8", Decimal("20")),
        ("8-3*2", Decimal("2")),
        ("(1+2)*3", Decimal("9")),
        ("10/4", Decimal("2.5")),
        ("1.5+2.7", Decimal("4.2")),
        ("-5+8", Decimal("3")),
        ("3*-2", Decimal("-6")),
        ("--5", Decimal("5")),
        ("2 × (3 + 4)", Decimal("14")),
    ],
)
def test_valid_expressions(expression, expected):
    assert evaluate_expression(expression) == expected


@pytest.mark.parametrize("expression", ["", "1+++", "2(3)", "abc", "(1+2", "."])
def test_invalid_expressions(expression):
    with pytest.raises(ExpressionError):
        evaluate_expression(expression)


def test_division_by_zero():
    with pytest.raises(DivisionByZeroError):
        evaluate_expression("5/(3-3)")

