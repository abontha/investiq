interface DisclaimerProps {
  subtle?: boolean;
}

export default function Disclaimer({ subtle }: DisclaimerProps) {
  return (
    <div
      className={`rounded-2xl border px-5 py-4 text-sm leading-relaxed ${
        subtle ? 'border-white/10 bg-white/5 text-white/60' : 'border-emerald-500/30 bg-[#0c131f] text-white/80'
      }`}
    >
      Educational use only — not investment advice. FinRL outputs illustrate research workflows and should not drive live trades.
    </div>
  );
}
