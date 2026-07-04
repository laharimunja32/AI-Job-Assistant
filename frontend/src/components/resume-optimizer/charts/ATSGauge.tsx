interface ATSGaugeProps {
  score: number;
  label?: string;
  size?: 'sm' | 'md' | 'lg';
}

const sizeMap = {
  sm: { box: 'h-24 w-24 text-lg', stroke: 6 },
  md: { box: 'h-32 w-32 text-2xl', stroke: 8 },
  lg: { box: 'h-40 w-40 text-3xl', stroke: 10 },
};

export function ATSGauge({ score, label = 'ATS Score', size = 'md' }: ATSGaugeProps) {
  const clamped = Math.max(0, Math.min(100, score));
  const { box, stroke } = sizeMap[size];
  const radius = 45;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (clamped / 100) * circumference;
  const color = clamped >= 80 ? '#10b981' : clamped >= 60 ? '#f59e0b' : '#ef4444';

  return (
    <div className="flex flex-col items-center gap-2">
      <div className={`relative ${box} flex items-center justify-center`}>
        <svg className="absolute inset-0 -rotate-90" viewBox="0 0 100 100">
          <circle cx="50" cy="50" r={radius} fill="none" stroke="currentColor" strokeWidth={stroke} className="text-slate-200 dark:text-slate-700" />
          <circle
            cx="50"
            cy="50"
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={stroke}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
          />
        </svg>
        <span className="relative font-bold text-slate-900 dark:text-slate-100">{Math.round(clamped)}</span>
      </div>
      <span className="text-xs font-medium text-slate-500">{label}</span>
    </div>
  );
}
