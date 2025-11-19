import type { BacktestResponse, PredictionResponse } from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

async function postJson<T>(path: string, payload: Record<string, unknown>): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let detail = 'Unable to reach FinRL backend';
    try {
      const data = await response.json();
      detail = data.detail ?? JSON.stringify(data);
    } catch (error) {
      // ignore JSON parse errors
    }
    throw new Error(detail);
  }

  return response.json();
}

export const requestPrediction = (symbol: string): Promise<PredictionResponse> =>
  postJson('/api/predict', { symbol: symbol.toUpperCase() });

export const requestBacktest = (symbol: string): Promise<BacktestResponse> =>
  postJson('/api/backtest', { symbol: symbol.toUpperCase() });
