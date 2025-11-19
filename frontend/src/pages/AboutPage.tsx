import { Shield, Sparkles, Target } from 'lucide-react';
import Disclaimer from '../components/Disclaimer';

export default function AboutPage() {
  const pillars = [
    {
      icon: Shield,
      title: 'Risk First',
      text: 'Metrics like Sharpe, drawdowns, and capital efficiency are surfaced first to ground every projection in risk-aware context.',
    },
    {
      icon: Target,
      title: 'Precision',
      text: 'FinRL PPO agents retrain over curated Yahoo Finance data to provide reproducible forecasts and cached experiences.',
    },
    {
      icon: Sparkles,
      title: 'Presentation',
      text: 'TradingView-inspired visuals, neon depth, and cinematic motion create an investor-ready narrative layer.',
    },
  ];

  return (
    <div className="space-y-8">
      <header className="space-y-2">
        <p className="text-sm uppercase tracking-[0.4em] text-white/60">About</p>
        <h1 className="text-4xl font-semibold">FinRL Alpha Studio</h1>
        <p className="text-white/70 max-w-3xl">
          Built on FastAPI + FinRL, this experience turns reinforcement-learning research into a premium, two-panel analytics cockpit. Every
          interaction remains educational—no execution, no brokerage integrations, just insights and storytelling.
        </p>
      </header>

      <div className="grid gap-6 lg:grid-cols-3">
        {pillars.map((pillar) => (
          <div key={pillar.title} className="glass-panel p-6 space-y-4">
            <pillar.icon className="text-emerald-400" />
            <h3 className="text-xl font-semibold">{pillar.title}</h3>
            <p className="text-white/70 text-sm">{pillar.text}</p>
          </div>
        ))}
      </div>

      <Disclaimer subtle />
    </div>
  );
}
