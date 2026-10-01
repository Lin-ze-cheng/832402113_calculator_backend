"""FastAPI entry point for the calculator backend."""

import os
from contextlib import asynccontextmanager
from datetime import datetime
from decimal import Decimal

from fastapi import FastAPI, Query
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.calculator import (
    DivisionByZeroError,
    ExpressionError,
    decimal_to_json,
    evaluate_expression,
    format_decimal,
)
from app.database import clear_history, create_history, delete_history, init_database, list_history
from app.schemas import CalculateRequest


def configured_origins() -> list[str]:
    raw_origins = os.getenv("CALCULATOR_CORS_ORIGINS", "*")
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_database()
    yield


app = FastAPI(
    title="前后端分离计算器 API",
    version="1.0.0",
    description="负责安全表达式计算和 SQLite 历史记录持久化。",
    lifespan=lifespan,
)

origins = configured_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exception: RequestValidationError):
    first_error = exception.errors()[0] if exception.errors() else {}
    message = first_error.get("msg", "请求参数不正确")
    return JSONResponse(status_code=422, content={"success": False, "message": message})


@app.get("/api/health")
def health_check() -> dict[str, str | bool]:
    return {"success": True, "status": "ok"}


@app.post("/api/calculate")
def calculate(payload: CalculateRequest):
    try:
        result = evaluate_expression(payload.expression)
    except DivisionByZeroError as error:
        return JSONResponse(status_code=400, content={"success": False, "message": str(error)})
    except ExpressionError as error:
        return JSONResponse(status_code=400, content={"success": False, "message": str(error)})

    created_at = datetime.now().astimezone().isoformat(timespec="seconds")
    result_text = format_decimal(result)
    record = create_history(payload.expression, result_text, created_at)

    return {
        "success": True,
        "expression": payload.expression,
        "result": decimal_to_json(result),
        "history_id": record["id"],
        "created_at": created_at,
    }


def history_result_to_json(value: str) -> int | float | str:
    try:
        return decimal_to_json(Decimal(value))
    except Exception:
        return value


@app.get("/api/history")
def get_history(limit: int = Query(default=100, ge=1, le=500)):
    records = list_history(limit)
    for record in records:
        record["result"] = history_result_to_json(record["result"])
    return {"success": True, "items": records, "count": len(records)}


@app.delete("/api/history/{record_id}")
def remove_history(record_id: int):
    if record_id <= 0 or not delete_history(record_id):
        return JSONResponse(
            status_code=404,
            content={"success": False, "message": "未找到指定的历史记录"},
        )
    return {"success": True, "message": "历史记录已删除", "id": record_id}


@app.delete("/api/history")
def remove_all_history():
    deleted_count = clear_history()
    return {
        "success": True,
        "message": "全部历史记录已清空",
        "deleted_count": deleted_count,
    }

