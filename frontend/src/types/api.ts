export interface PricePoint {
  date: string;
  value: number;
}

export interface PredictionPoint {
  date: string;
  predicted_close: number;
}

export interface PredictionResponse {
  symbol: string;
  latest_close: number;
  predicted_next_close: number;
  generated_at: string;
  price_history: PricePoint[];
  prediction_point: PredictionPoint;
  disclaimer: string;
}

export interface EquityPoint {
  date: string;
  equity: number;
}

export interface PriceComparisonRow {
  date: string;
  actual_close: number;
  predicted_close: number;
}

export interface BacktestMetrics {
  final_equity: number;
  total_return_pct: number;
  sharpe_ratio: number;
  max_drawdown_pct: number;
}

export interface BacktestResponse {
  symbol: string;
  generated_at: string;
  equity_curve: EquityPoint[];
  price_comparison: PriceComparisonRow[];
  metrics: BacktestMetrics;
  disclaimer: string;
}
