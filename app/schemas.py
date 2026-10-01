"""Request schemas used by the calculator API."""

from pydantic import BaseModel, Field, field_validator


class CalculateRequest(BaseModel):
    expression: str = Field(min_length=1, max_length=200)

    @field_validator("expression")
    @classmethod
    def expression_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("表达式不能为空")
        return cleaned

