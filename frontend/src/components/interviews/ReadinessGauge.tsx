interface ReadinessGaugeProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  label?: string;
}

const sizeMap = {
  sm: { box: 'h-14 w-14 text-sm', ring: 48 },
  md: { box: 'h-20 w-20 text-base', ring: 64 },
  lg: { box: 'h-28 w-28 text-xl', ring: 88 },
};

export function ReadinessGauge({ score, size = 'md', label = 'Readiness' }: ReadinessGaugeProps) {
  const clamped = Math.max(0, Math.min(100, score));
  const { box } = sizeMap[size];
  const color = clamped >= 80 ? 'text-emerald-600' : clamped >= 60 ? 'text-amber-600' : 'text-rose-600';

  return (
    <div className="flex flex-col items-center gap-1">
      <div
        className={`${box} flex items-center justify-center rounded-full border-4 border-slate-200 font-bold dark:border-slate-700 ${color}`}
      >
        {Math.round(clamped)}%
      </div>
      <span className="text-xs text-slate-500">{label}</span>
    </div>
  );
}
