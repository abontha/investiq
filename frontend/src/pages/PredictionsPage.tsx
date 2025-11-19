import { useEffect, useMemo, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { ArrowDownRight, ArrowUpRight, Clock } from 'lucide-react';
import { formatCurrency, formatPercent } from '../lib/format';
import { requestPrediction } from '../lib/api';
import type { PredictionResponse } from '../types/api';
import SymbolSearch from '../components/SymbolSearch';
import MetricCard from '../components/MetricCard';
import LineChart from '../components/LineChart';
import Loader from '../components/Loader';
import ErrorBanner from '../components/ErrorBanner';
import Disclaimer from '../components/Disclaimer';

const defaultSymbol = 'AAPL';

export default function PredictionsPage() {
  const [activeSymbol, setActiveSymbol] = useState(defaultSymbol);
  const {
    mutate,
    data,
    isPending,
    error,
    isError,
  } = useMutation({
    mutationFn: (symbol: string) => requestPrediction(symbol),
  });

  useEffect(() => {
    mutate(defaultSymbol);
  }, [mutate]);

  const handleSymbolSubmit = (symbol: string) => {
    setActiveSymbol(symbol);
    mutate(symbol);
  };

  const payload = data as PredictionResponse | undefined;

  const chartData = useMemo(() => {
    if (!payload) return [];
    return payload.price_history.slice(-240).map((point) => ({
      time: point.date.split('T')[0],
      value: point.value,
    }));
  }, [payload]);

  const predictionMarker = useMemo(() => {
    if (!payload) return undefined;
    return [
      {
        time: payload.prediction_point.date.split('T')[0],
        position: 'aboveBar' as const,
        color: payload.predicted_next_close >= payload.latest_close ? '#14F195' : '#F87171',
        shape: 'circle' as const,
        text: 'Next',
      },
    ];
  }, [payload]);

  const delta = payload ? payload.predicted_next_close - payload.latest_close : 0;
  const intent = delta >= 0 ? 'positive' : 'negative';

  return (
    <div className="space-y-8">
      <header className="space-y-2">
        <p className="text-sm uppercase tracking-[0.5em] text-white/50">Predictions</p>
        <div className="flex flex-col lg:flex-row lg:items-end gap-4">
          <div>
            <h1 className="text-4xl font-semibold">Price Prediction</h1>
            <p className="text-white/70 max-w-2xl">
              FinRL PPO agents forecast the next session close after retraining on fresh Yahoo Finance data. Visuals update with smooth transitions for a premium research moment.
            </p>
          </div>
          {payload && (
            <div className="glass-panel px-4 py-3 text-sm text-white/70 flex items-center gap-2">
              <Clock size={16} className="text-emerald-400" />
              Updated {new Date(payload.generated_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </div>
          )}
        </div>
      </header>

      <SymbolSearch defaultValue={defaultSymbol} loading={isPending} loadingLabel="Predicting…" onSubmit={handleSymbolSubmit} />

      {isError && <ErrorBanner message={(error as Error).message} />}

      {isPending && !payload && <Loader />}

      {payload && (
        <div className="space-y-6">
          <div className="grid gap-6 lg:grid-cols-2">
            <MetricCard
              label={`Latest Close · ${activeSymbol}`}
              value={formatCurrency(payload.latest_close)}
              intent="neutral"
              icon={ArrowDownRight}
            />
            <MetricCard
              label="Next-Day Prediction"
              value={formatCurrency(payload.predicted_next_close)}
              delta={`${formatCurrency(delta)} (${formatPercent((delta / payload.latest_close) * 100)})`}
              intent={intent}
              icon={intent === 'positive' ? ArrowUpRight : ArrowDownRight}
              delay={0.1}
            />
          </div>

          <div className="glass-panel p-6 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.4em] text-white/50">Price Action</p>
                <p className="text-2xl font-semibold">{activeSymbol} · Last {Math.min(chartData.length, 240)} sessions</p>
              </div>
              <div className="text-sm text-white/60">Prediction marker indicates next session close</div>
            </div>
            <LineChart data={chartData} markers={predictionMarker} height={360} />
          </div>
        </div>
      )}

      <Disclaimer subtle />
    </div>
  );
}
