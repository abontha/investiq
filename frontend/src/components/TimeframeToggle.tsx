const options = ['1Y', '3Y', '5Y'] as const;

export type TimeframeOption = (typeof options)[number];

interface TimeframeToggleProps {
  value: TimeframeOption;
  onChange: (value: TimeframeOption) => void;
}

export default function TimeframeToggle({ value, onChange }: TimeframeToggleProps) {
  return (
    <div className="inline-flex rounded-full bg-white/5 p-1 border border-white/10">
      {options.map((option) => (
        <button
          key={option}
          onClick={() => onChange(option)}
          className={`px-4 py-1.5 text-sm rounded-full transition ${
            value === option ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-night font-semibold' : 'text-white/60'
          }`}
        >
          {option}
        </button>
      ))}
    </div>
  );
}
