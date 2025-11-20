"""
Utility script to train a PPO model for single-stock FinRL predictions.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from finrl.agents.stablebaselines3.models import DRLAgent
from finrl.config import INDICATORS
from finrl.meta.env_stock_trading.env_stocktrading import StockTradingEnv
from finrl.meta.preprocessor.preprocessors import FeatureEngineer
from stable_baselines3.common.vec_env import DummyVecEnv

from app.yfinance_client import download_price_history

MODEL_PATH = Path(__file__).resolve().parent / "ppo_model.zip"
LOOKBACK_DAYS = 365


def _fetch_data(symbol: str) -> pd.DataFrame:
    end = datetime.utcnow()
    start = end - timedelta(days=LOOKBACK_DAYS)
    data = download_price_history(symbol, start, end)
    if data.empty:
        raise RuntimeError(f"No Yahoo Finance data returned for {symbol}.")
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
    if frame.empty:
        raise RuntimeError(f"Unable to prepare training frame for {symbol}.")
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


def _build_env_kwargs(stock_dim: int) -> dict:
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


def train(symbol: str, timesteps: int, output: Path) -> None:
    print(f"[train_model] Fetching {symbol} data...")
    raw_df = _fetch_data(symbol)
    processed_df = _engineer_features(raw_df)
    env_kwargs = _build_env_kwargs(len(processed_df.tic.unique()))
    print("[train_model] Building environment and training PPO agent...")
    train_env = DummyVecEnv([lambda: StockTradingEnv(df=processed_df, **env_kwargs)])
    agent = DRLAgent(env=train_env)
    model = agent.get_model("ppo")
    trained_model = agent.train_model(
        model=model, tb_log_name=f"{symbol}_ppo", total_timesteps=timesteps
    )
    print(f"[train_model] Saving model to {output}")
    trained_model.save(str(output))


def main() -> None:
    parser = argparse.ArgumentParser(description="Train PPO model for FinRL predictions.")
    parser.add_argument("--symbol", default="AAPL", help="Ticker symbol (default: AAPL)")
    parser.add_argument(
        "--timesteps",
        type=int,
        default=10_000,
        help="Number of PPO timesteps (default: 10000)",
    )
    parser.add_argument(
        "--output",
        default=str(MODEL_PATH),
        help="Path to save the trained model (default: backend/ppo_model.zip)",
    )
    args = parser.parse_args()
    train(args.symbol.upper(), args.timesteps, Path(args.output))


if __name__ == "__main__":
    main()
