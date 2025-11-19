import type { LucideIcon } from 'lucide-react';
import { motion } from 'framer-motion';
import { clsx } from 'clsx';

interface MetricCardProps {
  label: string;
  value: string;
  delta?: string;
  icon?: LucideIcon;
  intent?: 'neutral' | 'positive' | 'negative';
  delay?: number;
}

export default function MetricCard({ label, value, delta, icon: Icon, intent = 'neutral', delay = 0 }: MetricCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
      className="glass-panel p-5 space-y-3"
    >
      <div className="flex items-center gap-3 text-sm uppercase tracking-[0.3em] text-white/60">
        {Icon && <Icon size={16} className="text-white/60" />}
        {label}
      </div>
      <div className="text-3xl font-semibold">{value}</div>
      {delta && (
        <div
          className={clsx('text-sm font-medium', {
            'text-emerald-400': intent === 'positive',
            'text-red-400': intent === 'negative',
            'text-white/60': intent === 'neutral',
          })}
        >
          {delta}
        </div>
      )}
    </motion.div>
  );
}
