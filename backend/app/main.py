"""
FastAPI application exposing FinRL-powered endpoints.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .finrl_integration import FinRLException, FinRLService
from .routers.predict import router as predict_router
from .schemas import BacktestResponse, SymbolRequest

app = FastAPI(
    title="FinRL Stock Prediction API",
    version="0.1.0",
    description=(
        "Educational backend that trains FinRL PPO agents on Yahoo Finance data "
        "to power price predictions and backtesting visualizations."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

service = FinRLService()
app.include_router(predict_router)


@app.get("/health")
async def healthcheck() -> dict:
    """Simple health endpoint used by deployment targets."""
    return {"status": "ok"}


@app.post("/api/backtest", response_model=BacktestResponse)
async def backtest_strategy(payload: SymbolRequest) -> BacktestResponse:
    """Expose FinRL backtest metrics for the requested ticker."""
    try:
        result = await run_in_threadpool(
            service.get_backtest_payload, payload.symbol
        )
    except FinRLException as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive path
        raise HTTPException(status_code=500, detail="Unexpected FinRL error") from exc
    return result
