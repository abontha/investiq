import { formatCurrency, formatDate } from '../lib/format';
import type { PriceComparisonRow } from '../types/api';

interface PriceComparisonTableProps {
  rows: PriceComparisonRow[];
}

export default function PriceComparisonTable({ rows }: PriceComparisonTableProps) {
  return (
    <div className="glass-panel overflow-hidden">
      <table className="w-full text-left text-sm">
        <thead className="uppercase tracking-[0.4em] text-white/40 text-xs">
          <tr>
            <th className="px-4 py-3">Date</th>
            <th className="px-4 py-3">Actual Close</th>
            <th className="px-4 py-3">Policy Signal</th>
          </tr>
        </thead>
        <tbody>
          {rows.slice(-10).map((row) => (
            <tr key={row.date} className="border-t border-white/5 text-white/80">
              <td className="px-4 py-3">{formatDate(row.date)}</td>
              <td className="px-4 py-3">{formatCurrency(row.actual_close)}</td>
              <td className="px-4 py-3 text-emerald-400">{formatCurrency(row.predicted_close)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
