"""
Pydantic request/response models exposed by the FastAPI layer.
"""

from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, constr


class SymbolRequest(BaseModel):
    """Incoming payload containing the ticker to process."""

    symbol: constr(strip_whitespace=True, min_length=1) = Field(
        ..., description="Ticker symbol supported by Yahoo Finance."
    )


class PricePoint(BaseModel):
    date: datetime
    value: float


class PredictionPoint(BaseModel):
    date: datetime
    predicted_close: float


class PredictionResponse(BaseModel):
    symbol: str
    latest_close: float
    predicted_next_close: float
    delta: float
    delta_pct: float
    generated_at: datetime
    price_history: List[PricePoint]
    prediction_point: PredictionPoint
    disclaimer: str


class EquityPoint(BaseModel):
    date: datetime
    equity: float


class PriceComparisonRow(BaseModel):
    date: datetime
    actual_close: float
    predicted_close: float


class BacktestMetrics(BaseModel):
    final_equity: float
    total_return_pct: float
    sharpe_ratio: float
    max_drawdown_pct: float


class BacktestResponse(BaseModel):
    symbol: str
    generated_at: datetime
    equity_curve: List[EquityPoint]
    price_comparison: List[PriceComparisonRow]
    metrics: BacktestMetrics
    disclaimer: str
