"""Safe mathematical expression tokenizer and recursive-descent parser."""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, localcontext


class ExpressionError(ValueError):
    """Raised when an expression is empty, malformed, or unsupported."""


class DivisionByZeroError(ExpressionError):
    """Raised when an expression attempts to divide by zero."""


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    position: int


def tokenize(expression: str) -> list[Token]:
    """Convert an expression into numbers, operators, and parentheses."""
    normalized = expression.replace("×", "*").replace("÷", "/").replace("−", "-")
    tokens: list[Token] = []
    index = 0

    while index < len(normalized):
        char = normalized[index]

        if char.isspace():
            index += 1
            continue

        if char in "+-*/()":
            tokens.append(Token(char, char, index))
            index += 1
            continue

        if char.isdigit() or char == ".":
            start = index
            digit_count = 0

            while index < len(normalized) and normalized[index].isdigit():
                digit_count += 1
                index += 1

            if index < len(normalized) and normalized[index] == ".":
                index += 1
                while index < len(normalized) and normalized[index].isdigit():
                    digit_count += 1
                    index += 1

            if digit_count == 0:
                raise ExpressionError(f"位置 {start + 1} 的数字格式不正确")

            tokens.append(Token("NUMBER", normalized[start:index], start))
            continue

        raise ExpressionError(f"位置 {index + 1} 包含不支持的字符“{char}”")

    tokens.append(Token("EOF", "", len(normalized)))
    return tokens


class Parser:
    """Parse and calculate a token stream without executing user code."""

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.index = 0

    @property
    def current(self) -> Token:
        return self.tokens[self.index]

    def consume(self, kind: str) -> Token:
        token = self.current
        if token.kind != kind:
            shown = token.value or "表达式结尾"
            raise ExpressionError(f"位置 {token.position + 1} 附近存在语法错误：{shown}")
        self.index += 1
        return token

    def parse(self) -> Decimal:
        value = self.parse_expression()
        if self.current.kind != "EOF":
            token = self.current
            raise ExpressionError(f"位置 {token.position + 1} 附近存在多余内容：{token.value}")
        return value

    def parse_expression(self) -> Decimal:
        value = self.parse_term()
        while self.current.kind in {"+", "-"}:
            operator = self.current.kind
            self.index += 1
            right = self.parse_term()
            value = value + right if operator == "+" else value - right
        return value

    def parse_term(self) -> Decimal:
        value = self.parse_unary()
        while self.current.kind in {"*", "/"}:
            operator = self.current.kind
            self.index += 1
            right = self.parse_unary()
            if operator == "*":
                value *= right
            else:
                if right == 0:
                    raise DivisionByZeroError("除数不能为零")
                value /= right
        return value

    def parse_unary(self) -> Decimal:
        if self.current.kind == "+":
            self.index += 1
            return self.parse_unary()
        if self.current.kind == "-":
            self.index += 1
            return -self.parse_unary()
        return self.parse_primary()

    def parse_primary(self) -> Decimal:
        if self.current.kind == "NUMBER":
            token = self.consume("NUMBER")
            try:
                return Decimal(token.value)
            except InvalidOperation as error:
                raise ExpressionError(f"无法识别数字：{token.value}") from error

        if self.current.kind == "(":
            self.consume("(")
            value = self.parse_expression()
            self.consume(")")
            return value

        token = self.current
        shown = token.value or "表达式结尾"
        raise ExpressionError(f"位置 {token.position + 1} 缺少数字或括号：{shown}")


def evaluate_expression(expression: str) -> Decimal:
    """Validate and calculate an expression with decimal precision."""
    cleaned = expression.strip()
    if not cleaned:
        raise ExpressionError("表达式不能为空")
    if len(cleaned) > 200:
        raise ExpressionError("表达式长度不能超过 200 个字符")

    with localcontext() as context:
        context.prec = 28
        try:
            result = Parser(tokenize(cleaned)).parse()
        except InvalidOperation as error:
            raise ExpressionError("数字超出可计算范围") from error

    if not result.is_finite():
        raise ExpressionError("计算结果不是有限数值")
    return result


def format_decimal(value: Decimal) -> str:
    """Return a human-readable decimal string without unnecessary zeros."""
    if value == 0:
        return "0"
    normalized = format(value.normalize(), "f")
    return normalized.rstrip("0").rstrip(".") if "." in normalized else normalized


def decimal_to_json(value: Decimal) -> int | float:
    """Convert a Decimal to a JSON number for API responses."""
    if value == value.to_integral_value():
        return int(value)
    return float(value)

