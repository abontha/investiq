import { useEffect, useMemo, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Activity, ArrowDown, ArrowUp, LineChart as LineChartIcon, Shield } from 'lucide-react';
import SymbolSearch from '../components/SymbolSearch';
import MetricCard from '../components/MetricCard';
import LineChart from '../components/LineChart';
import Loader from '../components/Loader';
import ErrorBanner from '../components/ErrorBanner';
import Disclaimer from '../components/Disclaimer';
import PriceComparisonTable from '../components/PriceComparisonTable';
import TimeframeToggle, { type TimeframeOption } from '../components/TimeframeToggle';
import { formatCurrency, formatPercent } from '../lib/format';
import { requestBacktest } from '../lib/api';
import type { BacktestResponse } from '../types/api';

const defaultSymbol = 'AAPL';

const timeframeToDays: Record<TimeframeOption, number> = {
  '1Y': 365,
  '3Y': 365 * 3,
  '5Y': 365 * 5,
};

export default function BacktestingPage() {
  const [activeSymbol, setActiveSymbol] = useState(defaultSymbol);
  const [timeframe, setTimeframe] = useState<TimeframeOption>('1Y');
  const { mutate, data, isPending, error, isError } = useMutation({
    mutationFn: (symbol: string) => requestBacktest(symbol),
  });

  useEffect(() => {
    mutate(defaultSymbol);
  }, [mutate]);

  const payload = data as BacktestResponse | undefined;

  const filteredEquity = useMemo(() => {
    if (!payload) return [];
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - timeframeToDays[timeframe]);
    return payload.equity_curve
      .filter((point) => new Date(point.date) >= cutoff)
      .map((point) => ({
        time: point.date.split('T')[0],
        value: point.equity,
      }));
  }, [payload, timeframe]);

  const comparisonRows = useMemo(() => {
    if (!payload) return [];
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - timeframeToDays[timeframe]);
    return payload.price_comparison.filter((row) => new Date(row.date) >= cutoff);
  }, [payload, timeframe]);

  const handleSymbolSubmit = (symbol: string) => {
    setActiveSymbol(symbol);
    mutate(symbol);
  };

  return (
    <div className="space-y-8">
      <header className="space-y-2">
        <p className="text-sm uppercase tracking-[0.5em] text-white/50">Backtesting</p>
        <div className="flex flex-col lg:flex-row lg:items-end gap-4">
          <div>
            <h1 className="text-4xl font-semibold">Strategy Backtesting</h1>
            <p className="text-white/70 max-w-2xl">
              Replay FinRL policy behavior on the holdout window to inspect capital curve, edge metrics, and prediction drift against realized closes.
            </p>
          </div>
        </div>
      </header>

      <SymbolSearch defaultValue={defaultSymbol} ctaLabel="Backtest" loadingLabel="Running…" loading={isPending} onSubmit={handleSymbolSubmit} />

      {isError && <ErrorBanner message={(error as Error).message} />}
      {isPending && !payload && <Loader />}

      {payload && (
        <div className="space-y-6">
          <div className="grid gap-6 lg:grid-cols-4">
            <MetricCard label="Final Equity" value={formatCurrency(payload.metrics.final_equity)} icon={LineChartIcon} />
            <MetricCard
              label="Total Return"
              value={formatPercent(payload.metrics.total_return_pct)}
              intent={payload.metrics.total_return_pct >= 0 ? 'positive' : 'negative'}
              icon={payload.metrics.total_return_pct >= 0 ? ArrowUp : ArrowDown}
            />
            <MetricCard label="Sharpe Ratio" value={payload.metrics.sharpe_ratio.toFixed(2)} icon={Activity} />
            <MetricCard
              label="Max Drawdown"
              value={formatPercent(payload.metrics.max_drawdown_pct)}
              intent="negative"
              icon={Shield}
            />
          </div>

          <div className="glass-panel p-6 space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.4em] text-white/50">Equity Curve</p>
                <p className="text-2xl font-semibold">{activeSymbol} · Reinforcement Policy</p>
              </div>
              <TimeframeToggle value={timeframe} onChange={setTimeframe} />
            </div>
            <LineChart data={filteredEquity} height={360} gradientFrom="rgba(30,167,255,0.8)" gradientTo="rgba(30,167,255,0.1)" />
          </div>

          <div className="grid lg:grid-cols-2 gap-6">
            <div className="space-y-3">
              <p className="text-xs uppercase tracking-[0.4em] text-white/50">Prediction Drift</p>
              <PriceComparisonTable rows={comparisonRows} />
            </div>
            <div className="space-y-3">
              <p className="text-xs uppercase tracking-[0.4em] text-white/50">Narrative</p>
              <div className="glass-panel p-5 text-white/70 text-sm leading-relaxed">
                Policy views suggest equity settling at {formatCurrency(payload.metrics.final_equity)} with drawdown tolerance around
                {` ${formatPercent(payload.metrics.max_drawdown_pct)}`} relative to initial equity. Sharpe ratio of {payload.metrics.sharpe_ratio.toFixed(2)} indicates
                {(payload.metrics.sharpe_ratio > 1 ? ' a respectable risk-adjusted profile.' : ' room for further optimization.')} Use these signals for exploration only.
              </div>
            </div>
          </div>
        </div>
      )}

      <Disclaimer subtle />
    </div>
  );
}
