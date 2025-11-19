# InvestIQ – FinRL Stock Prediction Platform

This project delivers a professional-grade reference implementation for a two-page stock analytics experience:

1. **Predictions page** – FinRL-powered next-day price projection with TradingView-style visuals.
2. **Backtesting page** – Equity curve, risk KPIs, and actual vs policy-implied pricing.

The stack pairs a FastAPI backend (FinRL + Stable-Baselines3 + yfinance) with a React/Vite/Tailwind frontend using TradingView Lightweight Charts.  
**All outputs are educational only and are _not_ financial advice.**

---

## Backend (FastAPI + FinRL)

### Prerequisites
- Python 3.9+
- Recommended: a virtual environment (`python3 -m venv .venv && source .venv/bin/activate`)

### Install
```bash
cd backend
pip install -r requirements.txt
python3 train_model.py          # builds backend/ppo_model.zip (default AAPL)
uvicorn app.main:app --reload --port 8000
```

FinRL’s import path eagerly loads optional data processors, so the requirements file includes the extra adapters (`wrds`, `alpaca-trade-api`, `exchange-calendars`, etc.) needed to avoid runtime import errors. Rerun `python3 train_model.py --symbol MSFT --timesteps 20000` anytime you want to refresh the PPO weights.

### Key Endpoints
| Method | Path | Description |
| ------ | ---- | ----------- |
| `GET` | `/health` | Simple readiness probe |
| `POST` | `/api/predict` | Body: `{"symbol":"AAPL"}`. Loads `ppo_model.zip`, runs PPO inference on the latest market state, and returns latest close, predicted next close, deltas, chart-ready history, and disclaimer. |
| `POST` | `/api/backtest` | Body identical to `/api/predict`. Responds with equity curve data, Sharpe/max drawdown metrics, and actual vs policy-implied closes. |

Both endpoints cache the most recent run per ticker (default TTL: 60 minutes; tune with `FINRL_CACHE_TTL_MINUTES`). Other tunables:

| Env Var | Default | Purpose |
| ------- | ------- | ------- |
| `FINRL_LOOKBACK_YEARS` | `2` | Historical window sent to yfinance |
| `FINRL_TEST_WINDOW_DAYS` | `60` | Size of holdout window for FinRL backtests |
| `FINRL_TRAINING_TIMESTEPS` | `10000` | PPO timesteps per retrain (used by the backtest caching layer) |
| `FINRL_CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Comma-separated list for the frontend |

`routers/predict.py` handles inference via the saved PPO model, while `finrl_integration.py` encapsulates the backtesting loop (train-test-trade, caching, and metrics).

---

## Frontend (React + Vite + Tailwind)

### Install & Run
```bash
cd frontend
npm install
npm run dev
```

Set `VITE_API_BASE_URL` in a `.env` file (defaults to `http://localhost:8000`). The React app features:
- Dark premium aesthetic with sidebar navigation and smooth route transitions (Framer Motion)
- Shared symbol search component driving Prediction + Backtesting workflows
- TradingView-style line charts powered by `lightweight-charts`
- KPI cards, animated loaders, graceful error banners, timeframe toggle, and persistent disclaimers

---

## Disclaimers
This repository, its maintainers, and any associated institutions **do not provide investment advice**. The models and metrics are purely educational simulations built on historical data. Always consult a licensed professional before making financial decisions.
