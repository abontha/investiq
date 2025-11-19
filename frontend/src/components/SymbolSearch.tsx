import { type FormEvent, useState } from 'react';
import { Search } from 'lucide-react';

interface SymbolSearchProps {
  defaultValue?: string;
  loading?: boolean;
  ctaLabel?: string;
  loadingLabel?: string;
  onSubmit: (symbol: string) => void;
}

export default function SymbolSearch({
  defaultValue = 'AAPL',
  loading,
  ctaLabel = 'Predict',
  loadingLabel = 'Loading…',
  onSubmit,
}: SymbolSearchProps) {
  const [value, setValue] = useState(defaultValue);

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (!value.trim()) return;
    onSubmit(value.trim().toUpperCase());
  };

  return (
    <form onSubmit={handleSubmit} className="glass-panel px-6 py-5 flex flex-col gap-3">
      <label className="text-xs uppercase tracking-[0.4em] text-white/50">Symbol</label>
      <div className="flex flex-col md:flex-row gap-3">
        <div className="flex-1 relative">
          <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-white/40" />
          <input
            value={value}
            onChange={(event) => setValue(event.target.value.toUpperCase())}
            placeholder="Search a stock (e.g. AAPL)"
            className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-12 pr-4 text-lg focus:outline-none focus:border-emerald-400/60 transition"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="md:w-40 inline-flex items-center justify-center bg-gradient-to-r from-emerald-500 to-cyan-500 text-night font-semibold rounded-xl py-3 shadow-glow transition-transform disabled:opacity-40"
        >
          {loading ? loadingLabel : ctaLabel}
        </button>
      </div>
    </form>
  );
}
