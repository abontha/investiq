"""
Thin wrapper around FinRL that powers the FastAPI endpoints.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import yfinance as yf
from finrl.agents.stablebaselines3.models import DRLAgent, data_split
from finrl.config import INDICATORS
from finrl.meta.env_stock_trading.env_stocktrading import StockTradingEnv
from finrl.meta.preprocessor.preprocessors import FeatureEngineer
from stable_baselines3.common.base_class import BaseAlgorithm
from stable_baselines3.common.vec_env import DummyVecEnv

from .config import settings

DISCLAIMER_TEXT = (
    "Educational use only. These FinRL-driven simulations are NOT financial advice."
)


class FinRLException(RuntimeError):
    """Raised when the FinRL pipeline encounters a recoverable issue."""


@dataclass
class CacheEntry:
    prediction: Dict
    backtest: Dict
    expires_at: datetime


def _to_datetime(value: pd.Timestamp) -> datetime:
    """Convert pandas timestamps to naive UTC datetimes."""
    as_dt = value.to_pydatetime()
    if as_dt.tzinfo:
        as_dt = as_dt.astimezone(timezone.utc).replace(tzinfo=None)
    return as_dt


class FinRLService:
    """Coordinates training, inference, and result caching."""

    def __init__(self) -> None:
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.Lock()

    def get_prediction_payload(self, symbol: str) -> Dict:
        """Return only the prediction payload."""
        entry = self._get_or_train(symbol)
        return entry.prediction

    def get_backtest_payload(self, symbol: str) -> Dict:
        """Return only the backtest payload."""
        entry = self._get_or_train(symbol)
        return entry.backtest

    def _get_or_train(self, symbol: str) -> CacheEntry:
        normalized_symbol = symbol.upper()
        now = datetime.utcnow()
        with self._lock:
            entry = self._cache.get(normalized_symbol)
            if entry and entry.expires_at > now:
                return entry

        prediction, backtest = self._run_pipeline(normalized_symbol)
        expires = now + timedelta(minutes=settings.cache_ttl_minutes)
        new_entry = CacheEntry(
            prediction=prediction,
            backtest=backtest,
            expires_at=expires,
        )
        with self._lock:
            self._cache[normalized_symbol] = new_entry
        return new_entry

    def _run_pipeline(self, symbol: str) -> Tuple[Dict, Dict]:
        raw_df = self._download_market_data(symbol)
        processed_df = self._engineer_features(raw_df)
        train_df, test_df = self._split_dataframes(processed_df)
        env_kwargs = self._build_env_kwargs(train_df)
        trained_model = self._train_agent(train_df, env_kwargs)
        account_memory, actions_memory = self._run_trading_loop(
            trained_model, test_df, env_kwargs
        )

        prediction_payload = self._build_prediction_payload(
            symbol=symbol,
            raw_df=raw_df,
            actions=actions_memory,
            env_kwargs=env_kwargs,
        )
        backtest_payload = self._build_backtest_payload(
            symbol=symbol,
            account_memory=account_memory,
            actions=actions_memory,
            test_df=test_df,
            env_kwargs=env_kwargs,
        )
        return prediction_payload, backtest_payload

    def _download_market_data(self, symbol: str) -> pd.DataFrame:
        end = datetime.utcnow()
        start = end - timedelta(days=365 * settings.lookback_years)
        data = yf.download(
            symbol,
            start=start,
            end=end,
            auto_adjust=False,
            progress=False,
        )
        if data.empty:
            raise FinRLException(
                f"No Yahoo Finance data returned for {symbol}. Check the ticker symbol."
            )
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [str(levels[0]) for levels in data.columns]
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
        if frame.empty or len(frame) < 100:
            raise FinRLException(
                f"Insufficient historical data for {symbol}. Try expanding the window."
            )
        return frame

    def _engineer_features(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        fe = FeatureEngineer(
            use_technical_indicator=True,
            tech_indicator_list=INDICATORS,
            use_turbulence=False,
            user_defined_feature=False,
        )
        processed = fe.preprocess_data(raw_df)
        processed = processed.ffill().dropna()
        return processed

    def _split_dataframes(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        last_date = df["date"].max()
        split_date = last_date - timedelta(days=settings.test_window_days)
        if split_date <= df["date"].min():
            raise FinRLException(
                "Not enough rows to create training and testing windows. "
                "Reduce FINRL_TEST_WINDOW_DAYS or extend lookback."
            )
        train = data_split(df, start=df["date"].min(), end=split_date)
        test = data_split(df, start=split_date, end=last_date)
        if train.empty or test.empty:
            raise FinRLException("Empty training or testing dataset produced.")
        return train, test

    def _build_env_kwargs(self, train_df: pd.DataFrame) -> Dict:
        stock_dim = len(train_df.tic.unique())
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

    def _train_agent(self, train_df: pd.DataFrame, env_kwargs: Dict) -> BaseAlgorithm:
        train_env = DummyVecEnv([lambda: StockTradingEnv(df=train_df, **env_kwargs)])
        agent = DRLAgent(env=train_env)
        model = agent.get_model("ppo")
        trained_model = agent.train_model(
            model=model,
            tb_log_name="ppo",
            total_timesteps=settings.training_timesteps,
        )
        return trained_model

    def _run_trading_loop(
        self,
        model,
        test_df: pd.DataFrame,
        env_kwargs: Dict,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        trade_env = StockTradingEnv(df=test_df, **env_kwargs)
        account_memory, actions_memory = DRLAgent.DRL_prediction(
            model=model, environment=trade_env
        )
        return account_memory, actions_memory

    def _build_prediction_payload(
        self,
        symbol: str,
        raw_df: pd.DataFrame,
        actions: pd.DataFrame,
        env_kwargs: Dict,
    ) -> Dict:
        latest_row = raw_df.iloc[-1]
        latest_close = float(latest_row["close"])
        history = [
            {
                "date": _to_datetime(row["date"]),
                "value": float(row["close"]),
            }
            for _, row in raw_df.tail(240).iterrows()
        ]
        last_action = self._extract_action(actions, -1)
        predicted_next_close = self._estimate_price_from_action(
            latest_close, last_action, env_kwargs["hmax"]
        )
        next_date = _to_datetime(latest_row["date"]) + timedelta(days=1)

        return {
            "symbol": symbol,
            "latest_close": latest_close,
            "predicted_next_close": predicted_next_close,
            "generated_at": datetime.utcnow(),
            "price_history": history,
            "prediction_point": {
                "date": next_date,
                "predicted_close": predicted_next_close,
            },
            "disclaimer": DISCLAIMER_TEXT,
        }

    def _build_backtest_payload(
        self,
        symbol: str,
        account_memory: pd.DataFrame,
        actions: pd.DataFrame,
        test_df: pd.DataFrame,
        env_kwargs: Dict,
    ) -> Dict:
        equity_curve = [
            {
                "date": _to_datetime(row["date"]),
                "equity": float(row["account_value"]),
            }
            for _, row in account_memory.iterrows()
        ]
        metrics = self._calculate_metrics(account_memory)
        price_rows = self._build_price_comparison(actions, test_df, env_kwargs["hmax"])
        return {
            "symbol": symbol,
            "generated_at": datetime.utcnow(),
            "equity_curve": equity_curve,
            "price_comparison": price_rows,
            "metrics": metrics,
            "disclaimer": DISCLAIMER_TEXT,
        }

    def _calculate_metrics(self, account_memory: pd.DataFrame) -> Dict:
        series = account_memory["account_value"].astype(float)
        final_equity = float(series.iloc[-1])
        total_return = (final_equity / float(series.iloc[0]) - 1) * 100
        returns = series.pct_change().dropna()
        sharpe = 0.0
        if not returns.empty and returns.std() > 0:
            sharpe = (returns.mean() / returns.std()) * np.sqrt(252)
        rolling_max = series.cummax()
        drawdowns = (series - rolling_max) / rolling_max
        max_drawdown = float(drawdowns.min() * 100 if not drawdowns.empty else 0.0)
        return {
            "final_equity": round(final_equity, 2),
            "total_return_pct": round(total_return, 2),
            "sharpe_ratio": round(float(sharpe), 3),
            "max_drawdown_pct": round(max_drawdown, 2),
        }

    def _build_price_comparison(
        self, actions: pd.DataFrame, test_df: pd.DataFrame, hmax: int
    ) -> List[Dict]:
        closes = (
            test_df[["date", "close"]]
            .groupby("date")
            .mean()
            .reset_index()
            .sort_values("date")
        )
        if closes.empty:
            return []
        action_frame = actions.copy()
        if not action_frame.empty:
            action_frame["date"] = pd.to_datetime(action_frame["date"])
            action_frame["signal"] = np.tanh(
                action_frame["actions"].apply(self._action_to_scalar) / hmax
            )
        else:
            action_frame = pd.DataFrame(columns=["date", "signal"])
        merged = closes.merge(
            action_frame[["date", "signal"]],
            on="date",
            how="left",
        ).sort_values("date")
        merged["signal"] = merged["signal"].ffill().fillna(0.0)
        merged["predicted_close"] = merged["close"].shift(1).fillna(merged["close"])
        merged["predicted_close"] = merged["predicted_close"] * (
            1 + merged["signal"] * 0.01
        )
        rows = []
        for _, row in merged.iterrows():
            rows.append(
                {
                    "date": _to_datetime(pd.to_datetime(row["date"])),
                    "actual_close": float(row["close"]),
                    "predicted_close": float(row["predicted_close"]),
                }
            )
        return rows

    def _estimate_price_from_action(
        self, reference_close: float, action: float, hmax: int
    ) -> float:
        if action is None:
            return reference_close
        signal = np.tanh(action / hmax)
        return round(reference_close * (1 + signal * 0.01), 4)

    def _extract_action(self, actions: pd.DataFrame, position: int) -> float | None:
        if actions.empty:
            return None
        row = actions.iloc[position]
        return self._action_to_scalar(row["actions"])

    @staticmethod
    def _action_to_scalar(action_value) -> float:
        if isinstance(action_value, (list, tuple, np.ndarray)):
            return float(action_value[0]) if action_value else 0.0
        return float(action_value)
