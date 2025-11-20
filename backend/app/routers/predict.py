"""
Prediction router that loads a trained PPO model and produces next-day signals.
"""

from __future__ import annotations

import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from finrl.agents.stablebaselines3.models import DRLAgent
from finrl.config import INDICATORS
from finrl.meta.env_stock_trading.env_stocktrading import StockTradingEnv
from finrl.meta.preprocessor.preprocessors import FeatureEngineer
from stable_baselines3 import PPO

from ..schemas import PredictionResponse, SymbolRequest
from ..yfinance_client import download_price_history

MODEL_PATH = Path(__file__).resolve().parents[2] / "ppo_model.zip"
LOOKBACK_DAYS = 365
DISCLAIMER_TEXT = (
    "Educational use only. These FinRL-driven simulations are NOT financial advice."
)

router = APIRouter(prefix="/api", tags=["predictions"])

_model_cache: Dict[str, PPO] = {}
_model_lock = threading.Lock()


def _load_model() -> PPO:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Missing PPO model at {MODEL_PATH}. Train one via `python3 train_model.py`."
        )
    with _model_lock:
        cached = _model_cache.get("ppo")
        if cached is not None:
            return cached
        model = PPO.load(MODEL_PATH, device="cpu")
        _model_cache["ppo"] = model
        return model


def _fetch_market_data(symbol: str) -> pd.DataFrame:
    end = datetime.utcnow()
    start = end - timedelta(days=LOOKBACK_DAYS)
    try:
        data = download_price_history(symbol, start, end)
    except RuntimeError as exc:
        raise ValueError(str(exc)) from exc
    if data.empty:
        raise ValueError(f"No Yahoo Finance data returned for {symbol}.")
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [str(col[0]) for col in data.columns]
    frame = data.reset_index()
    frame["date"] = pd.to_datetime(frame["Date"]).dt.tz_localize(None)
    frame["tic"] = symbol
    frame = frame[
        ["date", "tic", "Open", "High", "Low", "Close", "Adj Close", "Volume"]
    ].rename(
        columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Adj Close": "adj_close",
            "Volume": "volume",
        }
    )
    frame = frame.dropna().sort_values("date")
    if frame.empty or len(frame) < 30:
        raise ValueError(f"Insufficient historical data for {symbol}.")
    return frame


def _engineer_features(raw_df: pd.DataFrame) -> pd.DataFrame:
    fe = FeatureEngineer(
        use_technical_indicator=True,
        tech_indicator_list=INDICATORS,
        use_turbulence=False,
        user_defined_feature=False,
    )
    processed = fe.preprocess_data(raw_df)
    return processed.ffill().dropna()


def _build_env_kwargs(stock_dim: int) -> Dict:
    state_space = 1 + 2 * stock_dim + len(INDICATORS) * stock_dim
    return {
        "hmax": 100,
        "initial_amount": 100_000,
        "buy_cost_pct": [0.001] * stock_dim,
        "sell_cost_pct": [0.001] * stock_dim,
        "state_space": state_space,
        "stock_dim": stock_dim,
        "tech_indicator_list": INDICATORS,
        "action_space": stock_dim,
        "reward_scaling": 1e-4,
        "num_stock_shares": [0] * stock_dim,
    }


def _to_datetime(value: pd.Timestamp) -> datetime:
    as_dt = value.to_pydatetime()
    if as_dt.tzinfo:
        as_dt = as_dt.astimezone(timezone.utc).replace(tzinfo=None)
    return as_dt


def _action_to_scalar(action_val) -> float:
    if isinstance(action_val, (list, tuple, np.ndarray)):
        return float(action_val[0]) if action_val else 0.0
    return float(action_val)


def _estimate_price(latest_close: float, action: Optional[float], hmax: int) -> float:
    if action is None:
        return latest_close
    signal = np.tanh(action / hmax)
    return round(latest_close * (1 + signal * 0.01), 4)


def _run_prediction(symbol: str) -> PredictionResponse:
    model = _load_model()
    raw_df = _fetch_market_data(symbol)
    processed_df = _engineer_features(raw_df)
    stock_dim = len(processed_df.tic.unique())
    env_kwargs = _build_env_kwargs(stock_dim)
    trade_env = StockTradingEnv(df=processed_df, **env_kwargs)
    _, actions = DRLAgent.DRL_prediction(model=model, environment=trade_env)
    latest_row = raw_df.iloc[-1]
    latest_close = float(latest_row["close"])
    last_action = _action_to_scalar(actions.iloc[-1]["actions"]) if not actions.empty else 0.0
    predicted_close = _estimate_price(latest_close, last_action, env_kwargs["hmax"])
    delta = predicted_close - latest_close
    delta_pct = (delta / latest_close) * 100 if latest_close else 0.0
    history = [
        {"date": _to_datetime(row["date"]), "value": float(row["close"])}
        for _, row in raw_df.tail(240).iterrows()
    ]
    prediction_point = {
        "date": _to_datetime(latest_row["date"]) + timedelta(days=1),
        "predicted_close": predicted_close,
    }
    return PredictionResponse(
        symbol=symbol.upper(),
        latest_close=latest_close,
        predicted_next_close=predicted_close,
        delta=delta,
        delta_pct=delta_pct,
        generated_at=datetime.utcnow(),
        price_history=history,
        prediction_point=prediction_point,
        disclaimer=DISCLAIMER_TEXT,
    )


@router.post("/predict", response_model=PredictionResponse)
async def predict(payload: SymbolRequest) -> PredictionResponse:
    try:
        return await run_in_threadpool(_run_prediction, payload.symbol)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - safety net
        raise HTTPException(status_code=500, detail="Unexpected prediction failure") from exc


# Expose helper for tests
def run_prediction_for_symbol(symbol: str) -> PredictionResponse:
    """Synchronous helper for scripts/tests."""
    return _run_prediction(symbol)
