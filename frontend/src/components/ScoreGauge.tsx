interface ScoreGaugeProps {
  score: number;
  size?: number;
}

export function ScoreGauge({ score, size = 140 }: ScoreGaugeProps) {
  const strokeWidth = 10;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  const color = score >= 80 ? "var(--color-verdigris)" : score >= 50 ? "#C08A2E" : "var(--color-clay)";
  const label = score >= 80 ? "Strong" : score >= 50 ? "Needs work" : "Weak";

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="var(--color-line)"
            strokeWidth={strokeWidth}
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            style={{ transition: "stroke-dashoffset 0.6s ease-out" }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="font-display text-4xl font-semibold text-ink">{score}</span>
          <span className="font-mono text-[10px] uppercase tracking-wider text-ink-soft">/ 100</span>
        </div>
      </div>
      <span className="font-mono text-xs uppercase tracking-wider" style={{ color }}>
        {label}
      </span>
    </div>
  );
}
